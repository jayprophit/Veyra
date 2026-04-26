"""Inspiration Matrix - Extract trading strategies from movies, anime, books"""

from .movie_intelligence import MovieIntelligenceExtractor
from .anime_analyzer import AnimeStrategyAnalyzer
from .book_wisdom import BookWisdomExtractor
from .narrative_patterns import NarrativePatternTrader

__all__ = [
    "MovieIntelligenceExtractor",
    "AnimeStrategyAnalyzer",
    "BookWisdomExtractor",
    "NarrativePatternTrader"
]
