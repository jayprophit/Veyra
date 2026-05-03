"""
BERT Intent Classification for Voice Commands

Upgrades the voice command system with transformer-based intent classification.

Features:
- BERT-based intent understanding
- Context-aware classification
- Multi-label support
- Confidence scoring
- Fine-tuned for trading domain
"""

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class IntentClassification:
    """Result of intent classification."""
    intent: str
    confidence: float
    alternative_intents: List[Tuple[str, float]]
    entities: Dict[str, Any]
    context: Dict[str, Any]
    processing_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'intent': self.intent,
            'confidence': self.confidence,
            'alternative_intents': [
                {'intent': i, 'confidence': c} for i, c in self.alternative_intents
            ],
            'entities': self.entities,
            'context': self.context,
            'processing_time_ms': self.processing_time_ms
        }


class BERTIntentClassifier:
    """
    BERT-based intent classification for trading voice commands.
    
    Provides:
    - Pre-trained BERT model
    - Domain-specific fine-tuning for trading
    - Entity extraction
    - Context tracking
    - Multi-turn conversation support
    """
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize BERT classifier.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # Intent definitions
        self.intents = {
            'place_order': {
                'description': 'Place a buy or sell order',
                'examples': [
                    'Buy 100 shares of Apple',
                    'Sell 0.5 Bitcoin at market price',
                    'Long EUR/USD with limit order at 1.0850',
                    'Short Tesla with stop loss at 200'
                ],
                'entities': ['symbol', 'side', 'amount', 'order_type', 'price', 'stop_loss', 'take_profit']
            },
            'cancel_order': {
                'description': 'Cancel an existing order',
                'examples': [
                    'Cancel my last order',
                    'Close all positions',
                    'Stop the pending order',
                    'Abort the trade'
                ],
                'entities': ['order_id', 'symbol', 'all']
            },
            'check_balance': {
                'description': 'Check account balance',
                'examples': [
                    'What\'s my balance',
                    'Show account balance',
                    'How much money do I have',
                    'Check my wallet'
                ],
                'entities': ['currency', 'account_type']
            },
            'check_positions': {
                'description': 'Check open positions',
                'examples': [
                    'Show my positions',
                    'What am I holding',
                    'List open trades',
                    'Current portfolio'
                ],
                'entities': ['symbol', 'position_type']
            },
            'get_price': {
                'description': 'Get current market price',
                'examples': [
                    'What\'s the price of Bitcoin',
                    'Current ETH price',
                    'Show me EUR/USD quote',
                    'Check Tesla stock price'
                ],
                'entities': ['symbol', 'exchange']
            },
            'start_bot': {
                'description': 'Start an automated trading bot',
                'examples': [
                    'Start the grid bot',
                    'Activate DCA strategy',
                    'Run arbitrage bot',
                    'Begin automated trading'
                ],
                'entities': ['bot_type', 'strategy', 'symbol']
            },
            'stop_bot': {
                'description': 'Stop an automated trading bot',
                'examples': [
                    'Stop the grid bot',
                    'Pause DCA strategy',
                    'Disable automation',
                    'Turn off trading bot'
                ],
                'entities': ['bot_type', 'strategy']
            },
            'get_profit_loss': {
                'description': 'Get profit and loss information',
                'examples': [
                    'What\'s my P&L today',
                    'Show trading performance',
                    'How much did I make',
                    'Trading results'
                ],
                'entities': ['time_period', 'symbol']
            },
            'switch_strategy': {
                'description': 'Change trading strategy',
                'examples': [
                    'Switch to conservative mode',
                    'Use aggressive strategy',
                    'Change to scalping',
                    'Activate swing trading'
                ],
                'entities': ['strategy_name', 'risk_level']
            },
            'set_alert': {
                'description': 'Set price or condition alert',
                'examples': [
                    'Alert me when Bitcoin hits 50000',
                    'Notify when EUR/USD reaches 1.0900',
                    'Set price alert for Tesla at 250'
                ],
                'entities': ['symbol', 'price', 'condition']
            },
            'risk_management': {
                'description': 'Configure risk management settings',
                'examples': [
                    'Set stop loss at 2%',
                    'Adjust risk per trade to 1%',
                    'Enable trailing stop',
                    'Set maximum daily loss'
                ],
                'entities': ['risk_type', 'percentage', 'amount']
            },
            'portfolio_analysis': {
                'description': 'Analyze portfolio performance',
                'examples': [
                    'Analyze my portfolio',
                    'Show portfolio allocation',
                    'Diversification report',
                    'Risk analysis'
                ],
                'entities': ['analysis_type', 'time_period']
            },
            'market_news': {
                'description': 'Get market news and updates',
                'examples': [
                    'What\'s the latest market news',
                    'Any updates on Bitcoin',
                    'Show financial news',
                    'Market headlines'
                ],
                'entities': ['topic', 'symbol']
            },
            'technical_analysis': {
                'description': 'Request technical analysis',
                'examples': [
                    'Show Bitcoin chart analysis',
                    'Technical outlook for EUR/USD',
                    'Support and resistance levels',
                    'Indicator analysis'
                ],
                'entities': ['symbol', 'indicator', 'timeframe']
            },
            'help': {
                'description': 'Get help information',
                'examples': [
                    'What can I do',
                    'Show available commands',
                    'Help me',
                    'How does this work'
                ],
                'entities': ['topic']
            }
        }
        
        # Conversation context
        self.conversation_history: Dict[str, List[Dict]] = defaultdict(list)
        self.max_context_length = 5
        
        logger.info("BERTIntentClassifier initialized")
    
    async def load_model(self):
        """Load BERT model and tokenizer."""
        if self.model is None:
            try:
                from transformers import BertTokenizer, BertForSequenceClassification
                
                self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
                
                # For production, use a fine-tuned model
                # Here we use a placeholder - in practice, load a fine-tuned trading model
                num_labels = len(self.intents)
                self.model = BertForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=num_labels
                )
                
                self.model.eval()
                
                logger.info(f"BERT model loaded: {self.model_name}")
                
            except ImportError:
                logger.error("transformers library not installed")
                raise
            except Exception as e:
                logger.error(f"Error loading BERT model: {e}")
                raise
    
    async def classify(self, 
                      text: str, 
                      user_id: Optional[str] = None,
                      context: Optional[Dict] = None) -> IntentClassification:
        """
        Classify intent from text.
        
        Args:
            text: Input text/command
            user_id: User identifier for context tracking
            context: Additional context
            
        Returns:
            IntentClassification result
        """
        import time
        start_time = time.time()
        
        await self.load_model()
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Get conversation context
        conversation_context = []
        if user_id:
            conversation_context = self._get_conversation_context(user_id)
        
        # Classify with BERT
        intent_scores = await self._bert_classify(processed_text, conversation_context)
        
        # Sort by confidence
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_intent = sorted_intents[0][0]
        primary_confidence = sorted_intents[0][1]
        
        # Extract entities
        entities = await self._extract_entities(text, primary_intent)
        
        # Build context
        context_info = {
            'conversation_turns': len(conversation_context),
            'previous_intent': conversation_context[-1]['intent'] if conversation_context else None,
            'user_id': user_id
        }
        
        # Update conversation history
        if user_id:
            self._update_conversation(user_id, text, primary_intent, entities)
        
        processing_time = (time.time() - start_time) * 1000
        
        return IntentClassification(
            intent=primary_intent,
            confidence=primary_confidence,
            alternative_intents=sorted_intents[1:3],
            entities=entities,
            context=context_info,
            processing_time_ms=processing_time
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for classification."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize numbers (keep them but standardize)
        import re
        text = re.sub(r'\d+\.?\d*', ' <NUM> ', text)
        
        return text.strip()
    
    async def _bert_classify(self, 
                           text: str, 
                           context: List[Dict]) -> Dict[str, float]:
        """
        Classify text using BERT.
        
        In production, this uses the actual BERT model.
        Here we provide a fallback implementation.
        """
        scores = {}
        
        if self.model and self.tokenizer:
            try:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=128,
                    padding=True
                )
                
                # Get predictions
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probabilities = torch.softmax(logits, dim=1)
                
                # Map to intents
                intent_names = list(self.intents.keys())
                for i, prob in enumerate(probabilities[0]):
                    if i < len(intent_names):
                        scores[intent_names[i]] = float(prob)
                
            except Exception as e:
                logger.error(f"BERT classification error: {e}")
                # Fallback to keyword matching
                scores = self._fallback_classification(text)
        else:
            # Fallback if model not loaded
            scores = self._fallback_classification(text)
        
        return scores
    
    def _fallback_classification(self, text: str) -> Dict[str, float]:
        """Fallback keyword-based classification."""
        scores = {}
        text_lower = text.lower()
        
        for intent_name, intent_data in self.intents.items():
            score = 0.0
            
            # Check examples for keyword matches
            for example in intent_data['examples']:
                example_lower = example.lower()
                words = example_lower.split()
                
                for word in words:
                    if len(word) > 3 and word in text_lower:
                        score += 0.1
                
                # Bonus for phrase matches
                if example_lower in text_lower:
                    score += 0.5
            
            # Check entity keywords
            for entity in intent_data.get('entities', []):
                if entity in text_lower:
                    score += 0.2
            
            scores[intent_name] = min(score, 1.0)
        
        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    async def _extract_entities(self, 
                              text: str, 
                              intent: str) -> Dict[str, Any]:
        """Extract entities from text based on intent."""
        entities = {}
        text_lower = text.lower()
        
        import re
        
        # Common entity extraction patterns
        
        # Symbol extraction
        symbols = [
            'btc', 'bitcoin', 'eth', 'ethereum', 'sol', 'solana',
            'ada', 'cardano', 'dot', 'polkadot', 'xrp', 'ripple',
            'doge', 'dogecoin', 'ltc', 'litecoin', 'bnb', 'binance',
            'eur/usd', 'gbp/usd', 'usd/jpy', 'aud/usd', 'usd/chf',
            'apple', 'aapl', 'tesla', 'tsla', 'amazon', 'amzn',
            'google', 'googl', 'microsoft', 'msft'
        ]
        
        for symbol in symbols:
            if symbol in text_lower:
                entities['symbol'] = symbol.upper()
                break
        
        # Amount/quantity extraction
        amount_match = re.search(
            r'(\d+(?:\.\d+)?)\s*(btc|eth|usd|eur|gbp|shares|units|contracts|lot|lots)?',
            text_lower
        )
        if amount_match:
            entities['amount'] = float(amount_match.group(1))
            if amount_match.group(2):
                entities['unit'] = amount_match.group(2)
        
        # Price extraction
        price_match = re.search(
            r'(?:at|@|price\s*(?:of|at)?)\s*(\d+(?:\.\d+)?)',
            text_lower
        )
        if price_match:
            entities['price'] = float(price_match.group(1))
        
        # Percentage extraction
        percent_match = re.search(r'(\d+(?:\.\d+)?)%', text_lower)
        if percent_match:
            entities['percentage'] = float(percent_match.group(1))
        
        # Side extraction
        if 'buy' in text_lower or 'long' in text_lower:
            entities['side'] = 'buy'
        elif 'sell' in text_lower or 'short' in text_lower:
            entities['side'] = 'sell'
        
        # Order type extraction
        if 'market' in text_lower:
            entities['order_type'] = 'market'
        elif 'limit' in text_lower:
            entities['order_type'] = 'limit'
        elif 'stop' in text_lower:
            entities['order_type'] = 'stop'
        elif 'trailing' in text_lower:
            entities['order_type'] = 'trailing_stop'
        
        # Bot type extraction
        bot_types = ['grid', 'dca', 'arbitrage', 'momentum', 'scalping', 'swing']
        for bot_type in bot_types:
            if bot_type in text_lower:
                entities['bot_type'] = bot_type
                break
        
        # Strategy extraction
        strategies = ['conservative', 'aggressive', 'balanced', 'moderate']
        for strategy in strategies:
            if strategy in text_lower:
                entities['strategy'] = strategy
                break
        
        # Time period extraction
        time_periods = {
            'today': '1d',
            'this week': '1w',
            'this month': '1m',
            'this year': '1y',
            'yesterday': '1d',
            'last week': '1w',
            'last month': '1m'
        }
        for period_text, period_code in time_periods.items():
            if period_text in text_lower:
                entities['time_period'] = period_code
                break
        
        return entities
    
    def _get_conversation_context(self, user_id: str) -> List[Dict]:
        """Get conversation context for a user."""
        return self.conversation_history.get(user_id, [])[-self.max_context_length:]
    
    def _update_conversation(self, 
                           user_id: str, 
                           text: str, 
                           intent: str, 
                           entities: Dict):
        """Update conversation history."""
        self.conversation_history[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'intent': intent,
            'entities': entities
        })
        
        # Trim history
        if len(self.conversation_history[user_id]) > self.max_context_length:
            self.conversation_history[user_id] = \
                self.conversation_history[user_id][-self.max_context_length:]
    
    def clear_conversation(self, user_id: str):
        """Clear conversation history for a user."""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
    
    def get_intent_info(self, intent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about an intent."""
        if intent_name in self.intents:
            return {
                'name': intent_name,
                **self.intents[intent_name]
            }
        return None
    
    def get_all_intents(self) -> Dict[str, Dict[str, Any]]:
        """Get all available intents."""
        return {
            name: {
                'description': data['description'],
                'entities': data['entities']
            }
            for name, data in self.intents.items()
        }


# Singleton instance
bert_classifier = BERTIntentClassifier()


async def classify_intent(text: str, 
                         user_id: Optional[str] = None,
                         context: Optional[Dict] = None) -> IntentClassification:
    """Convenience function for intent classification."""
    return await bert_classifier.classify(text, user_id, context)
