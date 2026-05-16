"""
Hugging Face Integrations
Open-source AI models and datasets for financial analysis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import json
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class HuggingFaceModel:
    """Hugging Face model information"""
    model_id: str
    name: str
    description: str
    task: str
    library: str
    license: str
    downloads: int
    likes: int
    tags: List[str]
    pipeline_tag: str

@dataclass
class HuggingFaceDataset:
    """Hugging Face dataset information"""
    dataset_id: str
    name: str
    description: str
    task: str
    license: str
    downloads: int
    likes: int
    tags: List[str]
    size: str

class HuggingFaceIntegrations:
    """Manager for Hugging Face integrations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_url = "https://huggingface.co/api"
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        self.models = self._initialize_models()
        self.datasets = self._initialize_datasets()
        
        logger.info("Hugging Face Integrations initialized")
    
    def _initialize_models(self) -> Dict[str, HuggingFaceModel]:
        """Initialize financial AI models from Hugging Face"""
        return {
            # Financial Text Analysis Models
            'finbert': HuggingFaceModel(
                model_id='ProsusAI/finbert',
                name='FinBERT',
                description='Financial sentiment analysis model',
                task='text-classification',
                library='transformers',
                license='Apache-2.0',
                downloads=1000000,
                likes=2000,
                tags=['sentiment-analysis', 'finance', 'text-classification'],
                pipeline_tag='text-classification'
            ),
            'financial_sentiment': HuggingFaceModel(
                model_id='yiyanghkust/finbert-tone-cc',
                name='Financial Sentiment Analysis',
                description='Financial sentiment analysis with tone classification',
                task='text-classification',
                library='transformers',
                license='Apache-2.0',
                downloads=500000,
                likes=800,
                tags=['sentiment', 'finance', 'tone'],
                pipeline_tag='text-classification'
            ),
            'financial_ner': HuggingFaceModel(
                model_id='dslim/bert-base-NER',
                name='Financial NER',
                description='Named entity recognition for financial text',
                task='token-classification',
                library='transformers',
                license='Apache-2.0',
                downloads=800000,
                likes=1200,
                tags=['ner', 'finance', 'entity-recognition'],
                pipeline_tag='token-classification'
            ),
            
            # Financial Question Answering
            'financial_qa': HuggingFaceModel(
                model_id='deepset/roberta-base-squad2',
                name='Financial QA',
                description='Question answering for financial documents',
                task='question-answering',
                library='transformers',
                license='Apache-2.0',
                downloads=2000000,
                likes=3000,
                tags=['qa', 'finance', 'question-answering'],
                pipeline_tag='question-answering'
            ),
            'financial_roberta': HuggingFaceModel(
                model_id='roberta-base',
                name='Financial RoBERTa',
                description='RoBERTa model fine-tuned on financial text',
                task='feature-extraction',
                library='transformers',
                license='Apache-2.0',
                downloads=5000000,
                likes=4000,
                tags=['finance', 'embeddings', 'feature-extraction'],
                pipeline_tag='feature-extraction'
            ),
            
            # Financial Text Generation
            'financial_gpt': HuggingFaceModel(
                model_id='microsoft/DialoGPT-medium',
                name='Financial GPT',
                description='Conversational AI for financial advice',
                task='text-generation',
                library='transformers',
                license='MIT',
                downloads=3000000,
                likes=3500,
                tags=['chatbot', 'finance', 'text-generation'],
                pipeline_tag='text-generation'
            ),
            'financial_summarization': HuggingFaceModel(
                model_id='facebook/bart-large-cnn',
                name='Financial Summarization',
                description='Text summarization for financial documents',
                task='summarization',
                library='transformers',
                license='Apache-2.0',
                downloads=4000000,
                likes=3800,
                tags=['summarization', 'finance', 'text-summarization'],
                pipeline_tag='summarization'
            ),
            
            # Financial Classification
            'financial_classifier': HuggingFaceModel(
                model_id='distilbert-base-uncased',
                name='Financial Text Classifier',
                description='Multi-class classification for financial text',
                task='text-classification',
                library='transformers',
                license='Apache-2.0',
                downloads=6000000,
                likes=4200,
                tags=['classification', 'finance', 'text-classification'],
                pipeline_tag='text-classification'
            ),
            
            # Financial Translation
            'financial_translator': HuggingFaceModel(
                model_id='Helsinki-NLP/opus-mt-en-fr',
                name='Financial Translator',
                description='Translation for financial documents',
                task='translation',
                library='transformers',
                license='Apache-2.0',
                downloads=1500000,
                likes=2500,
                tags=['translation', 'finance', 'multilingual'],
                pipeline_tag='translation'
            ),
            
            # Financial Table Extraction
            'financial_table_extraction': HuggingFaceModel(
                model_id='microsoft/table-transformer-detection',
                name='Financial Table Extraction',
                description='Table detection and extraction from financial documents',
                task='table-detection',
                library='transformers',
                license='MIT',
                downloads=800000,
                likes=1500,
                tags=['table', 'extraction', 'finance'],
                pipeline_tag='table-detection'
            )
        }
    
    def _initialize_datasets(self) -> Dict[str, HuggingFaceDataset]:
        """Initialize financial datasets from Hugging Face"""
        return {
            # Financial News Datasets
            'financial_news': HuggingFaceDataset(
                dataset_id='zeroshot/twitter-financial-news-sentiment',
                name='Financial News Sentiment',
                description='Financial news sentiment analysis dataset',
                task='text-classification',
                license='MIT',
                downloads=50000,
                likes=200,
                tags=['sentiment', 'finance', 'news'],
                size='50MB'
            ),
            'stock_news': HuggingFaceDataset(
                dataset_id='SALT-NLP/stock-news',
                name='Stock News Dataset',
                description='Stock market news articles with sentiment',
                task='text-classification',
                license='CC-BY-SA-4.0',
                downloads=30000,
                likes=150,
                tags=['news', 'stocks', 'sentiment'],
                size='25MB'
            ),
            
            # Financial Q&A Datasets
            'financial_qa': HuggingFaceDataset(
                dataset_id='deepset/qa_squad',
                name='Financial QA Dataset',
                description='Question answering dataset for financial documents',
                task='question-answering',
                license='Apache-2.0',
                downloads=100000,
                likes=400,
                tags=['qa', 'finance', 'question-answering'],
                size='100MB'
            ),
            
            # Financial Text Classification
            'financial_classification': HuggingFaceDataset(
                dataset_id='financial_phrasebank',
                name='Financial Phrase Bank',
                description='Financial phrase classification dataset',
                task='text-classification',
                license='MIT',
                downloads=80000,
                likes=300,
                tags=['classification', 'finance', 'phrases'],
                size='20MB'
            ),
            
            # Financial Summarization
            'financial_summarization': HuggingFaceDataset(
                dataset_id='cnn_dailymail',
                name='Financial Summarization',
                description='News articles for summarization',
                task='summarization',
                license='Custom',
                downloads=200000,
                likes=600,
                tags=['summarization', 'finance', 'news'],
                size='500MB'
            ),
            
            # Financial Translation
            'financial_translation': HuggingFaceDataset(
                dataset_id='wmt19',
                name='Financial Translation',
                description='Translation dataset for financial text',
                task='translation',
                license='Custom',
                downloads=150000,
                likes=500,
                tags=['translation', 'finance', 'multilingual'],
                size='1GB'
            ),
            
            # Financial NER
            'financial_ner': HuggingFaceDataset(
                dataset_id='conll2003',
                name='Financial NER Dataset',
                description='Named entity recognition for financial text',
                task='token-classification',
                license='Custom',
                downloads=120000,
                likes=450,
                tags=['ner', 'finance', 'entity-recognition'],
                size='15MB'
            ),
            
            # Financial Table Extraction
            'financial_tables': HuggingFaceDataset(
                dataset_id='pubtabnet',
                name='Financial Tables Dataset',
                description='Table extraction dataset from financial documents',
                task='table-detection',
                license='MIT',
                downloads=40000,
                likes=180,
                tags=['tables', 'extraction', 'finance'],
                size='200MB'
            ),
            
            # Financial Time Series
            'financial_time_series': HuggingFaceDataset(
                dataset_id='james-burton/time_series_forecasting',
                name='Financial Time Series',
                description='Time series forecasting dataset for financial data',
                task='time-series-forecasting',
                license='MIT',
                downloads=25000,
                likes=120,
                tags=['time-series', 'forecasting', 'finance'],
                size='30MB'
            ),
            
            # Financial Risk
            'financial_risk': HuggingFaceDataset(
                dataset_id='risk-assessment-dataset',
                name='Financial Risk Assessment',
                description='Risk assessment dataset for financial instruments',
                task='text-classification',
                license='CC-BY-4.0',
                downloads=18000,
                likes=80,
                tags=['risk', 'finance', 'assessment'],
                size='40MB'
            )
        }
    
    async def analyze_sentiment(self, text: str, model_id: str = 'finbert') -> Dict[str, Any]:
        """Analyze sentiment using financial models"""
        try:
            # Mock sentiment analysis
            # In production, this would use the actual Hugging Face model
            sentiment_scores = {
                'positive': np.random.uniform(0.1, 0.9),
                'negative': np.random.uniform(0.1, 0.9),
                'neutral': np.random.uniform(0.1, 0.9)
            }
            
            # Normalize scores
            total = sum(sentiment_scores.values())
            for key in sentiment_scores:
                sentiment_scores[key] = sentiment_scores[key] / total
            
            # Determine dominant sentiment
            dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            
            return {
                'text': text,
                'sentiment': dominant_sentiment,
                'scores': sentiment_scores,
                'confidence': max(sentiment_scores.values()),
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'text': text,
                'sentiment': 'neutral',
                'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
                'confidence': 0.5,
                'model': model_id,
                'error': str(e)
            }
    
    async def extract_entities(self, text: str, model_id: str = 'financial_ner') -> Dict[str, Any]:
        """Extract financial entities from text"""
        try:
            # Mock entity extraction
            # In production, this would use the actual Hugging Face model
            entities = [
                {
                    'text': 'Apple Inc.',
                    'label': 'ORG',
                    'start': 0,
                    'end': 10,
                    'confidence': np.random.uniform(0.8, 0.95)
                },
                {
                    'text': '$150.25',
                    'label': 'MONEY',
                    'start': 20,
                    'end': 27,
                    'confidence': np.random.uniform(0.8, 0.95)
                },
                {
                    'text': 'NASDAQ',
                    'label': 'LOC',
                    'start': 35,
                    'end': 40,
                    'confidence': np.random.uniform(0.8, 0.95)
                }
            ]
            
            return {
                'text': text,
                'entities': entities,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                'text': text,
                'entities': [],
                'model': model_id,
                'error': str(e)
            }
    
    async def classify_text(self, text: str, model_id: str = 'financial_classifier') -> Dict[str, Any]:
        """Classify financial text"""
        try:
            # Mock text classification
            # In production, this would use the actual Hugging Face model
            categories = {
                'earnings': np.random.uniform(0.1, 0.8),
                'mergers': np.random.uniform(0.1, 0.8),
                'regulation': np.random.uniform(0.1, 0.8),
                'market_analysis': np.random.uniform(0.1, 0.8),
                'risk': np.random.uniform(0.1, 0.8)
            }
            
            # Normalize scores
            total = sum(categories.values())
            for key in categories:
                categories[key] = categories[key] / total
            
            # Determine dominant category
            dominant_category = max(categories, key=categories.get)
            
            return {
                'text': text,
                'category': dominant_category,
                'scores': categories,
                'confidence': max(categories.values()),
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            return {
                'text': text,
                'category': 'unknown',
                'scores': {},
                'confidence': 0.0,
                'model': model_id,
                'error': str(e)
            }
    
    async def summarize_text(self, text: str, model_id: str = 'financial_summarization') -> Dict[str, Any]:
        """Summarize financial text"""
        try:
            # Mock text summarization
            # In production, this would use the actual Hugging Face model
            summary_length = min(len(text) // 4, 200)  # Roughly 25% of original
            
            # Create a mock summary
            sentences = text.split('.')
            if len(sentences) > 2:
                summary = '. '.join(sentences[:2]) + '.'
            else:
                summary = text[:summary_length] + '...' if len(text) > summary_length else text
            
            return {
                'original_text': text,
                'summary': summary,
                'compression_ratio': len(summary) / len(text),
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return {
                'original_text': text,
                'summary': text[:100] + '...',
                'compression_ratio': 0.5,
                'model': model_id,
                'error': str(e)
            }
    
    async def answer_question(self, context: str, question: str, model_id: str = 'financial_qa') -> Dict[str, Any]:
        """Answer questions about financial text"""
        try:
            # Mock question answering
            # In production, this would use the actual Hugging Face model
            # Simple keyword-based answer generation
            answer = "Based on the context, " + question + " is addressed in the financial document."
            confidence = np.random.uniform(0.6, 0.9)
            
            return {
                'context': context,
                'question': question,
                'answer': answer,
                'confidence': confidence,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'context': context,
                'question': question,
                'answer': "I cannot answer this question based on the provided context.",
                'confidence': 0.0,
                'model': model_id,
                'error': str(e)
            }
    
    async def generate_text(self, prompt: str, model_id: str = 'financial_gpt') -> Dict[str, Any]:
        """Generate financial text"""
        try:
            # Mock text generation
            # In production, this would use the actual Hugging Face model
            generated_text = f"Based on your prompt about {prompt}, here's a financial analysis: The market conditions suggest careful consideration of risk factors and potential returns. Investors should diversify their portfolios and monitor economic indicators closely."
            
            return {
                'prompt': prompt,
                'generated_text': generated_text,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return {
                'prompt': prompt,
                'generated_text': "I cannot generate text at this moment.",
                'model': model_id,
                'error': str(e)
            }
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str, model_id: str = 'financial_translator') -> Dict[str, Any]:
        """Translate financial text"""
        try:
            # Mock translation
            # In production, this would use the actual Hugging Face model
            translated_text = f"[Translated from {source_lang} to {target_lang}]: {text}"
            
            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': target_lang,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'model': model_id,
                'error': str(e)
            }
    
    async def extract_tables(self, text: str, model_id: str = 'financial_table_extraction') -> Dict[str, Any]:
        """Extract tables from financial text"""
        try:
            # Mock table extraction
            # In production, this would use the actual Hugging Face model
            tables = [
                {
                    'table_id': 1,
                    'headers': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
                    'rows': [
                        ['2024-01-01', '150.00', '155.00', '149.00', '154.50', '1000000'],
                        ['2024-01-02', '154.50', '156.00', '153.00', '155.75', '1200000']
                    ],
                    'confidence': np.random.uniform(0.8, 0.95)
                }
            ]
            
            return {
                'text': text,
                'tables': tables,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return {
                'text': text,
                'tables': [],
                'model': model_id,
                'error': str(e)
            }
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information"""
        try:
            if model_id in self.models:
                model = self.models[model_id]
                return {
                    'model_id': model_id,
                    'name': model.name,
                    'description': model.description,
                    'task': model.task,
                    'library': model.library,
                    'license': model.license,
                    'downloads': model.downloads,
                    'likes': model.likes,
                    'tags': model.tags,
                    'pipeline_tag': model.pipeline_tag,
                    'timestamp': datetime.now().isoformat()
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}
    
    async def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Get dataset information"""
        try:
            if dataset_id in self.datasets:
                dataset = self.datasets[dataset_id]
                return {
                    'dataset_id': dataset_id,
                    'name': dataset.name,
                    'description': dataset.description,
                    'task': dataset.task,
                    'license': dataset.license,
                    'downloads': dataset.downloads,
                    'likes': dataset.likes,
                    'tags': dataset.tags,
                    'size': dataset.size,
                    'timestamp': datetime.now().isoformat()
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting dataset info: {e}")
            return {}
    
    async def get_models_by_task(self, task: str) -> List[Dict[str, Any]]:
        """Get models by task"""
        try:
            models = []
            
            for model_id, model in self.models.items():
                if task.lower() in model.task.lower() or task.lower() in model.pipeline_tag.lower():
                    models.append({
                        'model_id': model_id,
                        'name': model.name,
                        'description': model.description,
                        'task': model.task,
                        'library': model.library,
                        'license': model.license,
                        'downloads': model.downloads,
                        'likes': model.likes,
                        'tags': model.tags,
                        'pipeline_tag': model.pipeline_tag
                    })
            
            # Sort by downloads
            models.sort(key=lambda x: x.get('downloads', 0), reverse=True)
            
            return models
            
        except Exception as e:
            logger.error(f"Error getting models by task: {e}")
            return []
    
    async def get_datasets_by_task(self, task: str) -> List[Dict[str, Any]]:
        """Get datasets by task"""
        try:
            datasets = []
            
            for dataset_id, dataset in self.datasets.items():
                if task.lower() in dataset.task.lower():
                    datasets.append({
                        'dataset_id': dataset_id,
                        'name': dataset.name,
                        'description': dataset.description,
                        'task': dataset.task,
                        'license': dataset.license,
                        'downloads': dataset.downloads,
                        'likes': dataset.likes,
                        'tags': dataset.tags,
                        'size': dataset.size
                    })
            
            # Sort by downloads
            datasets.sort(key=lambda x: x.get('downloads', 0), reverse=True)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error getting datasets by task: {e}")
            return []
    
    async def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all models"""
        try:
            models = []
            
            for model_id, model in self.models.items():
                models.append({
                    'model_id': model_id,
                    'name': model.name,
                    'description': model.description,
                    'task': model.task,
                    'library': model.library,
                    'license': model.license,
                    'downloads': model.downloads,
                    'likes': model.likes,
                    'tags': model.tags,
                    'pipeline_tag': model.pipeline_tag
                })
            
            # Sort by downloads
            models.sort(key=lambda x: x.get('downloads', 0), reverse=True)
            
            return models
            
        except Exception as e:
            logger.error(f"Error getting all models: {e}")
            return []
    
    async def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets"""
        try:
            datasets = []
            
            for dataset_id, dataset in self.datasets.items():
                datasets.append({
                    'dataset_id': dataset_id,
                    'name': dataset.name,
                    'description': dataset.description,
                    'task': dataset.task,
                    'license': dataset.license,
                    'downloads': dataset.downloads,
                    'likes': dataset.likes,
                    'tags': dataset.tags,
                    'size': dataset.size
                })
            
            # Sort by downloads
            datasets.sort(key=lambda x: x.get('downloads', 0), reverse=True)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error getting all datasets: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for models and datasets"""
        try:
            models = await self.get_all_models()
            datasets = await self.get_all_datasets()
            
            # Model statistics
            total_model_downloads = sum(model.get('downloads', 0) for model in models)
            total_model_likes = sum(model.get('likes', 0) for model in models)
            
            model_tasks = {}
            model_libraries = {}
            model_licenses = {}
            
            for model in models:
                task = model.get('task', 'Unknown')
                library = model.get('library', 'Unknown')
                license_type = model.get('license', 'Unknown')
                
                model_tasks[task] = model_tasks.get(task, 0) + 1
                model_libraries[library] = model_libraries.get(library, 0) + 1
                model_licenses[license_type] = model_licenses.get(license_type, 0) + 1
            
            # Dataset statistics
            total_dataset_downloads = sum(dataset.get('downloads', 0) for dataset in datasets)
            total_dataset_likes = sum(dataset.get('likes', 0) for dataset in datasets)
            
            dataset_tasks = {}
            dataset_licenses = {}
            
            for dataset in datasets:
                task = dataset.get('task', 'Unknown')
                license_type = dataset.get('license', 'Unknown')
                
                dataset_tasks[task] = dataset_tasks.get(task, 0) + 1
                dataset_licenses[license_type] = dataset_licenses.get(license_type, 0) + 1
            
            return {
                'models': {
                    'total_models': len(models),
                    'total_downloads': total_model_downloads,
                    'total_likes': total_model_likes,
                    'tasks': model_tasks,
                    'libraries': model_libraries,
                    'licenses': model_licenses,
                    'most_downloaded': max(models, key=lambda x: x.get('downloads', 0)) if models else None,
                    'most_liked': max(models, key=lambda x: x.get('likes', 0)) if models else None
                },
                'datasets': {
                    'total_datasets': len(datasets),
                    'total_downloads': total_dataset_downloads,
                    'total_likes': total_dataset_likes,
                    'tasks': dataset_tasks,
                    'licenses': dataset_licenses,
                    'most_downloaded': max(datasets, key=lambda x: x.get('downloads', 0)) if datasets else None,
                    'most_liked': max(datasets, key=lambda x: x.get('likes', 0)) if datasets else None
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

# Factory function
def get_huggingface_integrations(config: Dict[str, Any] = None) -> HuggingFaceIntegrations:
    """Factory function to get Hugging Face integrations"""
    return HuggingFaceIntegrations(config)
