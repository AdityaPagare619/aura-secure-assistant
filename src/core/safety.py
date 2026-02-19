"""
AURA 2.0 - Safety & Emergency Controls
Provides mechanisms to stop AURA from external triggers
"""

import os
import logging
import signal
import sys
from datetime import datetime

logger = logging.getLogger(__name__)


class SafetySwitch:
    """
    Provides multiple ways to stop AURA:
    1. Telegram /stop command
    2. Kill file (data/.stop_aura)
    3. Signal handlers (Ctrl+C)
    4. Emergency timeout (if no heartbeat)
    """
    
    def __init__(self, callback_stop=None):
        self.callback_stop = callback_stop
        self.stop_file = "data/.stop_aura"
        self.lock_file = "data/.aura_running"
        self.heartbeat_file = "data/.aura_heartbeat"
        self.running = True
        
        # Create lock file to indicate AURA is running
        self._create_lock()
        
        # Setup signal handlers
        self._setup_signals()
        
    def _create_lock(self):
        """Create lock file to prevent multiple instances"""
        if os.path.exists(self.lock_file):
            # Check if it's stale (older than 1 hour)
            try:
                with open(self.lock_file, 'r') as f:
                    pid = f.read().strip()
                    if pid:
                        # Check if process is actually running
                        try:
                            os.kill(int(pid), 0)
                            logger.error(f"❌ AURA is already running (PID: {pid})")
                            logger.error("Use 'bash scripts/kill_aura.sh' to stop it first")
                            sys.exit(1)
                        except (OSError, ValueError):
                            # Process not running, stale lock
                            logger.warning("Removing stale lock file")
            except:
                pass
        
        # Create new lock file with current PID
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
            f.write(f"\n{datetime.now().isoformat()}")
        
        logger.info(f"🔒 Lock file created (PID: {os.getpid()})")
    
    def _setup_signals(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        sig_name = signal.Signals(signum).name
        logger.info(f"\n📡 Received signal {sig_name}")
        self.trigger_stop(f"Signal {sig_name} received")
    
    def check_stop_file(self):
        """Check if stop file exists (external trigger)"""
        if os.path.exists(self.stop_file):
            logger.info("🛑 Stop file detected")
            try:
                with open(self.stop_file, 'r') as f:
                    reason = f.read().strip()
                    self.trigger_stop(f"Stop file: {reason}")
            except:
                self.trigger_stop("Stop file triggered")
            finally:
                # Remove stop file
                try:
                    os.remove(self.stop_file)
                except:
                    pass
            return True
        return False
    
    def update_heartbeat(self):
        """Update heartbeat timestamp"""
        with open(self.heartbeat_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
    def check_heartbeat(self, max_age_seconds=300):
        """Check if heartbeat is recent (auto-kill if stuck)"""
        if not os.path.exists(self.heartbeat_file):
            return True
        
        try:
            with open(self.heartbeat_file, 'r') as f:
                last_beat = datetime.fromisoformat(f.read().strip())
                age = (datetime.now() - last_beat).total_seconds()
                
                if age > max_age_seconds:
                    logger.error(f"⚠️  No heartbeat for {age} seconds - AURA may be stuck")
                    return False
        except:
            pass
        
        return True
    
    def trigger_stop(self, reason="Manual stop"):
        """Trigger shutdown sequence"""
        if not self.running:
            return
        
        self.running = False
        logger.info(f"🛑 Stopping AURA: {reason}")
        
        # Call custom callback if provided
        if self.callback_stop:
            try:
                self.callback_stop()
            except Exception as e:
                logger.error(f"Error in stop callback: {e}")
        
        # Cleanup
        self.cleanup()
        
        # Exit
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up...")
        
        # Remove lock file
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                logger.info("✅ Lock file removed")
        except Exception as e:
            logger.error(f"Error removing lock: {e}")
        
        # Remove heartbeat file
        try:
            if os.path.exists(self.heartbeat_file):
                os.remove(self.heartbeat_file)
        except:
            pass
        
        logger.info("✅ Cleanup complete")


def create_stop_file(reason="Emergency stop"):
    """Create stop file to trigger AURA shutdown from outside"""
    stop_file = "data/.stop_aura"
    with open(stop_file, 'w') as f:
        f.write(reason)
        f.write(f"\n{datetime.now().isoformat()}")
    print(f"🛑 Stop file created: {reason}")
    print("AURA will stop within a few seconds...")


def is_aura_running():
    """Check if AURA is currently running"""
    lock_file = "data/.aura_running"
    
    if not os.path.exists(lock_file):
        return False
    
    try:
        with open(lock_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 1:
                pid = int(lines[0].strip())
                # Check if process exists
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    return False
    except:
        pass
    
    return False


def get_aura_pid():
    """Get AURA process ID if running"""
    lock_file = "data/.aura_running"
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                return int(f.readline().strip())
        except:
            pass
    
    return None
