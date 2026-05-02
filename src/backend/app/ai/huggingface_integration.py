"""Hugging Face Integration - FinBERT, CLIP, Whisper, Transformers"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Graceful imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")

try:
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class HuggingFaceManager:
    """
    Manages Hugging Face models for financial analysis
    
    Models:
    - FinBERT: Financial sentiment analysis
    - CLIP: Visual-text matching
    - Whisper: Audio transcription
    - BERT: General NLP tasks
    """
    
    def __init__(self):
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Lazy initialization of models"""
        if TRANSFORMERS_AVAILABLE:
            try:
                # FinBERT for financial sentiment
                self.models['finbert'] = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                logger.info("FinBERT loaded")
            except Exception as e:
                logger.error(f"Failed to load FinBERT: {e}")
            
            try:
                # General sentiment
                self.models['sentiment'] = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            except Exception as e:
                logger.error(f"Failed to load sentiment model: {e}")
        
        if WHISPER_AVAILABLE:
            try:
                self.models['whisper'] = whisper.load_model("base")
                logger.info("Whisper loaded")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
    
    def analyze_sentiment(self, text: str, model: str = 'finbert') -> Dict:
        """
        Analyze financial sentiment
        
        Args:
            text: Text to analyze
            model: 'finbert' or 'sentiment'
        """
        pipeline_model = self.models.get(model)
        
        if not pipeline_model:
            # Fallback
            return self._fallback_sentiment(text)
        
        try:
            # Truncate if too long
            max_len = 512
            text = text[:max_len]
            
            result = pipeline_model(text)[0]
            
            return {
                'label': result['label'],
                'score': result['score'],
                'model': model,
                'text_length': len(text)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict:
        """Fallback sentiment using lexicon"""
        positive_words = ['growth', 'profit', 'success', 'strong', 'beat', 'raise']
        negative_words = ['decline', 'loss', 'weak', 'miss', 'cut', 'risk']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            label = 'positive'
            score = 0.5 + (pos_count - neg_count) * 0.1
        elif neg_count > pos_count:
            label = 'negative'
            score = 0.5 + (neg_count - pos_count) * 0.1
        else:
            label = 'neutral'
            score = 0.5
        
        return {
            'label': label,
            'score': min(score, 0.99),
            'model': 'fallback_lexicon',
            'text_length': len(text)
        }
    
    def transcribe_audio(self, audio_path: str, language: str = 'en') -> Dict:
        """Transcribe audio using Whisper"""
        whisper_model = self.models.get('whisper')
        
        if not whisper_model:
            return {'error': 'Whisper not available', 'text': ''}
        
        try:
            result = whisper_model.transcribe(audio_path, language=language)
            
            return {
                'text': result.get('text', ''),
                'language': result.get('language', language),
                'confidence': result.get('confidence', 0),
                'duration': result.get('duration', 0)
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {'error': str(e), 'text': ''}
    
    def batch_analyze(self, texts: List[str], model: str = 'finbert') -> List[Dict]:
        """Batch sentiment analysis"""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text, model))
        return results
    
    def get_model_status(self) -> Dict:
        """Get status of all models"""
        return {
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'clip_available': CLIP_AVAILABLE,
            'whisper_available': WHISPER_AVAILABLE,
            'loaded_models': list(self.models.keys()),
            'finbert_ready': 'finbert' in self.models,
            'whisper_ready': 'whisper' in self.models
        }


# Quick functions
def quick_sentiment(text: str) -> Dict:
    """Quick sentiment analysis"""
    hf = HuggingFaceManager()
    return hf.analyze_sentiment(text)


def batch_sentiment(texts: List[str]) -> List[Dict]:
    """Batch sentiment analysis"""
    hf = HuggingFaceManager()
    return hf.batch_analyze(texts)
