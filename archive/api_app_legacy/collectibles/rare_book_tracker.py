"""
Rare Books & Manuscripts Tracker
=================================
Track rare book and manuscript investments
First editions, signed copies, historical documents
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BookCategory(Enum):
    LITERATURE = "literature"
    SCIENCE = "science"
    HISTORY = "history"
    PHILOSOPHY = "philosophy"
    CHILDRENS = "childrens"
    RELIGIOUS = "religious"
    MAPS_ATLASES = "maps_atlases"
    MANUSCRIPTS = "manuscripts"


@dataclass
class RareBook:
    title: str
    author: str
    year: int
    edition: str  # 'first', 'second', 'limited', 'signed'
    publisher: str
    condition: str  # 'fine', 'very_good', 'good', 'fair', 'poor'
    binding: str
    provenance: List[str]
    notable_features: List[str]  # signed, inscribed, etc.
    
    purchase_price: float
    purchase_date: datetime
    current_estimate: float


class RareBookTracker:
    """Track rare book and manuscript investments"""
    
    # Major book indices (approximate returns)
    BOOK_INDICES = {
        'abe_american_authors': {'cagr_20yr': 0.065},
        'abe_english_literature': {'cagr_20yr': 0.055},
        'abe_science_medicine': {'cagr_20yr': 0.075},
        'travel_exploration': {'cagr_20yr': 0.060},
        'incunabula': {'cagr_20yr': 0.045}  # Pre-1501 books
    }
    
    # Blue chip authors/categories
    BLUE_CHIP_BOOKS = {
        'literature': [
            'William Shakespeare First Folio',
            'Jane Austen First Editions',
            'Charles Dickens First Editions',
            'Mark Twain First Editions',
            'F. Scott Fitzgerald (Gatsby)',
            'Ernest Hemingway First Editions',
            'J.R.R. Tolkien (Lord of the Rings)',
            'J.K. Rowling (Harry Potter 1st)'
        ],
        'science': [
            'Isaac Newton Principia Mathematica',
            'Charles Darwin Origin of Species',
            'Albert Einstein Papers',
            'Galileo Dialogo',
            'Copernicus De Revolutionibus'
        ],
        'americana': [
            'Federalist Papers First Edition',
            'Common Sense (Paine)',
            'Declaration Broadside',
            'Lewis and Clark Journals'
        ]
    }
    
    # Condition multipliers (relative to Fine)
    CONDITION_MULTIPLIERS = {
        'fine': 1.0,
        'fine_minus': 0.75,
        'very_good_plus': 0.55,
        'very_good': 0.45,
        'very_good_minus': 0.35,
        'good_plus': 0.25,
        'good': 0.20,
        'good_minus': 0.15,
        'fair': 0.10,
        'poor': 0.05
    }
    
    def analyze_book_performance(self, book: RareBook) -> Dict:
        """Analyze rare book investment performance"""
        
        holding_years = (datetime.now() - book.purchase_date).days / 365.25
        
        # Calculate returns
        if holding_years > 0:
            total_return = (book.current_estimate - book.purchase_price) / book.purchase_price
            annualized = (1 + total_return) ** (1 / holding_years) - 1
        else:
            total_return = 0
            annualized = 0
        
        # Book characteristics
        is_first_edition = 'first' in book.edition.lower()
        is_signed = any('signed' in f.lower() for f in book.notable_features)
        is_association = any('association' in f.lower() for f in book.provenance)
        
        # Scarcity assessment
        scarcity = self._assess_scarcity(book.author, book.title, book.year)
        
        # Condition impact
        condition_mult = self.CONDITION_MULTIPLIERS.get(book.condition, 0.5)
        
        return {
            'book': f"{book.title} by {book.author} ({book.year})",
            'edition': book.edition,
            'condition': book.condition,
            'condition_factor': condition_mult,
            'purchase_price': round(book.purchase_price, 0),
            'current_estimate': round(book.current_estimate, 0),
            'unrealized_gain': round(book.current_estimate - book.purchase_price, 0),
            'holding_years': round(holding_years, 1),
            'annualized_return_pct': round(annualized * 100, 1),
            'key_attributes': {
                'first_edition': is_first_edition,
                'signed': is_signed,
                'association_copy': is_association
            },
            'scarcity': scarcity,
            'rarity_score': self._calculate_rarity_score(book, is_first_edition, is_signed),
            'recommendation': self._book_recommendation(book, annualized, is_first_edition)
        }
    
    def _assess_scarcity(self, author: str, title: str, year: int) -> str:
        """Assess book scarcity"""
        # Check blue chip lists
        for category, books in self.BLUE_CHIP_BOOKS.items():
            for book in books:
                if author.lower() in book.lower() or title.lower() in book.lower():
                    return 'VERY_HIGH'
        
        # Age-based
        if year < 1500:
            return 'ULTRA_RARE'
        elif year < 1700:
            return 'VERY_HIGH'
        elif year < 1800:
            return 'HIGH'
        elif year < 1900:
            return 'MODERATE'
        else:
            return 'STANDARD'
    
    def _calculate_rarity_score(self, book: RareBook, 
                                is_first: bool, is_signed: bool) -> int:
        """Calculate rarity score 0-100"""
        score = 50  # Base
        
        if is_first:
            score += 25
        if is_signed:
            score += 15
        if any('association' in p.lower() for p in book.provenance):
            score += 10
        if book.year < 1800:
            score += 10
        if 'limited' in book.edition.lower():
            score += 5
        
        return min(score, 100)
    
    def _book_recommendation(self, book: RareBook, 
                           annualized_return: float,
                           is_first_edition: bool) -> str:
        """Generate book recommendation"""
        if annualized_return > 0.15 and not is_first_edition:
            return "CONSIDER_UPGRADE - Sell for true first edition"
        elif annualized_return > 0.20:
            return "PROFIT_TAKING - Exceptional appreciation"
        elif book.year < 1600:
            return "HOLD_FOREVER - Incunabula/early printing"
        elif 'Shakespeare' in book.author or 'Newton' in book.author:
            return "HOLD - Ultimate blue chip"
        elif book.condition in ['fair', 'poor']:
            return "RESTORE/CONSERVE - Condition upgrade potential"
        else:
            return "HOLD - Continue building collection"
    
    def get_investment_guide(self) -> Dict:
        """Get rare book investment guide"""
        return {
            'market_overview': {
                'annual_sales': '$500M+ globally',
                'growth_drivers': [
                    'Institutional collections',
                    'Wealthy individuals diversifying',
                    'Asian market growth',
                    'Digital scarcity premium'
                ]
            },
            'blue_chip_authors': {
                'english_literature': ['Shakespeare', 'Austen', 'Dickens', 'Brontes'],
                'american': ['Twain', 'Fitzgerald', 'Hemingway', 'Faulkner'],
                'science': ['Newton', 'Darwin', 'Einstein', 'Galileo'],
                'philosophy': ['Plato', 'Aristotle', 'Kant', 'Descartes']
            },
            'investment_principles': [
                'Condition is paramount - buy the best you can afford',
                'First editions only (except rare exceptions)',
                'Original bindings preferred',
                'Provenance adds 20-50% premium',
                'Complete copies essential',
                'Dust jackets on 20th century = critical'
            ],
            'financial_characteristics': {
                'returns_20yr': '5-7% annually',
                'volatility': 'LOW',
                'liquidity': 'LOW - 6-12 months typical',
                'transaction_costs': '20-30% (buyer premium + seller commission)',
                'storage': 'Minimal - proper shelving/climate control',
                'insurance': '0.5% annually'
            },
            'key_auctions': [
                'Christies New York/London',
                'Sothebys',
                'Swann Galleries',
                'Heritage Auctions'
            ]
        }


# Usage
def analyze_rare_book(title: str, author: str, year: int,
                     edition: str, condition: str,
                     purchase: float, current: float) -> Dict:
    """Quick rare book analysis"""
    tracker = RareBookTracker()
    
    book = RareBook(
        title=title,
        author=author,
        year=year,
        edition=edition,
        publisher='First Publisher',
        condition=condition,
        binding='Original cloth',
        provenance=['Private collection'],
        notable_features=['First Edition'] if 'first' in edition.lower() else [],
        purchase_price=purchase,
        purchase_date=datetime.now() - __import__('datetime').timedelta(days=365*5),
        current_estimate=current
    )
    
    return tracker.analyze_book_performance(book)


def get_book_guide() -> Dict:
    """Get book investment guide"""
    tracker = RareBookTracker()
    return tracker.get_investment_guide()
