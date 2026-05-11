"""
Voice Command System for Veyra

Implements:
- Whisper-based speech recognition
- Intent classification for trading commands
- Voice-controlled trading
- Multi-language support
- Real-time transcription

Based on OpenAI Whisper integration from analyzed data.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class VoiceIntent(Enum):
    """Recognized voice intents for trading."""
    PLACE_ORDER = "place_order"
    CHECK_BALANCE = "check_balance"
    CHECK_POSITIONS = "check_positions"
    CANCEL_ORDER = "cancel_order"
    GET_PRICE = "get_price"
    START_BOT = "start_bot"
    STOP_BOT = "stop_bot"
    GET_PROFIT_LOSS = "get_profit_loss"
    SWITCH_STRATEGY = "switch_strategy"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Represents a processed voice command."""
    transcript: str
    intent: VoiceIntent
    confidence: float
    parameters: Dict[str, Any]
    timestamp: datetime
    language: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'transcript': self.transcript,
            'intent': self.intent.value,
            'confidence': self.confidence,
            'parameters': self.parameters,
            'timestamp': self.timestamp.isoformat(),
            'language': self.language
        }


class VoiceCommandProcessor:
    """
    Voice command processing system using Whisper.
    
    Features:
    - Speech-to-text transcription
    - Intent classification
    - Parameter extraction
    - Multi-language support
    - Real-time processing
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize voice command processor.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.whisper_model = None
        self.intent_patterns = self._initialize_intent_patterns()
        self.command_history: List[VoiceCommand] = []
        self.max_history = 100
        
        # Callbacks for command execution
        self.intent_handlers: Dict[VoiceIntent, Callable] = {}
        
        logger.info(f"VoiceCommandProcessor initialized with model: {model_size}")
    
    def _initialize_intent_patterns(self) -> Dict[VoiceIntent, List[str]]:
        """Initialize keyword patterns for intent recognition."""
        return {
            VoiceIntent.PLACE_ORDER: [
                "buy", "sell", "order", "long", "short", "purchase", "execute",
                "buy bitcoin", "sell ethereum", "place order", "make trade"
            ],
            VoiceIntent.CHECK_BALANCE: [
                "balance", "account", "how much", "funds", "wallet",
                "check balance", "show balance", "what's my balance"
            ],
            VoiceIntent.CHECK_POSITIONS: [
                "positions", "holdings", "portfolio", "trades", "open orders",
                "show positions", "my positions", "current holdings"
            ],
            VoiceIntent.CANCEL_ORDER: [
                "cancel", "stop", "abort", "remove", "delete order",
                "cancel trade", "stop order", "abort trade"
            ],
            VoiceIntent.GET_PRICE: [
                "price", "current price", "market price", "trading at",
                "how much is", "what's the price of", "check price"
            ],
            VoiceIntent.START_BOT: [
                "start bot", "activate bot", "run bot", "enable bot",
                "begin trading", "start automation", "turn on bot"
            ],
            VoiceIntent.STOP_BOT: [
                "stop bot", "deactivate bot", "pause bot", "disable bot",
                "end trading", "stop automation", "turn off bot"
            ],
            VoiceIntent.GET_PROFIT_LOSS: [
                "profit", "loss", "pnl", "performance", "gains", "returns",
                "how am i doing", "show pnl", "trading performance"
            ],
            VoiceIntent.SWITCH_STRATEGY: [
                "switch strategy", "change strategy", "use strategy",
                "activate strategy", "strategy mode", "switch to"
            ],
            VoiceIntent.HELP: [
                "help", "commands", "what can i say", "assist", "guide",
                "how do i", "what are the commands"
            ]
        }
    
    async def load_model(self):
        """Load the Whisper model (lazy loading)."""
        if self.whisper_model is None:
            try:
                import whisper
                self.whisper_model = whisper.load_model(self.model_size)
                logger.info(f"Whisper model '{self.model_size}' loaded successfully")
            except ImportError:
                logger.error("Whisper not installed. Install with: pip install openai-whisper")
                raise
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
    
    async def process_audio(self, 
                          audio_data: bytes,
                          language: Optional[str] = None) -> VoiceCommand:
        """
        Process audio data into a voice command.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc.)
            language: Expected language code (optional)
            
        Returns:
            VoiceCommand with transcript and intent
        """
        await self.load_model()
        
        # Save audio to temp file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                tmp_path,
                language=language,
                fp16=False
            )
            
            transcript = result["text"].strip()
            detected_language = result.get("language", "en")
            
            # Classify intent
            intent, confidence, parameters = self._classify_intent(transcript)
            
            # Create command
            command = VoiceCommand(
                transcript=transcript,
                intent=intent,
                confidence=confidence,
                parameters=parameters,
                timestamp=datetime.now(),
                language=detected_language
            )
            
            # Add to history
            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
            
            logger.info(f"Voice command processed: {transcript} -> {intent.value}")
            
            return command
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
    
    async def process_text(self, text: str) -> VoiceCommand:
        """
        Process text directly (for testing or text-based commands).
        
        Args:
            text: Command text
            
        Returns:
            VoiceCommand
        """
        intent, confidence, parameters = self._classify_intent(text)
        
        command = VoiceCommand(
            transcript=text,
            intent=intent,
            confidence=confidence,
            parameters=parameters,
            timestamp=datetime.now(),
            language="en"
        )
        
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        return command
    
    def _classify_intent(self, text: str) -> tuple:
        """
        Classify intent from transcribed text.
        
        Returns:
            Tuple of (intent, confidence, parameters)
        """
        text_lower = text.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            # Bonus for exact matches
            for pattern in patterns:
                words = pattern.split()
                if all(word in text_lower for word in words):
                    score += 2
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return VoiceIntent.UNKNOWN, 0.0, {}
        
        # Get highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / 5, 1.0)  # Normalize to 0-1
        
        # Extract parameters
        parameters = self._extract_parameters(text_lower, best_intent)
        
        return best_intent, confidence, parameters
    
    def _extract_parameters(self, text: str, intent: VoiceIntent) -> Dict[str, Any]:
        """Extract parameters from text based on intent."""
        parameters = {}
        
        # Common symbols/pairs
        symbols = [
            "btc", "bitcoin", "eth", "ethereum", "sol", "solana",
            "ada", "cardano", "dot", "polkadot", "xrp", "ripple",
            "doge", "dogecoin", "ltc", "litecoin", "bnb", "binance",
            "eur/usd", "gbp/usd", "usd/jpy", "aud/usd", "usd/chf"
        ]
        
        # Extract symbol
        for symbol in symbols:
            if symbol in text:
                parameters['symbol'] = symbol.upper()
                break
        
        # Extract amount
        import re
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(btc|eth|usd|eur|gbp|shares|units|contracts)?', text)
        if amount_match:
            parameters['amount'] = float(amount_match.group(1))
            parameters['unit'] = amount_match.group(2) if amount_match.group(2) else 'units'
        
        # Extract price (for limit orders)
        price_match = re.search(r'(?:at|@)\s*(\d+(?:\.\d+)?)', text)
        if price_match:
            parameters['price'] = float(price_match.group(1))
        
        # Extract order type
        if 'market' in text:
            parameters['order_type'] = 'market'
        elif 'limit' in text:
            parameters['order_type'] = 'limit'
        elif 'stop' in text:
            parameters['order_type'] = 'stop'
        
        # Extract side
        if 'buy' in text or 'long' in text:
            parameters['side'] = 'buy'
        elif 'sell' in text or 'short' in text:
            parameters['side'] = 'sell'
        
        # Intent-specific parameters
        if intent == VoiceIntent.START_BOT or intent == VoiceIntent.STOP_BOT:
            # Extract bot/strategy name
            for word in ['grid', 'dca', 'arbitrage', 'momentum', 'scalping']:
                if word in text:
                    parameters['bot_type'] = word
                    break
        
        if intent == VoiceIntent.SWITCH_STRATEGY:
            # Extract strategy name
            strategies = ['conservative', 'aggressive', 'balanced', 'scalping', 'swing']
            for strategy in strategies:
                if strategy in text:
                    parameters['strategy'] = strategy
                    break
        
        return parameters
    
    def register_intent_handler(self, intent: VoiceIntent, handler: Callable):
        """Register a handler for a specific intent."""
        self.intent_handlers[intent] = handler
        logger.info(f"Handler registered for intent: {intent.value}")
    
    async def execute_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """
        Execute a voice command using registered handlers.
        
        Returns:
            Execution result
        """
        if command.intent not in self.intent_handlers:
            return {
                'success': False,
                'message': f"No handler registered for intent: {command.intent.value}",
                'command': command.to_dict()
            }
        
        handler = self.intent_handlers[command.intent]
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(command)
            else:
                result = handler(command)
            
            return {
                'success': True,
                'result': result,
                'command': command.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error executing voice command: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command.to_dict()
            }
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """Get list of supported voice commands."""
        return {
            "Place Orders": [
                "Buy 0.5 BTC",
                "Sell 1000 EUR/USD at 1.0850",
                "Long Ethereum with market order",
                "Short Bitcoin with stop loss at 40000"
            ],
            "Account Info": [
                "Check my balance",
                "Show my positions",
                "What's my profit and loss",
                "How am I doing today"
            ],
            "Bot Control": [
                "Start the grid bot",
                "Stop the DCA bot",
                "Activate arbitrage strategy",
                "Switch to conservative mode"
            ],
            "Market Data": [
                "What's the price of Bitcoin",
                "Current Ethereum price",
                "Show BTC/USD chart"
            ],
            "Order Management": [
                "Cancel my last order",
                "Close all positions",
                "Show open orders"
            ]
        }
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return [cmd.to_dict() for cmd in self.command_history[-limit:]]


class VoiceCommandAPI:
    """FastAPI integration for voice commands."""
    
    def __init__(self):
        self.processor = VoiceCommandProcessor()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup default intent handlers."""
        # These would connect to actual trading functions
        self.processor.register_intent_handler(
            VoiceIntent.PLACE_ORDER,
            self._handle_place_order
        )
        self.processor.register_intent_handler(
            VoiceIntent.CHECK_BALANCE,
            self._handle_check_balance
        )
        self.processor.register_intent_handler(
            VoiceIntent.GET_PRICE,
            self._handle_get_price
        )
        self.processor.register_intent_handler(
            VoiceIntent.HELP,
            self._handle_help
        )
    
    async def _handle_place_order(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handler for place order intent."""
        params = command.parameters
        
        return {
            'action': 'place_order',
            'symbol': params.get('symbol', 'UNKNOWN'),
            'side': params.get('side', 'buy'),
            'amount': params.get('amount', 0),
            'order_type': params.get('order_type', 'market'),
            'price': params.get('price'),
            'status': 'pending_execution'
        }
    
    async def _handle_check_balance(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handler for check balance intent."""
        return {
            'action': 'check_balance',
            'status': 'retrieving',
            'note': 'Connect to actual balance API'
        }
    
    async def _handle_get_price(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handler for get price intent."""
        symbol = command.parameters.get('symbol', 'BTC')
        return {
            'action': 'get_price',
            'symbol': symbol,
            'price': None,  # Would fetch from market data
            'note': 'Connect to price feed API'
        }
    
    async def _handle_help(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handler for help intent."""
        return {
            'action': 'help',
            'available_commands': self.processor.get_supported_commands()
        }


# Singleton instance
voice_processor = VoiceCommandProcessor()


async def process_voice_command(audio_data: bytes, 
                               language: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for voice command processing."""
    command = await voice_processor.process_audio(audio_data, language)
    return await voice_processor.execute_command(command)


async def process_text_command(text: str) -> Dict[str, Any]:
    """Convenience function for text command processing."""
    command = await voice_processor.process_text(text)
    return await voice_processor.execute_command(command)
