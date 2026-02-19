"""
Android Controller - Controls the Android device
Makes AURA actually perform actions on apps, screen, calls, messages
"""

import subprocess
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    success: bool
    action: str
    output: str
    error: Optional[str] = None


class AndroidController:
    """
    Controls Android device via Termux API and ADB
    Enables AURA to actually DO things: tap, swipe, type, open apps
    """
    
    def __init__(self):
        self.screen_width = 1080
        self.screen_height = 2400
        self._get_screen_size()
        
    def _get_screen_size(self):
        """Get device screen dimensions"""
        try:
            # Get screen size
            result = subprocess.run(
                ['termux-display-size'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse output like "1080x2400"
                size = result.stdout.strip().split('x')
                if len(size) == 2:
                    self.screen_width = int(size[0])
                    self.screen_height = int(size[1])
                    logger.info(f"Screen size: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            logger.warning(f"Could not get screen size: {e}")
    
    def tap(self, x: int, y: int) -> ActionResult:
        """Tap at screen coordinates"""
        try:
            result = subprocess.run(
                ['input', 'tap', str(x), str(y)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ActionResult(True, "tap", f"Tapped at ({x}, {y})")
            else:
                return ActionResult(False, "tap", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "tap", "", str(e))
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> ActionResult:
        """Swipe from (x1,y1) to (x2,y2)"""
        try:
            result = subprocess.run(
                ['input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ActionResult(True, "swipe", f"Swiped from ({x1},{y1}) to ({x2},{y2})")
            else:
                return ActionResult(False, "swipe", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "swipe", "", str(e))
    
    def type_text(self, text: str) -> ActionResult:
        """Type text on screen"""
        try:
            # Escape special characters
            safe_text = text.replace('"', '\\"').replace("'", "\\'")
            
            result = subprocess.run(
                ['input', 'text', safe_text],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ActionResult(True, "type", f"Typed: {text[:20]}...")
            else:
                return ActionResult(False, "type", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "type", "", str(e))
    
    def press_key(self, keycode: str) -> ActionResult:
        """Press a key (BACK, HOME, RECENT, etc.)"""
        keycodes = {
            'back': 'KEYCODE_BACK',
            'home': 'KEYCODE_HOME',
            'recent': 'KEYCODE_APP_SWITCH',
            'power': 'KEYCODE_POWER',
            'volume_up': 'KEYCODE_VOLUME_UP',
            'volume_down': 'KEYCODE_VOLUME_DOWN',
            'enter': 'KEYCODE_ENTER',
        }
        
        key = keycodes.get(keycode.lower(), keycode)
        
        try:
            result = subprocess.run(
                ['input', 'keyevent', key],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ActionResult(True, "keypress", f"Pressed {key}")
            else:
                return ActionResult(False, "keypress", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "keypress", "", str(e))
    
    def open_app(self, package_name: str) -> ActionResult:
        """Open an app by package name"""
        try:
            result = subprocess.run(
                ['monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return ActionResult(True, "open_app", f"Opened {package_name}")
            else:
                return ActionResult(False, "open_app", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "open_app", "", str(e))
    
    def find_and_tap_text(self, text: str) -> ActionResult:
        """Find text on screen and tap it (using accessibility)"""
        # This requires accessibility service
        # For now, return not implemented
        return ActionResult(
            False, 
            "find_and_tap", 
            "", 
            "Accessibility service required for text detection"
        )
    
    def take_screenshot(self, save_path: str = "/sdcard/aura_screenshot.png") -> ActionResult:
        """Take a screenshot"""
        try:
            result = subprocess.run(
                ['screencap', '-p', save_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ActionResult(True, "screenshot", f"Screenshot saved: {save_path}")
            else:
                return ActionResult(False, "screenshot", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "screenshot", "", str(e))
    
    def get_current_app(self) -> ActionResult:
        """Get currently open app"""
        try:
            result = subprocess.run(
                ['dumpsys', 'window', 'windows', '|', 'grep', '-E', 'mCurrentFocus|mFocusedApp'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            if result.returncode == 0:
                return ActionResult(True, "get_app", result.stdout)
            else:
                return ActionResult(False, "get_app", "", result.stderr)
                
        except Exception as e:
            return ActionResult(False, "get_app", "", str(e))


class AppNavigator:
    """
    High-level app navigation
    Knows how to navigate common apps (WhatsApp, Phone, etc.)
    """
    
    def __init__(self, controller: AndroidController):
        self.controller = controller
        self.app_mappings = {
            'whatsapp': 'com.whatsapp',
            'phone': 'com.android.dialer',
            'messages': 'com.android.messaging',
            'contacts': 'com.android.contacts',
            'calendar': 'com.android.calendar',
            'settings': 'com.android.settings',
            'chrome': 'com.android.chrome',
            'gmail': 'com.google.android.gm',
        }
    
    def open_app_by_name(self, app_name: str) -> ActionResult:
        """Open app by common name"""
        app_name = app_name.lower().strip()
        package = self.app_mappings.get(app_name)
        
        if not package:
            return ActionResult(
                False,
                "open_app",
                "",
                f"Unknown app: {app_name}. Known apps: {list(self.app_mappings.keys())}"
            )
        
        return self.controller.open_app(package)
    
    def navigate_whatsapp_to_chat(self, contact_name: str) -> List[ActionResult]:
        """Navigate WhatsApp to specific contact chat"""
        results = []
        
        # 1. Open WhatsApp
        results.append(self.open_app_by_name('whatsapp'))
        time.sleep(2)
        
        # 2. Tap search (approximate position - top right)
        # This is a rough estimate, needs calibration
        results.append(self.controller.tap(950, 150))
        time.sleep(1)
        
        # 3. Type contact name
        results.append(self.controller.type_text(contact_name))
        time.sleep(1)
        
        # 4. Tap first result (approximate)
        results.append(self.controller.tap(540, 400))
        
        return results
    
    def send_whatsapp_message(self, contact: str, message: str) -> List[ActionResult]:
        """Send a WhatsApp message"""
        results = []
        
        # Navigate to chat
        results.extend(self.navigate_whatsapp_to_chat(contact))
        time.sleep(2)
        
        # Type message
        results.append(self.controller.type_text(message))
        time.sleep(0.5)
        
        # Tap send button (approximate position)
        results.append(self.controller.tap(950, 2200))
        
        return results
    
    def make_phone_call(self, number: str) -> List[ActionResult]:
        """Make a phone call"""
        results = []
        
        # Open phone app
        results.append(self.open_app_by_name('phone'))
        time.sleep(2)
        
        # Type number
        results.append(self.controller.type_text(number))
        time.sleep(0.5)
        
        # Tap call button (approximate)
        results.append(self.controller.tap(540, 2000))
        
        return results
