"""
Device Profiler - Detects and adapts to different Android devices
Handles fragmentation: different manufacturers, Android versions, screen sizes
"""

import subprocess
import logging
import json
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceProfile:
    """Complete device profile"""
    manufacturer: str
    model: str
    android_version: str
    api_level: int
    screen_width: int
    screen_height: int
    dpi: int
    is_rooted: bool
    termux_version: str
    available_features: list
    limitations: list


class DeviceProfiler:
    """
    Profiles the Android device and adapts behavior accordingly
    Critical for universal compatibility across different phones
    """
    
    def __init__(self):
        self.profile: Optional[DeviceProfile] = None
        self._profile_device()
    
    def _profile_device(self):
        """Build complete device profile"""
        logger.info("🔍 Profiling device...")
        
        # Get basic device info
        manufacturer = self._get_prop("ro.product.manufacturer", "Unknown")
        model = self._get_prop("ro.product.model", "Unknown")
        android_version = self._get_prop("ro.build.version.release", "Unknown")
        api_level = int(self._get_prop("ro.build.version.sdk", "0"))
        
        # Get screen info
        width, height, dpi = self._get_screen_info()
        
        # Check if rooted
        is_rooted = self._check_root()
        
        # Get Termux version
        termux_version = self._get_termux_version()
        
        # Detect available features
        features = self._detect_features()
        
        # Detect limitations
        limitations = self._detect_limitations(api_level, manufacturer)
        
        self.profile = DeviceProfile(
            manufacturer=manufacturer,
            model=model,
            android_version=android_version,
            api_level=api_level,
            screen_width=width,
            screen_height=height,
            dpi=dpi,
            is_rooted=is_rooted,
            termux_version=termux_version,
            available_features=features,
            limitations=limitations
        )
        
        self._log_profile()
    
    def _get_prop(self, prop: str, default: str = "") -> str:
        """Get Android property"""
        try:
            result = subprocess.run(
                ['getprop', prop],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or default
        except:
            return default
    
    def _get_screen_info(self) -> Tuple[int, int, int]:
        """Get screen dimensions and DPI"""
        width, height, dpi = 1080, 2400, 400  # Defaults
        
        try:
            # Try wm size
            result = subprocess.run(
                ['wm', 'size'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse: "Physical size: 1080x2400"
                match = re.search(r'(\d+)x(\d+)', result.stdout)
                if match:
                    width = int(match.group(1))
                    height = int(match.group(2))
            
            # Try wm density
            result = subprocess.run(
                ['wm', 'density'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse: "Physical density: 400"
                match = re.search(r'(\d+)', result.stdout)
                if match:
                    dpi = int(match.group(1))
                    
        except Exception as e:
            logger.warning(f"Could not get screen info: {e}")
        
        return width, height, dpi
    
    def _check_root(self) -> bool:
        """Check if device is rooted"""
        try:
            result = subprocess.run(
                ['su', '-c', 'id'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_termux_version(self) -> str:
        """Get Termux version"""
        try:
            result = subprocess.run(
                ['termux-info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'version' in line.lower():
                        return line.split(':')[-1].strip()
        except:
            pass
        return "Unknown"
    
    def _detect_features(self) -> list:
        """Detect available features on this device"""
        features = []
        
        # Check Termux API
        if self._check_command('termux-telephony-call'):
            features.append('telephony')
        
        if self._check_command('termux-sms-send'):
            features.append('sms')
        
        if self._check_command('termux-notification'):
            features.append('notifications')
        
        if self._check_command('termux-camera-photo'):
            features.append('camera')
        
        if self._check_command('termux-tts-speak'):
            features.append('tts')
        
        if self._check_command('termux-dialog'):
            features.append('dialogs')
        
        # Check if we can use input command (screen control)
        if self._check_command('input'):
            features.append('screen_control')
        
        # Check accessibility services
        if self._check_accessibility():
            features.append('accessibility')
        
        return features
    
    def _check_command(self, cmd: str) -> bool:
        """Check if command is available"""
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_accessibility(self) -> bool:
        """Check if accessibility service is available"""
        try:
            result = subprocess.run(
                ['settings', 'get', 'secure', 'enabled_accessibility_services'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return 'termux' in result.stdout.lower()
        except:
            return False
    
    def _detect_limitations(self, api_level: int, manufacturer: str) -> list:
        """Detect device-specific limitations"""
        limitations = []
        
        # API level limitations
        if api_level < 23:  # Android 6.0
            limitations.append('old_android')
            limitations.append('no_direct_boot')
        
        if api_level < 26:  # Android 8.0
            limitations.append('limited_background')
        
        # Manufacturer-specific issues
        manufacturer_lower = manufacturer.lower()
        
        if 'samsung' in manufacturer_lower:
            limitations.append('samsung_battery_opt')  # Aggressive battery optimization
        
        if 'xiaomi' in manufacturer_lower or 'redmi' in manufacturer_lower:
            limitations.append('xiaomi_miui_restrictions')
            limitations.append('xiaomi_autostart_disabled')
        
        if 'huawei' in manufacturer_lower:
            limitations.append('huawei_power_genie')
            limitations.append('huawei_app_launch')
        
        if 'oppo' in manufacturer_lower or 'vivo' in manufacturer_lower:
            limitations.append('coloros_restrictions')
        
        if 'oneplus' in manufacturer_lower:
            limitations.append('oneplus_battery_opt')
        
        # Check Termux API availability
        if not self._check_command('termux-api-start'):
            limitations.append('no_termux_api')
        
        return limitations
    
    def _log_profile(self):
        """Log device profile"""
        p = self.profile
        logger.info("=" * 60)
        logger.info("📱 DEVICE PROFILE")
        logger.info("=" * 60)
        logger.info(f"Manufacturer: {p.manufacturer}")
        logger.info(f"Model: {p.model}")
        logger.info(f"Android: {p.android_version} (API {p.api_level})")
        logger.info(f"Screen: {p.screen_width}x{p.screen_height} ({p.dpi} DPI)")
        logger.info(f"Rooted: {'Yes' if p.is_rooted else 'No'}")
        logger.info(f"Termux: {p.termux_version}")
        logger.info(f"Features: {', '.join(p.available_features)}")
        if p.limitations:
            logger.info(f"Limitations: {', '.join(p.limitations)}")
        logger.info("=" * 60)
    
    def get_screen_coordinates(self, relative_x: float, relative_y: float) -> Tuple[int, int]:
        """
        Convert relative coordinates (0.0-1.0) to absolute pixel coordinates
        Adapts to different screen sizes
        """
        if not self.profile:
            return (0, 0)
        
        x = int(relative_x * self.profile.screen_width)
        y = int(relative_y * self.profile.screen_height)
        return (x, y)
    
    def get_ui_element_coordinates(self, element_name: str) -> Optional[Tuple[int, int]]:
        """
        Get coordinates for common UI elements
        Adapts to different manufacturers and screen sizes
        """
        if not self.profile:
            return None
        
        # Relative coordinates (0.0-1.0) for common elements
        # These adapt to screen size automatically
        elements = {
            # WhatsApp
            'whatsapp_search': (0.88, 0.08),  # Top right
            'whatsapp_message_box': (0.5, 0.92),  # Bottom center
            'whatsapp_send_button': (0.92, 0.92),  # Bottom right
            
            # Phone app
            'phone_dialpad': (0.5, 0.7),  # Center-bottom
            'phone_call_button': (0.5, 0.85),  # Bottom center
            
            # General
            'home_button': (0.5, 0.96),  # Bottom center
            'back_button': (0.12, 0.96),  # Bottom left
            'recent_apps': (0.88, 0.96),  # Bottom right
            'status_bar': (0.5, 0.02),  # Top
        }
        
        if element_name in elements:
            return self.get_screen_coordinates(*elements[element_name])
        
        return None
    
    def has_feature(self, feature: str) -> bool:
        """Check if device has specific feature"""
        if not self.profile:
            return False
        return feature in self.profile.available_features
    
    def has_limitation(self, limitation: str) -> bool:
        """Check if device has specific limitation"""
        if not self.profile:
            return False
        return limitation in self.profile.limitations
    
    def get_profile_dict(self) -> dict:
        """Get profile as dictionary"""
        if not self.profile:
            return {}
        
        return {
            'manufacturer': self.profile.manufacturer,
            'model': self.profile.model,
            'android_version': self.profile.android_version,
            'api_level': self.profile.api_level,
            'screen': {
                'width': self.profile.screen_width,
                'height': self.profile.screen_height,
                'dpi': self.profile.dpi
            },
            'is_rooted': self.profile.is_rooted,
            'features': self.profile.available_features,
            'limitations': self.profile.limitations
        }


class AdaptiveUIController:
    """
    UI controller that adapts to different devices
    Uses DeviceProfiler to adjust coordinates and behaviors
    """
    
    def __init__(self, profiler: DeviceProfiler):
        self.profiler = profiler
        self.profile = profiler.profile
    
    def tap_element(self, element_name: str) -> bool:
        """Tap a UI element by name (adapts to device)"""
        coords = self.profiler.get_ui_element_coordinates(element_name)
        
        if not coords:
            logger.error(f"Unknown element: {element_name}")
            return False
        
        x, y = coords
        logger.info(f"Tapping {element_name} at ({x}, {y})")
        
        try:
            result = subprocess.run(
                ['input', 'tap', str(x), str(y)],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Tap failed: {e}")
            return False
    
    def swipe_gesture(self, start_element: str, end_element: str, duration: int = 300) -> bool:
        """Swipe from one element to another"""
        start_coords = self.profiler.get_ui_element_coordinates(start_element)
        end_coords = self.profiler.get_ui_element_coordinates(end_element)
        
        if not start_coords or not end_coords:
            return False
        
        try:
            result = subprocess.run(
                ['input', 'swipe',
                 str(start_coords[0]), str(start_coords[1]),
                 str(end_coords[0]), str(end_coords[1]),
                 str(duration)],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            return False
    
    def navigate_back(self) -> bool:
        """Navigate back - works on all devices"""
        try:
            result = subprocess.run(
                ['input', 'keyevent', 'KEYCODE_BACK'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Back navigation failed: {e}")
            return False
    
    def go_home(self) -> bool:
        """Go to home screen"""
        try:
            result = subprocess.run(
                ['input', 'keyevent', 'KEYCODE_HOME'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Home navigation failed: {e}")
            return False
