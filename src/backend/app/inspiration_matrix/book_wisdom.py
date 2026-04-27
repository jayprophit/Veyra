"""Book Wisdom Extractor - Extract trading wisdom from literature"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class BookCategory(Enum):
    INVESTING_CLASSICS = "investing_classics"
    TRADING_PSYCHOLOGY = "trading_psychology"
    MARKET_HISTORY = "market_history"
    RISK_MANAGEMENT = "risk_management"
    PHILOSOPHY = "philosophy"
    BIOGRAPHY = "biography"

@dataclass
class BookInsight:
    book: str
    author: str
    concept: str
    quote: str
    application: str
    category: BookCategory

class BookWisdomExtractor:
    """Extract trading wisdom from classic finance books"""
    
    def __init__(self):
        self.wisdom_database = self._load_wisdom()
    
    def _load_wisdom(self) -> List[BookInsight]:
        """Load wisdom from classic books"""
        return [
            BookInsight(
                book="Reminiscences of a Stock Operator",
                author="Edwin Lefevre",
                concept="Trend Following",
                quote="The market never changes - the pockets change, the suckers change, the stocks change, but Wall Street never changes",
                application="Human nature drives markets - patterns repeat",
                category=BookCategory.TRADING_PSYCHOLOGY
            ),
            BookInsight(
                book="Reminiscences of a Stock Operator",
                author="Edwin Lefevre",
                concept="Patience",
                quote="It was never my thinking that made the big money for me. It was always my sitting",
                application="Wait for the right setup, don't overtrade",
                category=BookCategory.TRADING_PSYCHOLOGY
            ),
            BookInsight(
                book="The Intelligent Investor",
                author="Benjamin Graham",
                concept="Margin of Safety",
                quote="The margin of safety is the difference between the intrinsic value and the market price",
                application="Only buy when price significantly below value",
                category=BookCategory.INVESTING_CLASSICS
            ),
            BookInsight(
                book="The Intelligent Investor",
                author="Benjamin Graham",
                concept="Mr. Market",
                quote="Mr. Market is there to serve you, not to guide you",
                application="Use market volatility to your advantage, don't be swayed by it",
                category=BookCategory.INVESTING_CLASSICS
            ),
            BookInsight(
                book="Market Wizards",
                author="Jack Schwager",
                concept="Risk Management",
                quote="The most important rule of trading is to play great defense, not offense",
                application="Protect capital first, profits second",
                category=BookCategory.RISK_MANAGEMENT
            ),
            BookInsight(
                book="Market Wizards",
                author="Jack Schwager",
                concept="Cut Losses",
                quote="Losers average losers",
                application="Never add to losing positions",
                category=BookCategory.RISK_MANAGEMENT
            ),
            BookInsight(
                book="Fooled by Randomness",
                author="Nassim Taleb",
                concept="Survivorship Bias",
                quote="We see the winners and learn from them, while forgetting about the losers",
                application="Be skeptical of success stories, consider base rates",
                category=BookCategory.PHILOSOPHY
            ),
            BookInsight(
                book="Fooled by Randomness",
                author="Nassim Taleb",
                concept="Black Swans",
                quote="Black swan events are rare, high-impact, and retrospectively predictable",
                application="Always maintain tail risk hedges",
                category=BookCategory.RISK_MANAGEMENT
            ),
            BookInsight(
                book="One Up On Wall Street",
                author="Peter Lynch",
                concept="Invest in What You Know",
                quote="Invest in companies you understand and use their products",
                application="Edge comes from personal experience and observation",
                category=BookCategory.INVESTING_CLASSICS
            ),
            BookInsight(
                book="One Up On Wall Street",
                author="Peter Lynch",
                concept="Ten-Baggers",
                quote="The best stock to buy may be the one you already own",
                application="Winners often keep winning - let winners run",
                category=BookCategory.INVESTING_CLASSICS
            ),
            BookInsight(
                book="When Genius Failed",
                author="Roger Lowenstein",
                concept="Leverage Danger",
                quote="LTCM's models said they couldn't lose more than x - they lost 100x",
                application="Models can fail - size positions for worst case, not expected case",
                category=BookCategory.RISK_MANAGEMENT
            ),
            BookInsight(
                book="The Black Swan",
                author="Nassim Taleb",
                concept="Antifragility",
                quote="Antifragile systems gain from disorder",
                application="Structure portfolios to benefit from volatility",
                category=BookCategory.PHILOSOPHY
            ),
            BookInsight(
                book="Flash Boys",
                author="Michael Lewis",
                concept="Market Structure",
                quote="The market is rigged - but understanding how gives you edge",
                application="Understand market microstructure to avoid predatory practices",
                category=BookCategory.MARKET_HISTORY
            ),
            BookInsight(
                book="The Big Short",
                author="Michael Lewis",
                concept="Contrarian Thinking",
                quote="The greatest trade is when everyone else is on the other side",
                application="Look for where consensus is wrong",
                category=BookCategory.MARKET_HISTORY
            ),
            BookInsight(
                book="Trading in the Zone",
                author="Mark Douglas",
                concept="Probabilistic Thinking",
                quote="Each trade is an independent event",
                application="Don't let previous trades affect current decisions",
                category=BookCategory.TRADING_PSYCHOLOGY
            )
        ]
    
    def get_wisdom_by_category(self, category: BookCategory) -> List[Dict]:
        """Get wisdom by category"""
        insights = [w for w in self.wisdom_database if w.category == category]
        return [self._insight_to_dict(i) for i in insights]
    
    def get_random_wisdom(self) -> Dict:
        """Get random wisdom nugget"""
        import random
        insight = random.choice(self.wisdom_database)
        return self._insight_to_dict(insight)
    
    def search_wisdom(self, keyword: str) -> List[Dict]:
        """Search wisdom by keyword"""
        matches = []
        for insight in self.wisdom_database:
            if (keyword.lower() in insight.book.lower() or
                keyword.lower() in insight.concept.lower() or
                keyword.lower() in insight.application.lower()):
                matches.append(self._insight_to_dict(insight))
        return matches
    
    def _insight_to_dict(self, insight: BookInsight) -> Dict:
        """Convert insight to dict"""
        return {
            "book": insight.book,
            "author": insight.author,
            "concept": insight.concept,
            "quote": insight.quote,
            "application": insight.application,
            "category": insight.category.value
        }
    
    def get_strategy_from_book(self, book_name: str) -> Dict:
        """Get complete strategy from a specific book"""
        insights = [w for w in self.wisdom_database if w.book == book_name]
        
        if not insights:
            return {"error": "Book not found"}
        
        # Group by concept
        concepts = {}
        for i in insights:
            if i.concept not in concepts:
                concepts[i.concept] = []
            concepts[i.concept].append(i.quote)
        
        return {
            "book": book_name,
            "author": insights[0].author,
            "key_concepts": list(concepts.keys()),
            "total_insights": len(insights),
            "strategy_summary": self._generate_strategy_summary(insights),
            "category": insights[0].category.value
        }
    
    def _generate_strategy_summary(self, insights: List[BookInsight]) -> str:
        """Generate strategy summary from insights"""
        applications = [i.application for i in insights]
        return " | ".join(applications[:3])  # Top 3 applications
    
    def compare_concepts(self, concept1: str, concept2: str) -> Dict:
        """Compare two trading concepts from literature"""
        insights1 = [w for w in self.wisdom_database if w.concept == concept1]
        insights2 = [w for w in self.wisdom_database if w.concept == concept2]
        
        return {
            "concept_1": {
                "name": concept1,
                "book_count": len(set(i.book for i in insights1)),
                "examples": [i.quote for i in insights1[:2]]
            },
            "concept_2": {
                "name": concept2,
                "book_count": len(set(i.book for i in insights2)),
                "examples": [i.quote for i in insights2[:2]]
            },
            "synergy": "Both emphasize risk control" if concept1 in ["Risk Management", "Margin of Safety"] and concept2 in ["Risk Management", "Margin of Safety"] else "Different approaches"
        }
