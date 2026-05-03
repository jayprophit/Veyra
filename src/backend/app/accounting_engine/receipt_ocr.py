"""
Receipt OCR Processing System
Inspired by ANNA Business Account - Photo to Expense automation
Supports Tesseract.js local OCR and cloud OCR APIs
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum
import uuid
import re

class OCREngine(Enum):
    TESSERACT = "tesseract"  # Local processing
    GOOGLE_VISION = "google_vision"  # Cloud API
    AWS_TEXTRACT = "aws_textract"  # Cloud API
    AZURE_FORM_RECOGNIZER = "azure_form_recognizer"  # Cloud API
    OPENAI_VISION = "openai_vision"  # GPT-4 Vision

@dataclass
class ExtractedReceiptData:
    """Structured data extracted from receipt"""
    vendor_name: str = ""
    vendor_address: str = ""
    date: Optional[datetime] = None
    total_amount: float = 0.0
    subtotal: float = 0.0
    tax_amount: float = 0.0
    tip_amount: float = 0.0
    currency: str = "USD"
    items: List[Dict[str, Any]] = field(default_factory=list)
    payment_method: str = ""
    receipt_number: str = ""
    category_suggestion: str = ""
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    raw_text: str = ""

@dataclass
class ReceiptLineItem:
    """Individual line item from receipt"""
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    total_price: float = 0.0
    category: str = ""

class ReceiptOCR:
    """
    Receipt OCR processing with AI enhancement
    Extracts expense data from receipt images
    """
    
    # Common receipt patterns for regex extraction
    AMOUNT_PATTERNS = [
        r'total[\s:]+[$€£]?\s*([\d,]+\.?\d{0,2})',
        r'amount[\s:]+[$€£]?\s*([\d,]+\.?\d{0,2})',
        r'subtotal[\s:]+[$€£]?\s*([\d,]+\.?\d{0,2})',
        r'tax[\s:]+[$€£]?\s*([\d,]+\.?\d{0,2})',
        r'tip[\s:]+[$€£]?\s*([\d,]+\.?\d{0,2})',
    ]
    
    DATE_PATTERNS = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
    ]
    
    VENDOR_CATEGORIES = {
        "restaurant|cafe|coffee|food|dining": "Meals & Entertainment",
        "gas|fuel|petrol|shell|bp |exxon": "Fuel",
        "uber|lyft|taxi|transport": "Transportation",
        "hotel|airbnb|motel": "Lodging",
        "office|staples|supplies": "Office Supplies",
        "software|saas|subscription": "Software",
        "airline|flight|travel": "Travel",
        "pharmacy|medical|health": "Medical",
    }
    
    def __init__(self, engine: OCREngine = OCREngine.TESSERACT):
        self.engine = engine
        self._processing_history: List[Dict] = []
    
    def process_receipt(self, image_data: bytes, 
                       filename: str = "",
                       user_id: str = "",
                       auto_categorize: bool = True) -> ExtractedReceiptData:
        """
        Process a receipt image and extract structured data
        
        Args:
            image_data: Raw image bytes
            filename: Original filename
            user_id: User identifier for learning
            auto_categorize: Whether to auto-suggest expense category
        
        Returns:
            ExtractedReceiptData with all found fields
        """
        # Step 1: OCR text extraction
        raw_text = self._extract_text(image_data)
        
        # Step 2: Parse structured data
        extracted = self._parse_receipt_text(raw_text)
        
        # Step 3: AI enhancement and categorization
        if auto_categorize:
            extracted.category_suggestion = self._suggest_category(extracted)
        
        # Step 4: Store processing record
        self._record_processing(filename, user_id, extracted)
        
        return extracted
    
    def _extract_text(self, image_data: bytes) -> str:
        """
        Extract raw text from image using selected OCR engine
        Placeholder - actual implementation would use OCR library
        """
        # In production, this would:
        # - Use pytesseract for local OCR
        # - Or call cloud APIs (Google Vision, AWS Textract, etc.)
        # - Or use OpenAI GPT-4 Vision
        
        # For now, return empty string - actual OCR would be integrated
        return ""
    
    def _parse_receipt_text(self, text: str) -> ExtractedReceiptData:
        """Parse structured data from OCR text"""
        extracted = ExtractedReceiptData(raw_text=text)
        
        # Extract amounts
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    if 'total' in pattern.lower() and not extracted.total_amount:
                        extracted.total_amount = amount
                        extracted.confidence_scores['total'] = 0.9
                    elif 'subtotal' in pattern.lower():
                        extracted.subtotal = amount
                        extracted.confidence_scores['subtotal'] = 0.85
                    elif 'tax' in pattern.lower():
                        extracted.tax_amount = amount
                        extracted.confidence_scores['tax'] = 0.8
                    elif 'tip' in pattern.lower():
                        extracted.tip_amount = amount
                        extracted.confidence_scores['tip'] = 0.8
                except ValueError:
                    continue
        
        # Extract date
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse date
                    extracted.date = self._parse_date(date_str)
                    extracted.confidence_scores['date'] = 0.85
                    break
                except:
                    continue
        
        # Extract vendor (first line often contains vendor name)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First few lines often contain vendor name
            for line in lines[:5]:
                if len(line) > 2 and not any(x in line.lower() for x in ['total', 'date', 'receipt']):
                    extracted.vendor_name = line
                    extracted.confidence_scores['vendor'] = 0.7
                    break
        
        # Extract receipt number
        receipt_match = re.search(r'(?:receipt|invoice|order)[\s#:]*(\w+[\w-]*)', text, re.IGNORECASE)
        if receipt_match:
            extracted.receipt_number = receipt_match.group(1)
            extracted.confidence_scores['receipt_number'] = 0.9
        
        # Extract line items (simplified)
        extracted.items = self._extract_line_items(text)
        
        return extracted
    
    def _extract_line_items(self, text: str) -> List[Dict]:
        """Extract individual line items from receipt"""
        items = []
        lines = text.split('\n')
        
        # Look for patterns like "Item $X.XX" or "Item... $X.XX"
        item_pattern = r'(.+?)[\s.]+[$€£]?\s*(\d+\.\d{2})\s*$'
        
        for line in lines:
            match = re.match(item_pattern, line.strip())
            if match and 'total' not in line.lower() and 'subtotal' not in line.lower():
                description = match.group(1).strip()
                try:
                    price = float(match.group(2))
                    if 0.01 < price < 10000:  # Reasonable price range
                        items.append({
                            "description": description,
                            "quantity": 1,
                            "unit_price": price,
                            "total_price": price
                        })
                except ValueError:
                    continue
        
        return items
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        formats = [
            '%m/%d/%Y', '%m/%d/%y',
            '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%y/%m/%d',
            '%m-%d-%Y', '%m-%d-%y',
            '%d %b %Y', '%d %B %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _suggest_category(self, extracted: ExtractedReceiptData) -> str:
        """Suggest expense category based on vendor and items"""
        text_to_analyze = f"{extracted.vendor_name} {extracted.raw_text}".lower()
        
        for pattern, category in self.VENDOR_CATEGORIES.items():
            if re.search(pattern, text_to_analyze):
                return category
        
        # Default categorization based on amount
        if extracted.total_amount < 10:
            return "Small Expenses"
        elif extracted.total_amount > 100:
            return "Major Expenses"
        
        return "General Expense"
    
    def _record_processing(self, filename: str, user_id: str, extracted: ExtractedReceiptData):
        """Record processing for analytics and improvement"""
        record = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "vendor": extracted.vendor_name,
            "amount": extracted.total_amount,
            "category": extracted.category_suggestion,
            "confidence_avg": sum(extracted.confidence_scores.values()) / len(extracted.confidence_scores) if extracted.confidence_scores else 0,
            "fields_extracted": len([v for v in [extracted.vendor_name, extracted.total_amount, extracted.date] if v])
        }
        
        self._processing_history.append(record)
    
    def create_journal_entry_from_receipt(self, extracted: ExtractedReceiptData,
                                         payment_account: str = "1000") -> Dict:
        """
        Create a journal entry proposal from extracted receipt data
        Ready to be posted to the double-entry system
        """
        from .ai_categorization import get_ai_categorization
        
        # Get AI categorization
        ai = get_ai_categorization()
        cat_result = ai.categorize_transaction(
            description=f"{extracted.vendor_name} - Receipt {extracted.receipt_number}",
            amount=-extracted.total_amount,  # Expense is negative
            merchant=extracted.vendor_name
        )
        
        return {
            "description": f"Expense: {extracted.vendor_name} - {extracted.receipt_number}",
            "date": extracted.date.isoformat() if extracted.date else datetime.now().isoformat(),
            "amount": extracted.total_amount,
            "expense_account": cat_result.account_code,
            "payment_account": payment_account,
            "category": cat_result.category,
            "receipt_data": extracted.to_dict() if hasattr(extracted, 'to_dict') else {
                "vendor": extracted.vendor_name,
                "amount": extracted.total_amount,
                "date": extracted.date.isoformat() if extracted.date else None,
                "items": extracted.items
            },
            "confidence": cat_result.confidence,
            "explanation": cat_result.explanation
        }
    
    def get_processing_stats(self) -> Dict:
        """Get OCR processing statistics"""
        if not self._processing_history:
            return {
                "total_processed": 0,
                "avg_confidence": 0,
                "success_rate": 0
            }
        
        total = len(self._processing_history)
        avg_confidence = sum(r.get("confidence_avg", 0) for r in self._processing_history) / total
        
        # Success = at least 2 fields extracted
        successful = sum(1 for r in self._processing_history if r.get("fields_extracted", 0) >= 2)
        success_rate = (successful / total) * 100
        
        return {
            "total_processed": total,
            "avg_confidence": avg_confidence,
            "success_rate": success_rate,
            "category_breakdown": self._get_category_breakdown()
        }
    
    def _get_category_breakdown(self) -> Dict:
        """Get breakdown of processed receipts by category"""
        from collections import Counter
        categories = [r.get("category", "Unknown") for r in self._processing_history]
        return dict(Counter(categories))

# Singleton instance
_receipt_ocr: Optional[ReceiptOCR] = None

def get_receipt_ocr(engine: OCREngine = OCREngine.TESSERACT) -> ReceiptOCR:
    """Get or create singleton Receipt OCR instance"""
    global _receipt_ocr
    if _receipt_ocr is None:
        _receipt_ocr = ReceiptOCR(engine)
    return _receipt_ocr
