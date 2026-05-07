"""
Advanced AI/ML with Transformer Models
=====================================
Enterprise-grade transformer models for Financial Master
"""

import asyncio
import torch
import torch.nn as nn
from torch.nn import functional as F
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    AutoModelForTokenClassification, AutoModelForQuestionAnswering,
    BertTokenizer, BertModel, GPT2LMHeadModel, GPT2Tokenizer,
    T5ForConditionalGeneration, T5Tokenizer
)
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for transformer models"""
    model_name: str
    model_type: str  # bert, gpt2, t5, custom
    task_type: str  # classification, generation, qa, ner
    max_length: int
    batch_size: int
    learning_rate: float
    num_epochs: int
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class FinancialBERT(nn.Module):
    """BERT-based model for financial text analysis"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        
        # Financial-specific layers
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(768, 5)  # 5 sentiment classes
        self.financial_entity_classifier = nn.Linear(768, 10)  # 10 entity types
        self.market_sentiment_classifier = nn.Linear(768, 3)  # bullish/bearish/neutral
        
    def forward(self, input_ids, attention_mask=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        
        # Classification heads
        sentiment_logits = self.classifier(self.dropout(pooled_output))
        entity_logits = self.financial_entity_classifier(self.dropout(pooled_output))
        market_sentiment_logits = self.market_sentiment_classifier(self.dropout(pooled_output))
        
        return {
            'sentiment': sentiment_logits,
            'entities': entity_logits,
            'market_sentiment': market_sentiment_logits
        }


class FinancialGPT2(nn.Module):
    """GPT-2 based model for financial text generation"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        
        # Add special tokens for financial domain
        self.tokenizer.add_special_tokens({
            'additional_special_tokens': ['[STOCK]', '[PRICE]', '[VOLUME]', '[TREND]']
        })
        self.model.resize_token_embeddings(len(self.tokenizer))
        
    def generate_financial_report(self, prompt: str, max_length: int = 500):
        """Generate financial report from prompt"""
        inputs = self.tokenizer.encode(prompt, return_tensors='pt')
        outputs = self.model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            pad_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def generate_trading_signals(self, market_data: Dict[str, Any]):
        """Generate trading signals from market data"""
        prompt = f"Market Analysis: {json.dumps(market_data)}\nTrading Signal:"
        return self.generate_financial_report(prompt, max_length=200)


class FinancialT5(nn.Module):
    """T5-based model for financial question answering and summarization"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base')
        
    def summarize_financial_text(self, text: str, max_length: int = 150):
        """Summarize financial text"""
        inputs = self.tokenizer.encode(
            f"summarize: {text}",
            return_tensors='pt',
            max_length=self.config.max_length,
            truncation=True
        )
        
        outputs = self.model.generate(
            inputs,
            max_length=max_length,
            num_beams=4,
            early_stopping=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def answer_financial_question(self, question: str, context: str):
        """Answer financial questions"""
        input_text = f"question: {question} context: {context}"
        inputs = self.tokenizer.encode(
            input_text,
            return_tensors='pt',
            max_length=self.config.max_length,
            truncation=True
        )
        
        outputs = self.model.generate(
            inputs,
            max_length=100,
            num_beams=4,
            early_stopping=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class TransformerModelManager:
    """Manager for transformer models in Financial Master"""
    
    def __init__(self):
        self.models: Dict[str, nn.Module] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize default models
        self._initialize_default_models()
        
    def _initialize_default_models(self):
        """Initialize default transformer models"""
        # Financial Sentiment Analysis Model
        sentiment_config = ModelConfig(
            model_name="financial-bert-sentiment",
            model_type="bert",
            task_type="classification",
            max_length=512,
            batch_size=16,
            learning_rate=2e-5,
            num_epochs=3
        )
        
        # Financial Report Generation Model
        generation_config = ModelConfig(
            model_name="financial-gpt2-generation",
            model_type="gpt2",
            task_type="generation",
            max_length=1024,
            batch_size=8,
            learning_rate=5e-5,
            num_epochs=5
        )
        
        # Financial QA Model
        qa_config = ModelConfig(
            model_name="financial-t5-qa",
            model_type="t5",
            task_type="qa",
            max_length=512,
            batch_size=8,
            learning_rate=3e-5,
            num_epochs=4
        )
        
        self.model_configs["sentiment"] = sentiment_config
        self.model_configs["generation"] = generation_config
        self.model_configs["qa"] = qa_config
        
        # Load models (in production, would load pre-trained models)
        try:
            self.models["sentiment"] = FinancialBERT(sentiment_config).to(self.device)
            self.models["generation"] = FinancialGPT2(generation_config).to(self.device)
            self.models["qa"] = FinancialT5(qa_config).to(self.device)
            
            # Set to evaluation mode
            for model in self.models.values():
                model.eval()
                
        except Exception as e:
            logger.error(f"Error loading transformer models: {e}")
            
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of financial text"""
        try:
            model = self.models.get("sentiment")
            if not model:
                return {"error": "Sentiment model not available"}
                
            tokenizer = model.tokenizer
            inputs = tokenizer(
                text,
                return_tensors="pt",
                max_length=model.config.max_length,
                truncation=True,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                
            # Process outputs
            sentiment_probs = F.softmax(outputs['sentiment'], dim=-1)
            entity_probs = F.softmax(outputs['entities'], dim=-1)
            market_sentiment_probs = F.softmax(outputs['market_sentiment'], dim=-1)
            
            return {
                "sentiment": {
                    "positive": sentiment_probs[0][0].item(),
                    "negative": sentiment_probs[0][1].item(),
                    "neutral": sentiment_probs[0][2].item(),
                    "bullish": sentiment_probs[0][3].item(),
                    "bearish": sentiment_probs[0][4].item()
                },
                "entities": {
                    "stock": entity_probs[0][0].item(),
                    "price": entity_probs[0][1].item(),
                    "volume": entity_probs[0][2].item(),
                    "trend": entity_probs[0][3].item()
                },
                "market_sentiment": {
                    "bullish": market_sentiment_probs[0][0].item(),
                    "bearish": market_sentiment_probs[0][1].item(),
                    "neutral": market_sentiment_probs[0][2].item()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"error": str(e)}
            
    async def generate_financial_report(self, data: Dict[str, Any]) -> str:
        """Generate financial report"""
        try:
            model = self.models.get("generation")
            if not model:
                return "Report generation model not available"
                
            # Create prompt from data
            prompt = self._create_report_prompt(data)
            
            with torch.no_grad():
                report = model.generate_financial_report(prompt)
                
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial report: {e}")
            return f"Error generating report: {str(e)}"
            
    def _create_report_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for report generation"""
        prompt = "Financial Analysis Report:\n\n"
        
        if "portfolio" in data:
            portfolio = data["portfolio"]
            prompt += f"Portfolio Value: ${portfolio.get('value', 0):,.2f}\n"
            prompt += f"Daily Change: {portfolio.get('change', 0):+.2f}%\n"
            prompt += f"Holdings: {len(portfolio.get('holdings', []))}\n\n"
            
        if "market" in data:
            market = data["market"]
            prompt += "Market Conditions:\n"
            for symbol, info in market.items():
                prompt += f"{symbol}: ${info.get('price', 0):.2f} ({info.get('change', 0):+.2f}%)\n"
            prompt += "\n"
            
        if "news" in data:
            news = data["news"]
            prompt += "Recent News:\n"
            for article in news[:3]:
                prompt += f"- {article.get('headline', '')}\n"
            prompt += "\n"
            
        prompt += "Analysis and Recommendations:\n"
        
        return prompt
        
    async def answer_financial_question(self, question: str, context: str = "") -> str:
        """Answer financial questions"""
        try:
            model = self.models.get("qa")
            if not model:
                return "QA model not available"
                
            with torch.no_grad():
                answer = model.answer_financial_question(question, context)
                
            return answer
            
        except Exception as e:
            logger.error(f"Error answering financial question: {e}")
            return f"Error answering question: {str(e)}"
            
    async def summarize_financial_document(self, text: str) -> str:
        """Summarize financial documents"""
        try:
            model = self.models.get("qa")
            if not model:
                return "Summarization model not available"
                
            with torch.no_grad():
                summary = model.summarize_financial_text(text)
                
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing document: {e}")
            return f"Error summarizing: {str(e)}"
            
    async def extract_financial_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial entities from text"""
        try:
            model = self.models.get("sentiment")
            if not model:
                return []
                
            tokenizer = model.tokenizer
            inputs = tokenizer(
                text,
                return_tensors="pt",
                max_length=model.config.max_length,
                truncation=True,
                padding=True,
                return_offsets_mapping=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items() if k != 'offset_mapping'}
            
            with torch.no_grad():
                outputs = model(**inputs)
                entity_probs = F.softmax(outputs['entities'], dim=-1)
                
            # Extract entities (simplified)
            entities = []
            entity_types = ["stock", "price", "volume", "trend", "company", "currency"]
            
            for i, probs in enumerate(entity_probs[0]):
                max_prob, max_idx = torch.max(probs, dim=0)
                if max_prob > 0.5 and max_idx < len(entity_types):
                    entities.append({
                        "type": entity_types[max_idx.item()],
                        "confidence": max_prob.item(),
                        "position": i
                    })
                    
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
            
    async def predict_market_movement(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict market movement using transformer models"""
        try:
            # Combine market data into text
            market_text = " ".join([
                f"{data.get('symbol', '')} {data.get('price', 0)} {data.get('volume', 0)} {data.get('change', 0)}"
                for data in market_data
            ])
            
            # Analyze sentiment
            sentiment_result = await self.analyze_sentiment(market_text)
            
            # Generate prediction based on sentiment
            market_sentiment = sentiment_result.get("market_sentiment", {})
            bullish_confidence = market_sentiment.get("bullish", 0)
            bearish_confidence = market_sentiment.get("bearish", 0)
            
            prediction = "neutral"
            confidence = 0.5
            
            if bullish_confidence > bearish_confidence and bullish_confidence > 0.6:
                prediction = "bullish"
                confidence = bullish_confidence
            elif bearish_confidence > bullish_confidence and bearish_confidence > 0.6:
                prediction = "bearish"
                confidence = bearish_confidence
                
            return {
                "prediction": prediction,
                "confidence": confidence,
                "bullish_confidence": bullish_confidence,
                "bearish_confidence": bearish_confidence,
                "neutral_confidence": market_sentiment.get("neutral", 0)
            }
            
        except Exception as e:
            logger.error(f"Error predicting market movement: {e}")
            return {"error": str(e)}
            
    async def generate_trading_signals(self, portfolio_data: Dict[str, Any], 
                                     market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals using transformer models"""
        try:
            model = self.models.get("generation")
            if not model:
                return []
                
            # Combine portfolio and market data
            combined_data = {
                "portfolio": portfolio_data,
                "market": market_data
            }
            
            # Generate signals
            signals_text = model.generate_trading_signals(combined_data)
            
            # Parse signals (simplified)
            signals = []
            signal_lines = signals_text.split('\n')
            
            for line in signal_lines:
                if 'BUY' in line:
                    symbol = line.split('BUY')[1].strip().split()[0]
                    signals.append({
                        "action": "BUY",
                        "symbol": symbol,
                        "confidence": 0.75,
                        "reason": "AI-generated buy signal"
                    })
                elif 'SELL' in line:
                    symbol = line.split('SELL')[1].strip().split()[0]
                    signals.append({
                        "action": "SELL",
                        "symbol": symbol,
                        "confidence": 0.75,
                        "reason": "AI-generated sell signal"
                    })
                    
            return signals[:5]  # Return top 5 signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return []
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "device": str(self.device),
            "models": {
                name: {
                    "type": config.model_type,
                    "task": config.task_type,
                    "max_length": config.max_length,
                    "parameters": sum(p.numel() for p in model.parameters())
                }
                for name, (model, config) in zip(self.models.keys(), 
                                                [(self.models[k], self.model_configs[k]) for k in self.models.keys()])
            }
        }


# Global transformer model manager instance
_transformer_manager = None

def get_transformer_manager() -> TransformerModelManager:
    """Get the global transformer model manager instance"""
    global _transformer_manager
    if _transformer_manager is None:
        _transformer_manager = TransformerModelManager()
    return _transformer_manager
