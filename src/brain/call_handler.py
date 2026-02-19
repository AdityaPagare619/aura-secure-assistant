"""
Call Handler - Intelligent Call Answering System
AURA can actually pick up calls and have conversations
"""

import logging
import subprocess
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CallContext:
    """Context about an incoming call"""
    caller_number: str
    caller_name: Optional[str]
    is_contact: bool
    is_spam: bool
    relationship: str  # 'family', 'friend', 'work', 'unknown'
    recent_context: str  # Recent messages/conversations
    urgency: float  # 0.0 to 1.0


class CallHandler:
    """
    Handles incoming calls intelligently
    Can answer, talk, take messages, and relay information
    """
    
    def __init__(self, llm_server, memory_system, reasoning_engine):
        self.llm = llm_server
        self.memory = memory_system
        self.reasoning = reasoning_engine
        self.active_call = None
        
    async def handle_incoming_call(self, call_info: Dict) -> bool:
        """
        Handle incoming call - decide whether to answer and how
        Returns True if call was answered
        """
        number = call_info.get('number', 'Unknown')
        name = call_info.get('name')
        duration = call_info.get('duration', 0)
        
        logger.info(f"📞 Call from {name or number} (ringing for {duration}s)")
        
        # Build call context
        context = await self._build_call_context(call_info)
        
        # If 20 seconds passed and user hasn't picked up
        if duration >= 20:
            logger.info(f"⏰ Auto-answer trigger ({duration}s)")
            
            # Decide whether to answer
            should_answer = await self._should_answer_call(context)
            
            if should_answer:
                await self._answer_call(context)
                return True
            else:
                logger.info(f"📵 Declining call from {context.caller_name or number}")
                self._decline_call()
        
        return False
    
    async def _build_call_context(self, call_info: Dict) -> CallContext:
        """Build comprehensive context about the caller"""
        number = call_info.get('number', '')
        name = call_info.get('name')
        
        # Search memory for this contact
        contact_info = self._search_contact_info(number, name)
        
        # Search recent conversations
        recent = self.memory.recall(name or number, limit=5)
        recent_context = ""
        if recent:
            recent_context = "Recent interactions:\n" + "\n".join([
                f"- {r['content']}" for r in recent[:3]
            ])
        
        # Determine relationship
        relationship = self._determine_relationship(name, number, recent)
        
        # Check if spam
        is_spam = self._check_spam(number)
        
        # Calculate urgency
        urgency = self._calculate_urgency(relationship, recent)
        
        return CallContext(
            caller_number=number,
            caller_name=name,
            is_contact=bool(name),
            is_spam=is_spam,
            relationship=relationship,
            recent_context=recent_context,
            urgency=urgency
        )
    
    def _search_contact_info(self, number: str, name: Optional[str]) -> Dict:
        """Search for contact information"""
        # TODO: Query phone contacts database
        return {}
    
    def _determine_relationship(self, name: Optional[str], number: str, recent: list) -> str:
        """Determine relationship type"""
        if not name:
            return 'unknown'
        
        name_lower = name.lower()
        
        # Family keywords
        family_terms = ['papa', 'mama', 'dad', 'mom', 'father', 'mother', 'brother', 'sister']
        if any(term in name_lower for term in family_terms):
            return 'family'
        
        # Work keywords
        work_terms = ['boss', 'office', 'work', 'client', 'manager']
        if any(term in name_lower for term in work_terms):
            return 'work'
        
        # Check recent interaction frequency
        if recent and len(recent) > 5:
            return 'friend'
        
        return 'acquaintance'
    
    def _check_spam(self, number: str) -> bool:
        """Check if number is likely spam"""
        # TODO: Check against spam database
        # TODO: Check call patterns
        return False
    
    def _calculate_urgency(self, relationship: str, recent: list) -> float:
        """Calculate urgency score"""
        base_scores = {
            'family': 0.8,
            'work': 0.7,
            'friend': 0.5,
            'acquaintance': 0.4,
            'unknown': 0.3
        }
        
        return base_scores.get(relationship, 0.3)
    
    async def _should_answer_call(self, context: CallContext) -> bool:
        """Decide whether AURA should answer the call"""
        
        # Never answer spam
        if context.is_spam:
            return False
        
        # Always answer family (if urgent)
        if context.relationship == 'family' and context.urgency > 0.7:
            return True
        
        # Answer work calls during work hours (simplified)
        if context.relationship == 'work':
            hour = datetime.now().hour
            if 9 <= hour <= 18:  # Work hours
                return True
        
        # Answer if we have context about pending tasks
        if context.recent_context and 'need' in context.recent_context.lower():
            return True
        
        # Default: answer if it's a known contact
        return context.is_contact and context.urgency > 0.5
    
    async def _answer_call(self, context: CallContext):
        """Answer the call and handle conversation"""
        logger.info(f"📞 Answering call from {context.caller_name or context.caller_number}")
        
        # Actually answer the call (via Android API)
        self._perform_answer_call()
        
        # Generate greeting
        greeting = await self._generate_greeting(context)
        
        # Speak greeting (TTS)
        await self._speak(greeting)
        
        # Start conversation monitoring
        self.active_call = {
            'context': context,
            'started_at': datetime.now(),
            'transcript': [f"AURA: {greeting}"]
        }
        
        # Log the call
        self.memory.store(
            content=f"Answered call from {context.caller_name or context.caller_number}. Said: {greeting}",
            importance=0.9,
            metadata={
                'type': 'call_answered',
                'caller': context.caller_name or context.caller_number,
                'relationship': context.relationship
            }
        )
    
    async def _generate_greeting(self, context: CallContext) -> str:
        """Generate appropriate greeting based on context"""
        
        prompt = f"""You are AURA, an AI assistant answering a phone call for your boss.

CALLER: {context.caller_name or context.caller_number}
RELATIONSHIP: {context.relationship}
CONTEXT: {context.recent_context}

Generate a natural, friendly greeting (2-3 sentences) that:
1. Introduces yourself as the boss's assistant
2. Asks how you can help
3. Is appropriate for the relationship (formal for work, warm for family)

Example for family:
"Hello Papa! This is Aura, Aditya's assistant. He's not available right now, but I can help you. What do you need?"

Example for work:
"Hello, this is Aura, Aditya's AI assistant. He's currently unavailable. How may I assist you?"

Your greeting:"""
        
        greeting = self.llm.generate(prompt=prompt, max_tokens=150, temperature=0.8)
        return greeting.strip()
    
    def _perform_answer_call(self):
        """Actually answer the call via Android"""
        try:
            # Method 1: Input keyevent (may not work on all devices)
            subprocess.run(['input', 'keyevent', 'KEYCODE_CALL'], timeout=5)
            logger.info("Call answered via keyevent")
        except Exception as e:
            logger.error(f"Failed to answer call: {e}")
    
    def _decline_call(self):
        """Decline the call"""
        try:
            subprocess.run(['input', 'keyevent', 'KEYCODE_ENDCALL'], timeout=5)
            logger.info("Call declined")
        except Exception as e:
            logger.error(f"Failed to decline call: {e}")
    
    async def _speak(self, text: str):
        """Text-to-speech"""
        try:
            # Use termux-tts-speak
            subprocess.run(['termux-tts-speak', text], timeout=10)
            logger.info(f"🗣️ Spoke: {text[:50]}...")
        except Exception as e:
            logger.error(f"TTS failed: {e}")
    
    async def handle_call_conversation(self, transcript: str):
        """Handle ongoing conversation during call"""
        if not self.active_call:
            return
        
        context = self.active_call['context']
        
        # Add to transcript
        self.active_call['transcript'].append(f"CALLER: {transcript}")
        
        # Generate response
        prompt = f"""You are AURA on a phone call. Generate a response.

CALLER ({context.caller_name}): {transcript}

Recent conversation:
{chr(10).join(self.active_call['transcript'][-5:])}

Respond naturally and helpfully. Be concise (1-2 sentences). If you need to take a message or relay info, offer to do so."""
        
        response = self.llm.generate(prompt=prompt, max_tokens=150)
        
        # Speak response
        await self._speak(response)
        
        # Add to transcript
        self.active_call['transcript'].append(f"AURA: {response}")
        
        # Store in memory
        self.memory.store(
            content=f"Call with {context.caller_name}: {transcript} -> {response}",
            importance=0.8,
            metadata={'type': 'call_transcript'}
        )
    
    async def end_call(self):
        """End the active call"""
        if not self.active_call:
            return
        
        context = self.active_call['context']
        duration = (datetime.now() - self.active_call['started_at']).seconds
        
        logger.info(f"📞 Call ended. Duration: {duration}s")
        
        # Generate summary
        summary = await self._summarize_call()
        
        # Store summary
        self.memory.store(
            content=f"Call summary with {context.caller_name}: {summary}",
            importance=0.9,
            metadata={
                'type': 'call_summary',
                'caller': context.caller_name,
                'duration': duration
            }
        )
        
        # Notify boss
        await self._notify_boss(context, summary)
        
        self.active_call = None
    
    async def _summarize_call(self) -> str:
        """Generate summary of the call"""
        transcript = "\n".join(self.active_call['transcript'])
        
        prompt = f"""Summarize this phone call transcript in 2-3 sentences:

{transcript}

Summary:"""
        
        return self.llm.generate(prompt=prompt, max_tokens=100)
    
    async def _notify_boss(self, context: CallContext, summary: str):
        """Notify the boss about the call"""
        message = f"📞 Call from {context.caller_name}\n\n{summary}"
        
        # TODO: Send via Telegram
        logger.info(f"Notification to boss: {message}")
