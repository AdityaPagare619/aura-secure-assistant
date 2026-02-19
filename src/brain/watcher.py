"""
Watcher Layer - Always-on monitoring
Detects events: calls, notifications, time triggers
Minimal resources: <50MB RAM
"""

import asyncio
import logging
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class Event:
    type: str  # 'call', 'notification', 'calendar', 'user_message'
    source: str
    data: Dict
    timestamp: datetime
    priority: float  # 0.0 to 1.0


class Watcher:
    """
    Ultra-lightweight event watcher
    Monitors phone 24/7 with minimal resources
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self.event_queue = asyncio.Queue()
        self.event_counts: Dict[str, int] = {}
        
        # Call tracking
        self.active_calls: Dict[str, Dict] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type}")
    
    async def start(self):
        """Start watching for events"""
        self.running = True
        logger.info("Watcher started - monitoring phone")
        
        # Start processors
        asyncio.create_task(self._process_events())
        
        # Start monitoring loops
        asyncio.create_task(self._monitor_calls())
        asyncio.create_task(self._monitor_notifications())
        asyncio.create_task(self._monitor_time())
        
        logger.info("All monitoring loops active")
    
    async def _monitor_calls(self):
        """Monitor incoming calls"""
        while self.running:
            try:
                # Check for calls using termux API
                call_info = await self._check_call_status()
                
                if call_info:
                    call_id = call_info.get('number', 'unknown')
                    
                    # Track call duration
                    if call_id not in self.active_calls:
                        # New call
                        self.active_calls[call_id] = {
                            'start_time': datetime.now(),
                            'number': call_id,
                            'name': call_info.get('name', 'Unknown')
                        }
                        
                        # Create event
                        event = Event(
                            type='call',
                            source='phone',
                            data={
                                'number': call_id,
                                'name': call_info.get('name', 'Unknown'),
                                'duration': 0,
                                'state': 'ringing'
                            },
                            timestamp=datetime.now(),
                            priority=self._calculate_call_priority(call_info)
                        )
                        await self.event_queue.put(event)
                    else:
                        # Ongoing call - check duration
                        call = self.active_calls[call_id]
                        duration = (datetime.now() - call['start_time']).seconds
                        
                        if duration == 20:  # 20 second mark
                            event = Event(
                                type='call_auto_answer',
                                source='phone',
                                data={
                                    'number': call_id,
                                    'name': call['name'],
                                    'duration': duration,
                                    'state': 'auto_answer_ready'
                                },
                                timestamp=datetime.now(),
                                priority=0.9
                            )
                            await self.event_queue.put(event)
                        
                else:
                    # Clear ended calls
                    self.active_calls.clear()
                    
            except Exception as e:
                logger.error(f"Call monitoring error: {e}")
            
            await asyncio.sleep(1)
    
    async def _monitor_notifications(self):
        """Monitor phone notifications"""
        last_notifications = set()
        
        while self.running:
            try:
                # Get notifications
                notifications = await self._get_notifications()
                
                for notif in notifications:
                    notif_id = f"{notif.get('package')}:{notif.get('title')}"
                    
                    if notif_id not in last_notifications:
                        # New notification
                        last_notifications.add(notif_id)
                        
                        event = Event(
                            type='notification',
                            source=notif.get('package', 'unknown'),
                            data=notif,
                            timestamp=datetime.now(),
                            priority=self._calculate_notification_priority(notif)
                        )
                        await self.event_queue.put(event)
                
                # Keep set manageable
                if len(last_notifications) > 100:
                    last_notifications.clear()
                    
            except Exception as e:
                logger.error(f"Notification monitoring error: {e}")
            
            await asyncio.sleep(2)
    
    async def _monitor_time(self):
        """Monitor time-based triggers"""
        while self.running:
            try:
                now = datetime.now()
                
                # Check calendar events
                events = await self._check_calendar(now)
                for event in events:
                    event_time = datetime.fromisoformat(event.get('time', ''))
                    minutes_until = (event_time - now).total_seconds() / 60
                    
                    if 4 < minutes_until <= 5:  # 5 minute warning
                        evt = Event(
                            type='calendar_5min',
                            source='calendar',
                            data=event,
                            timestamp=now,
                            priority=0.8
                        )
                        await self.event_queue.put(evt)
                    elif 0 < minutes_until <= 2:  # 2 minute urgent
                        evt = Event(
                            type='calendar_urgent',
                            source='calendar',
                            data=event,
                            timestamp=now,
                            priority=0.95
                        )
                        await self.event_queue.put(evt)
                
            except Exception as e:
                logger.error(f"Time monitoring error: {e}")
            
            await asyncio.sleep(30)
    
    async def _process_events(self):
        """Process events from queue"""
        while self.running:
            try:
                event = await self.event_queue.get()
                
                # Update stats
                self.event_counts[event.type] = self.event_counts.get(event.type, 0) + 1
                
                # Log event
                logger.info(f"Event: {event.type} from {event.source} (priority: {event.priority})")
                
                # Route to handlers
                handlers = self.event_handlers.get(event.type, [])
                for handler in handlers:
                    try:
                        asyncio.create_task(handler(event))
                    except Exception as e:
                        logger.error(f"Handler error: {e}")
                
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Event processing error: {e}")
    
    async def _check_call_status(self) -> Optional[Dict]:
        """Check for incoming calls via termux"""
        try:
            # Use termux-telephony-call to check
            result = os.popen("termux-telephony-call -l 2>/dev/null || echo '[]'").read()
            calls = json.loads(result)
            
            for call in calls:
                if call.get('state') == 'RINGING':
                    return {
                        'number': call.get('number', 'unknown'),
                        'name': call.get('name', 'Unknown'),
                        'state': 'RINGING'
                    }
        except:
            pass
        return None
    
    async def _get_notifications(self) -> List[Dict]:
        """Get notifications via termux"""
        try:
            # Use termux-notification-list
            result = os.popen("termux-notification-list 2>/dev/null || echo '[]'").read()
            return json.loads(result)
        except:
            return []
    
    async def _check_calendar(self, now: datetime) -> List[Dict]:
        """Check calendar events"""
        try:
            # Use termux-calendar-list
            result = os.popen("termux-calendar-list -n 5 2>/dev/null || echo '[]'").read()
            return json.loads(result)
        except:
            return []
    
    def _calculate_call_priority(self, call_info: Dict) -> float:
        """Calculate call priority"""
        if call_info.get('is_contact'):
            return 0.8
        if call_info.get('is_spam'):
            return 0.1
        return 0.5
    
    def _calculate_notification_priority(self, notif: Dict) -> float:
        """Calculate notification priority"""
        app = notif.get('package', '').lower()
        title = notif.get('title', '').lower()
        
        # High priority apps
        if app in ['com.whatsapp', 'com.google.android.gm']:
            if any(kw in title for kw in ['urgent', 'asap', 'meeting', 'call']):
                return 0.9
            return 0.7
        
        return 0.3
    
    async def stop(self):
        """Stop watching"""
        self.running = False
        logger.info("Watcher stopped")
    
    def get_stats(self) -> Dict:
        """Get watcher statistics"""
        return {
            'event_counts': self.event_counts,
            'active_calls': len(self.active_calls),
            'queue_size': self.event_queue.qsize()
        }
