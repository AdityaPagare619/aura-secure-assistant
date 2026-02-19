"""
Tool Executor - Connects LLM reasoning to real actions
Parses LLM output and executes tools
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..actions.android_controller import AndroidController, AppNavigator

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    tool: str
    params: Dict[str, Any]
    reasoning: str


class ToolRegistry:
    """Registry of available tools"""
    
    def __init__(self):
        self.tools = {}
        self.controller = AndroidController()
        self.navigator = AppNavigator(self.controller)
        
        # Register tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        
        # Communication tools
        self.register("send_whatsapp_message", self._send_whatsapp)
        self.register("make_phone_call", self._make_call)
        self.register("send_sms", self._send_sms)
        
        # App control tools
        self.register("open_app", self._open_app)
        self.register("tap_screen", self._tap_screen)
        self.register("type_text", self._type_text)
        self.register("press_back", self._press_back)
        self.register("press_home", self._press_home)
        
        # Information tools
        self.register("get_current_app", self._get_current_app)
        self.register("take_screenshot", self._take_screenshot)
        
        # Wait tool
        self.register("wait", self._wait)
    
    def register(self, name: str, func):
        """Register a tool"""
        self.tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str):
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for LLM"""
        descriptions = [
            "Available tools:",
            "",
            "COMMUNICATION:",
            "- send_whatsapp_message(contact: str, message: str): Send WhatsApp message",
            "- make_phone_call(number: str): Make a phone call", 
            "- send_sms(number: str, message: str): Send SMS message",
            "",
            "APP CONTROL:",
            "- open_app(app_name: str): Open an app (whatsapp, phone, messages, calendar, etc.)",
            "- tap_screen(x: int, y: int): Tap at screen coordinates",
            "- type_text(text: str): Type text on screen",
            "- press_back(): Press back button",
            "- press_home(): Press home button",
            "",
            "INFORMATION:",
            "- get_current_app(): Get currently open app",
            "- take_screenshot(): Take a screenshot",
            "",
            "UTILITY:",
            "- wait(seconds: int): Wait for specified seconds",
        ]
        return "\n".join(descriptions)
    
    # Tool implementations
    def _send_whatsapp(self, contact: str, message: str) -> Dict:
        """Send WhatsApp message"""
        logger.info(f"Tool: Sending WhatsApp to {contact}")
        results = self.navigator.send_whatsapp_message(contact, message)
        return {
            "success": all(r.success for r in results),
            "results": [{"action": r.action, "success": r.success} for r in results]
        }
    
    def _make_call(self, number: str) -> Dict:
        """Make phone call"""
        logger.info(f"Tool: Making call to {number}")
        results = self.navigator.make_phone_call(number)
        return {
            "success": all(r.success for r in results),
            "results": [{"action": r.action, "success": r.success} for r in results]
        }
    
    def _send_sms(self, number: str, message: str) -> Dict:
        """Send SMS"""
        logger.info(f"Tool: Sending SMS to {number}")
        # TODO: Implement SMS
        return {"success": False, "error": "SMS not yet implemented"}
    
    def _open_app(self, app_name: str) -> Dict:
        """Open app"""
        logger.info(f"Tool: Opening app {app_name}")
        result = self.navigator.open_app_by_name(app_name)
        return {"success": result.success, "output": result.output, "error": result.error}
    
    def _tap_screen(self, x: int, y: int) -> Dict:
        """Tap screen"""
        logger.info(f"Tool: Tapping at ({x}, {y})")
        result = self.controller.tap(x, y)
        return {"success": result.success, "output": result.output, "error": result.error}
    
    def _type_text(self, text: str) -> Dict:
        """Type text"""
        logger.info(f"Tool: Typing text")
        result = self.controller.type_text(text)
        return {"success": result.success, "output": result.output, "error": result.error}
    
    def _press_back(self) -> Dict:
        """Press back"""
        result = self.controller.press_key('back')
        return {"success": result.success}
    
    def _press_home(self) -> Dict:
        """Press home"""
        result = self.controller.press_key('home')
        return {"success": result.success}
    
    def _get_current_app(self) -> Dict:
        """Get current app"""
        result = self.controller.get_current_app()
        return {"success": result.success, "app": result.output}
    
    def _take_screenshot(self) -> Dict:
        """Take screenshot"""
        result = self.controller.take_screenshot()
        return {"success": result.success, "path": result.output}
    
    def _wait(self, seconds: int) -> Dict:
        """Wait"""
        import time
        time.sleep(seconds)
        return {"success": True, "waited": seconds}


class ToolExecutor:
    """
    Parses LLM output and executes tools
    Similar to OpenClaw's function calling system
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
    
    def parse_llm_response(self, response: str) -> Optional[ToolCall]:
        """
        Parse LLM response to extract tool calls
        Looks for patterns like:
        ACTION: send_whatsapp_message
        PARAMS: {"contact": "Papa", "message": "Hello"}
        """
        # Try to find JSON format
        json_pattern = r'```(?:json)?\s*({[\s\S]*?})\s*```'
        json_match = re.search(json_pattern, response)
        
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if 'action' in data:
                    return ToolCall(
                        tool=data['action'],
                        params=data.get('params', {}),
                        reasoning=data.get('reasoning', '')
                    )
            except json.JSONDecodeError:
                pass
        
        # Try simple format: ACTION: tool_name
        action_pattern = r'ACTION:\s*(\w+)'
        action_match = re.search(action_pattern, response, re.IGNORECASE)
        
        if action_match:
            tool_name = action_match.group(1)
            
            # Try to find params
            params = {}
            params_pattern = r'PARAMS:\s*({[\s\S]*?})'
            params_match = re.search(params_pattern, response)
            
            if params_match:
                try:
                    params = json.loads(params_match.group(1))
                except:
                    pass
            
            return ToolCall(
                tool=tool_name,
                params=params,
                reasoning="Extracted from response"
            )
        
        return None
    
    def execute_tool(self, tool_call: ToolCall) -> Dict:
        """Execute a tool call"""
        tool = self.registry.get_tool(tool_call.tool)
        
        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_call.tool}",
                "available_tools": self.registry.list_tools()
            }
        
        try:
            result = tool(**tool_call.params)
            return {
                "success": result.get("success", False),
                "tool": tool_call.tool,
                "params": tool_call.params,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "tool": tool_call.tool,
                "error": str(e)
            }
    
    def execute_plan(self, tool_calls: List[ToolCall]) -> List[Dict]:
        """Execute multiple tool calls"""
        results = []
        
        for call in tool_calls:
            result = self.execute_tool(call)
            results.append(result)
            
            # Stop on critical failure
            if not result["success"]:
                logger.warning(f"Tool {call.tool} failed, stopping plan")
                break
        
        return results
