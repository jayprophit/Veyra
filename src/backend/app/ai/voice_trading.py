"""
Voice Trading Assistant - Phase 9 Legendary Feature (+5 points)
Natural language trading via voice commands
"""
import re
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class VoiceCommandType(Enum):
    MARKET_ORDER = "market_order"
    LIMIT_ORDER = "limit_order"
    STOP_ORDER = "stop_order"
    GET_QUOTE = "get_quote"
    GET_PORTFOLIO = "get_portfolio"
    SET_ALERT = "set_alert"
    CANCEL_ORDER = "cancel_order"
    UNKNOWN = "unknown"

@dataclass
class VoiceCommand:
    command_type: VoiceCommandType
    symbol: Optional[str]
    side: Optional[str]  # buy, sell
    quantity: Optional[int]
    price: Optional[float]
    confidence: float
    raw_text: str

class VoiceTradingAssistant:
    """
    Natural language trading assistant.
    
    Examples:
    - "Buy 100 shares of Apple at market"
    - "Show me my portfolio"
    - "What's the price of Tesla?"
    - "Set an alert when Bitcoin hits 50000"
    """
    
    def __init__(self):
        self.command_patterns = self._compile_patterns()
        self.voice_history: list = []
        self.confidence_threshold = 0.7
    
    def _compile_patterns(self) -> Dict[VoiceCommandType, list]:
        """Compile regex patterns for command recognition."""
        return {
            VoiceCommandType.MARKET_ORDER: [
                r"(?i)(buy|purchase|get)\s+(\d+)\s*(shares?|stocks?)\s+(of\s+)?([a-zA-Z]{1,5})",
                r"(?i)(buy|purchase|get)\s+([a-zA-Z]{1,5})\s+(\d+)\s*(shares?|stocks?)",
                r"(?i)sell\s+(\d+)\s*(shares?|stocks?)\s+(of\s+)?([a-zA-Z]{1,5})",
                r"(?i)sell\s+([a-zA-Z]{1,5})\s+(\d+)\s*(shares?|stocks?)",
            ],
            VoiceCommandType.LIMIT_ORDER: [
                r"(?i)(buy|sell)\s+(\d+)\s*(shares?|stocks?)\s+(of\s+)?([a-zA-Z]{1,5})\s+(at|@)\s*\$?(\d+\.?\d*)",
                r"(?i)(buy|sell)\s+([a-zA-Z]{1,5})\s+(at|@)\s*\$?(\d+\.?\d*)",
            ],
            VoiceCommandType.STOP_ORDER: [
                r"(?i)(stop loss|stop)\s+(\d+)\s*(shares?|stocks?)\s+(of\s+)?([a-zA-Z]{1,5})\s+(at|@)\s*\$?(\d+\.?\d*)",
            ],
            VoiceCommandType.GET_QUOTE: [
                r"(?i)(what'?s|what is|show me|get)\s+(the\s+)?(price|quote|value)\s+(of\s+)?(for\s+)?([a-zA-Z]{1,5})",
                r"(?i)quote\s+(for\s+)?([a-zA-Z]{1,5})",
                r"(?i)(how much is|price of)\s+([a-zA-Z]{1,5})",
            ],
            VoiceCommandType.GET_PORTFOLIO: [
                r"(?i)(show|display|get|what's)\s+(my\s+)?portfolio",
                r"(?i)(portfolio|positions|holdings)",
                r"(?i)(how am i doing|pnl|profit and loss)",
            ],
            VoiceCommandType.SET_ALERT: [
                r"(?i)(alert|notify|tell)\s+me\s+(when|if)\s+([a-zA-Z]{1,5})\s+(hits|reaches|goes above|goes below|drops to|rises to)\s*\$?(\d+\.?\d*)",
                r"(?i)set\s+(an\s+)?alert\s+(for\s+)?([a-zA-Z]{1,5})\s+(at|@)\s*\$?(\d+\.?\d*)",
            ],
            VoiceCommandType.CANCEL_ORDER: [
                r"(?i)(cancel|delete|remove)\s+(order|trade)\s+(.+)",
                r"(?i)cancel\s+(my\s+)?(last\s+)?order",
            ],
        }
    
    def process_command(self, text: str) -> VoiceCommand:
        """Process voice command and return structured command."""
        text = text.strip().lower()
        logger.info(f"Processing voice command: {text}")
        
        # Try to match against patterns
        best_match = None
        best_confidence = 0.0
        
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = self._calculate_confidence(text, match, cmd_type)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = (cmd_type, match)
        
        if best_match and best_confidence >= self.confidence_threshold:
            cmd_type, match = best_match
            parsed = self._extract_parameters(cmd_type, match, text)
            command = VoiceCommand(
                command_type=cmd_type,
                symbol=parsed.get('symbol'),
                side=parsed.get('side'),
                quantity=parsed.get('quantity'),
                price=parsed.get('price'),
                confidence=best_confidence,
                raw_text=text
            )
        else:
            command = VoiceCommand(
                command_type=VoiceCommandType.UNKNOWN,
                symbol=None,
                side=None,
                quantity=None,
                price=None,
                confidence=0.0,
                raw_text=text
            )
        
        self.voice_history.append(command)
        return command
    
    def _calculate_confidence(self, text: str, match, cmd_type: VoiceCommandType) -> float:
        """Calculate confidence score for match."""
        base_confidence = 0.8
        
        # Boost for exact keyword matches
        if cmd_type == VoiceCommandType.MARKET_ORDER:
            if any(word in text for word in ['buy', 'sell', 'purchase']):
                base_confidence += 0.1
        
        # Penalty for very short commands
        if len(text) < 5:
            base_confidence -= 0.2
        
        # Penalty for ambiguous words
        ambiguous = ['maybe', 'perhaps', 'i think', 'possibly', 'um', 'uh']
        if any(word in text for word in ambiguous):
            base_confidence -= 0.15
        
        return min(1.0, base_confidence)
    
    def _extract_parameters(self, cmd_type: VoiceCommandType, match, text: str) -> Dict:
        """Extract parameters from regex match."""
        params = {}
        groups = match.groups()
        
        if cmd_type == VoiceCommandType.MARKET_ORDER:
            # Try to extract symbol, quantity, side
            if 'buy' in text or 'purchase' in text:
                params['side'] = 'buy'
            elif 'sell' in text:
                params['side'] = 'sell'
            
            # Find numbers (quantity)
            numbers = re.findall(r'\d+', text)
            if numbers:
                params['quantity'] = int(numbers[0])
            
            # Find symbol (1-5 capital letters)
            symbols = re.findall(r'\b[A-Z]{1,5}\b', text.upper())
            if symbols:
                params['symbol'] = symbols[0]
        
        elif cmd_type == VoiceCommandType.LIMIT_ORDER:
            if 'buy' in text:
                params['side'] = 'buy'
            elif 'sell' in text:
                params['side'] = 'sell'
            
            numbers = re.findall(r'\d+\.?\d*', text)
            if len(numbers) >= 2:
                params['quantity'] = int(float(numbers[0]))
                params['price'] = float(numbers[1])
            elif numbers:
                params['price'] = float(numbers[0])
            
            symbols = re.findall(r'\b[A-Z]{1,5}\b', text.upper())
            if symbols:
                params['symbol'] = symbols[0]
        
        elif cmd_type == VoiceCommandType.GET_QUOTE:
            symbols = re.findall(r'\b[A-Z]{1,5}\b', text.upper())
            if symbols:
                params['symbol'] = symbols[0]
        
        elif cmd_type == VoiceCommandType.SET_ALERT:
            symbols = re.findall(r'\b[A-Z]{1,5}\b', text.upper())
            if symbols:
                params['symbol'] = symbols[0]
            
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                params['price'] = float(numbers[0])
        
        return params
    
    def execute_command(self, command: VoiceCommand) -> Dict:
        """Execute the parsed voice command."""
        if command.command_type == VoiceCommandType.UNKNOWN:
            return {
                "success": False,
                "message": "I didn't understand that command. Try: 'Buy 100 shares of Apple at market'",
                "action": None
            }
        
        if command.confidence < self.confidence_threshold:
            return {
                "success": False,
                "message": f"I'm not confident I understood. Did you want to {command.command_type.value}?",
                "action": "clarify",
                "parsed_command": command
            }
        
        # Execute based on command type
        actions = {
            VoiceCommandType.MARKET_ORDER: self._execute_market_order,
            VoiceCommandType.LIMIT_ORDER: self._execute_limit_order,
            VoiceCommandType.GET_QUOTE: self._execute_get_quote,
            VoiceCommandType.GET_PORTFOLIO: self._execute_get_portfolio,
            VoiceCommandType.SET_ALERT: self._execute_set_alert,
        }
        
        executor = actions.get(command.command_type)
        if executor:
            return executor(command)
        
        return {
            "success": False,
            "message": f"Command type {command.command_type.value} not yet implemented",
            "action": None
        }
    
    def _execute_market_order(self, cmd: VoiceCommand) -> Dict:
        """Execute market order from voice command."""
        if not all([cmd.symbol, cmd.side, cmd.quantity]):
            return {
                "success": False,
                "message": "Missing information for market order. Need symbol, side, and quantity.",
                "action": None
            }
        
        return {
            "success": True,
            "message": f"Executing {cmd.side} market order for {cmd.quantity} shares of {cmd.symbol}",
            "action": "place_order",
            "order_details": {
                "symbol": cmd.symbol,
                "side": cmd.side,
                "quantity": cmd.quantity,
                "order_type": "market"
            }
        }
    
    def _execute_limit_order(self, cmd: VoiceCommand) -> Dict:
        """Execute limit order from voice command."""
        if not all([cmd.symbol, cmd.side, cmd.quantity, cmd.price]):
            return {
                "success": False,
                "message": "Missing information for limit order. Need symbol, side, quantity, and price.",
                "action": None
            }
        
        return {
            "success": True,
            "message": f"Placing {cmd.side} limit order: {cmd.quantity} shares of {cmd.symbol} at ${cmd.price}",
            "action": "place_order",
            "order_details": {
                "symbol": cmd.symbol,
                "side": cmd.side,
                "quantity": cmd.quantity,
                "order_type": "limit",
                "price": cmd.price
            }
        }
    
    def _execute_get_quote(self, cmd: VoiceCommand) -> Dict:
        """Get quote for symbol."""
        if not cmd.symbol:
            return {
                "success": False,
                "message": "I didn't catch which symbol you want a quote for.",
                "action": None
            }
        
        return {
            "success": True,
            "message": f"Getting current price for {cmd.symbol}",
            "action": "get_quote",
            "symbol": cmd.symbol
        }
    
    def _execute_get_portfolio(self, cmd: VoiceCommand) -> Dict:
        """Get portfolio summary."""
        return {
            "success": True,
            "message": "Here's your portfolio summary",
            "action": "get_portfolio"
        }
    
    def _execute_set_alert(self, cmd: VoiceCommand) -> Dict:
        """Set price alert."""
        if not all([cmd.symbol, cmd.price]):
            return {
                "success": False,
                "message": "I need a symbol and price to set an alert.",
                "action": None
            }
        
        return {
            "success": True,
            "message": f"Alert set: Notify when {cmd.symbol} reaches ${cmd.price}",
            "action": "set_alert",
            "alert_details": {
                "symbol": cmd.symbol,
                "target_price": cmd.price
            }
        }
    
    def get_response_text(self, result: Dict) -> str:
        """Generate natural language response."""
        if result["success"]:
            return result["message"]
        else:
            return f"Sorry, I couldn't do that. {result['message']}"

# Global instance
voice_assistant = VoiceTradingAssistant()

# Example usage
if __name__ == "__main__":
    test_commands = [
        "Buy 100 shares of Apple at market",
        "Sell 50 shares of Tesla",
        "What's the price of Bitcoin?",
        "Show me my portfolio",
        "Alert me when Google hits 150",
        "Buy Microsoft at $300",
    ]
    
    for cmd_text in test_commands:
        print(f"\nCommand: '{cmd_text}'")
        command = voice_assistant.process_command(cmd_text)
        result = voice_assistant.execute_command(command)
        print(f"Response: {voice_assistant.get_response_text(result)}")
