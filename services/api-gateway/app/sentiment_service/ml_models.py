"""
ML Models for Sentiment Analysis
Integrates with Hugging Face transformers for financial sentiment
"""

from typing import Dict, Optional, List
import re
from dataclasses import dataclass

@dataclass
class SentimentResult:
    sentiment_score: float  # -1.0 to 1.0
    confidence: float
    label: str
    explanation: str
    key_phrases: List[str]

class SentimentAnalyzer:
    """
    Financial sentiment analysis using ML models
    Falls back to rule-based if models not available
    """
    
    # Financial sentiment keywords
    POSITIVE_KEYWORDS = [
        "bullish", "buy", "strong", "growth", "profit", "gain", "up", "rise",
        "moon", "rocket", "🚀", "💰", "beat", "exceed", "outperform", "upgrade"
    ]
    
    NEGATIVE_KEYWORDS = [
        "bearish", "sell", "weak", "loss", "down", "fall", "drop", "crash",
        "dump", "💩", "miss", "underperform", "downgrade", "debt", "bankruptcy"
    ]
    
    NEUTRAL_INDICATORS = [
        "hold", "neutral", "wait", "watch", "consider", "maybe", "possibly"
    ]
    
    def __init__(self, use_transformers: bool = False):
        self.use_transformers = use_transformers
        self._model = None
        self._tokenizer = None
        
        if use_transformers:
            try:
                self._load_transformer_model()
            except Exception as e:
                print(f"Could not load transformer model: {e}")
                self.use_transformers = False
    
    def _load_transformer_model(self):
        """Load Hugging Face sentiment model"""
        # Would load: rahulholla1/mistral-stock-model or similar
        # from transformers import AutoModelForSequenceClassification, AutoTokenizer
        # self._model = AutoModelForSequenceClassification.from_pretrained("...")
        # self._tokenizer = AutoTokenizer.from_pretrained("...")
        pass
    
    async def analyze(self, text: str, ticker: Optional[str] = None) -> Dict:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Text to analyze
            ticker: Optional ticker symbol for context
        
        Returns:
            Sentiment analysis result
        """
        if self.use_transformers and self._model:
            return await self._analyze_with_model(text, ticker)
        else:
            return self._analyze_rule_based(text, ticker)
    
    async def _analyze_with_model(self, text: str, ticker: Optional[str]) -> Dict:
        """Analyze using transformer model"""
        # Placeholder - would use actual model inference
        # inputs = self._tokenizer(text, return_tensors="pt")
        # outputs = self._model(**inputs)
        # sentiment = outputs.logits.softmax(dim=-1)
        
        return {
            "sentiment_score": 0.5,
            "confidence": 0.85,
            "label": "positive",
            "explanation": "Model-based analysis",
            "key_phrases": ["strong growth"],
            "model_used": "transformer"
        }
    
    def _analyze_rule_based(self, text: str, ticker: Optional[str]) -> Dict:
        """Rule-based sentiment analysis (fallback)"""
        text_lower = text.lower()
        
        # Count keyword occurrences
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        neutral_count = sum(1 for word in self.NEUTRAL_INDICATORS if word in text_lower)
        
        # Calculate raw sentiment score
        total_indicators = positive_count + negative_count + neutral_count
        
        if total_indicators == 0:
            sentiment_score = 0.0
            confidence = 0.3
            label = "neutral"
        else:
            # Weighted calculation
            sentiment_score = (positive_count - negative_count) / max(total_indicators, 3)
            
            # Normalize to -1 to 1
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            # Calculate confidence based on indicator strength
            confidence = min(0.95, 0.4 + (total_indicators * 0.1))
            
            # Determine label
            if sentiment_score > 0.1:
                label = "positive"
            elif sentiment_score < -0.1:
                label = "negative"
            else:
                label = "neutral"
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)
        
        # Generate explanation
        explanation = self._generate_explanation(sentiment_score, label, key_phrases)
        
        return {
            "sentiment_score": round(sentiment_score, 3),
            "confidence": round(confidence, 3),
            "label": label,
            "explanation": explanation,
            "key_phrases": key_phrases,
            "model_used": "rule_based",
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key financial phrases from text"""
        phrases = []
        
        # Pattern for dollar amounts
        dollar_pattern = re.findall(r'\$[\d,]+\.?\d*', text)
        phrases.extend(dollar_pattern[:3])
        
        # Pattern for percentages
        percent_pattern = re.findall(r'\d+\.?\d*%', text)
        phrases.extend(percent_pattern[:2])
        
        # Pattern for ticker mentions
        ticker_pattern = re.findall(r'\$[A-Z]{1,5}', text)
        phrases.extend(ticker_pattern[:3])
        
        return phrases
    
    def _generate_explanation(
        self,
        sentiment_score: float,
        label: str,
        key_phrases: List[str]
    ) -> str:
        """Generate human-readable explanation"""
        
        if label == "positive":
            strength = "strongly" if sentiment_score > 0.5 else "moderately"
            return f"Text is {strength} positive. Key indicators: {', '.join(key_phrases[:3])}"
        elif label == "negative":
            strength = "strongly" if sentiment_score < -0.5 else "moderately"
            return f"Text is {strength} negative. Key indicators: {', '.join(key_phrases[:3])}"
        else:
            return f"Text is neutral with mixed signals. Key terms: {', '.join(key_phrases[:3])}"
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts"""
        return [self._analyze_rule_based(text, None) for text in texts]
