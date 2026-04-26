"""
Import/Export Management System
Handles international trade documentation, customs, and compliance
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import asyncio


class TradeType(Enum):
    IMPORT = "import"
    EXPORT = "export"


class TransportMode(Enum):
    SEA = "sea"
    AIR = "air"
    LAND = "land"
    MULTIMODAL = "multimodal"


class ShipmentStatus(Enum):
    PENDING = "pending"
    DOCUMENTATION = "documentation"
    CUSTOMS_CLEARANCE = "customs_clearance"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


@dataclass
class TradeDocument:
    """Trade documentation"""
    document_type: str  # commercial_invoice, packing_list, bill_of_lading, certificate_of_origin, etc.
    document_number: str
    issue_date: date
    expiry_date: Optional[date] = None
    issuing_authority: str = ""
    file_url: str = ""
    is_verified: bool = False
    verification_date: Optional[date] = None


@dataclass
class CustomsDeclaration:
    """Customs declaration details"""
    declaration_id: str
    country_of_origin: str
    country_of_destination: str
    hs_code: str  # Harmonized System code
    product_description: str
    quantity: Decimal
    unit_of_measure: str
    value_declaration: Decimal
    currency: str
    duty_rate: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    total_duties: Decimal = Decimal("0")
    total_vat: Decimal = Decimal("0")


@dataclass
class Shipment:
    """Shipment tracking"""
    shipment_id: str
    trade_type: TradeType
    transport_mode: TransportMode
    status: ShipmentStatus
    
    # Parties
    exporter_id: str
    importer_id: str
    
    # Goods
    product_name: str
    product_category: str
    quantity: Decimal
    unit_value: Decimal
    total_value: Decimal
    currency: str
    
    # Logistics
    port_of_loading: str
    port_of_discharge: str
    estimated_departure: datetime
    estimated_arrival: datetime
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    
    # Documentation
    documents: List[TradeDocument] = field(default_factory=list)
    customs: Optional[CustomsDeclaration] = None
    
    # Tracking
    tracking_number: str = ""
    carrier: str = ""
    current_location: str = ""
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class ImportExportManager:
    """
    Manages import/export operations
    
    Features:
    - Shipment tracking
    - Document management
    - Customs compliance
    - Duty/VAT calculations
    - Trade finance integration
    """
    
    def __init__(self):
        self.shipments: Dict[str, Shipment] = {}
        self.hs_code_database: Dict[str, Dict] = {}
        self.trade_agreements: Dict[str, Any] = {}
        
        # Tariff rates by country and HS code
        self.tariff_rates: Dict[str, Dict[str, Decimal]] = {}
        
        # Incoterms
        self.incoterms = [
            "EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP",
            "FAS", "FOB", "CFR", "CIF"
        ]
    
    async def create_shipment(
        self,
        trade_type: TradeType,
        exporter_id: str,
        importer_id: str,
        product_details: Dict[str, Any],
        logistics: Dict[str, Any],
        transport_mode: TransportMode = TransportMode.SEA
    ) -> Shipment:
        """
        Create new import/export shipment
        
        Args:
            trade_type: Import or Export
            exporter_id: Exporting party ID
            importer_id: Importing party ID
            product_details: Product name, category, quantity, value
            logistics: Ports, dates, carrier
            transport_mode: Sea, air, land, multimodal
        """
        shipment_id = f"SHIP_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        shipment = Shipment(
            shipment_id=shipment_id,
            trade_type=trade_type,
            transport_mode=transport_mode,
            status=ShipmentStatus.PENDING,
            exporter_id=exporter_id,
            importer_id=importer_id,
            product_name=product_details["name"],
            product_category=product_details["category"],
            quantity=Decimal(str(product_details["quantity"])),
            unit_value=Decimal(str(product_details["unit_value"])),
            total_value=Decimal(str(product_details["quantity"])) * Decimal(str(product_details["unit_value"])),
            currency=product_details.get("currency", "USD"),
            port_of_loading=logistics["port_of_loading"],
            port_of_discharge=logistics["port_of_discharge"],
            estimated_departure=logistics["estimated_departure"],
            estimated_arrival=logistics["estimated_arrival"],
            tracking_number=logistics.get("tracking_number", ""),
            carrier=logistics.get("carrier", "")
        )
        
        self.shipments[shipment_id] = shipment
        
        return shipment
    
    async def add_document(
        self,
        shipment_id: str,
        document_type: str,
        document_number: str,
        issue_date: date,
        file_url: str,
        issuing_authority: str = ""
    ) -> TradeDocument:
        """Add document to shipment"""
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            raise ValueError("Shipment not found")
        
        document = TradeDocument(
            document_type=document_type,
            document_number=document_number,
            issue_date=issue_date,
            file_url=file_url,
            issuing_authority=issuing_authority
        )
        
        shipment.documents.append(document)
        
        return document
    
    async def create_customs_declaration(
        self,
        shipment_id: str,
        origin_country: str,
        destination_country: str,
        hs_code: str,
        product_description: str,
        quantity: Decimal,
        unit: str,
        value: Decimal,
        currency: str
    ) -> CustomsDeclaration:
        """
        Create customs declaration
        
        Calculates duties and VAT automatically
        """
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            raise ValueError("Shipment not found")
        
        # Calculate duties
        duty_rate = await self._get_duty_rate(origin_country, destination_country, hs_code)
        total_duties = value * duty_rate if duty_rate else Decimal("0")
        
        # Calculate VAT
        vat_rate = await self._get_vat_rate(destination_country)
        total_vat = (value + total_duties) * vat_rate
        
        customs = CustomsDeclaration(
            declaration_id=f"CUST_{shipment_id}",
            country_of_origin=origin_country,
            country_of_destination=destination_country,
            hs_code=hs_code,
            product_description=product_description,
            quantity=quantity,
            unit_of_measure=unit,
            value_declaration=value,
            currency=currency,
            duty_rate=duty_rate,
            vat_rate=vat_rate,
            total_duties=total_duties,
            total_vat=total_vat
        )
        
        shipment.customs = customs
        shipment.status = ShipmentStatus.CUSTOMS_CLEARANCE
        
        return customs
    
    async def _get_duty_rate(
        self,
        origin: str,
        destination: str,
        hs_code: str
    ) -> Optional[Decimal]:
        """Get duty rate from tariff database"""
        # Check for trade agreement
        agreement_key = f"{origin}_{destination}"
        if agreement_key in self.trade_agreements:
            return self.trade_agreements[agreement_key].get("duty_rate", Decimal("0"))
        
        # Default MFN rate
        country_tariffs = self.tariff_rates.get(destination, {})
        return country_tariffs.get(hs_code, Decimal("0.05"))  # Default 5%
    
    async def _get_vat_rate(self, country: str) -> Decimal:
        """Get VAT/GST rate for country"""
        vat_rates = {
            "UK": Decimal("0.20"),
            "DE": Decimal("0.19"),
            "FR": Decimal("0.20"),
            "IT": Decimal("0.22"),
            "ES": Decimal("0.21"),
            "US": Decimal("0"),  # Sales tax varies by state
            "CN": Decimal("0.13"),
            "JP": Decimal("0.10"),
            "AU": Decimal("0.10"),
            "CA": Decimal("0.05"),
        }
        return vat_rates.get(country, Decimal("0.20"))
    
    async def update_shipment_status(
        self,
        shipment_id: str,
        status: ShipmentStatus,
        location: str = "",
        notes: str = ""
    ) -> Shipment:
        """Update shipment status and add milestone"""
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            raise ValueError("Shipment not found")
        
        shipment.status = status
        shipment.current_location = location
        
        milestone = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status.value,
            "location": location,
            "notes": notes
        }
        shipment.milestones.append(milestone)
        
        return shipment
    
    async def track_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Get shipment tracking information"""
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return {"error": "Shipment not found"}
        
        return {
            "shipment_id": shipment_id,
            "status": shipment.status.value,
            "carrier": shipment.carrier,
            "tracking_number": shipment.tracking_number,
            "current_location": shipment.current_location,
            "origin": shipment.port_of_loading,
            "destination": shipment.port_of_discharge,
            "estimated_arrival": shipment.estimated_arrival.isoformat(),
            "milestones": shipment.milestones,
            "progress_percentage": self._calculate_progress(shipment)
        }
    
    def _calculate_progress(self, shipment: Shipment) -> int:
        """Calculate shipment progress percentage"""
        status_order = [
            ShipmentStatus.PENDING,
            ShipmentStatus.DOCUMENTATION,
            ShipmentStatus.CUSTOMS_CLEARANCE,
            ShipmentStatus.IN_TRANSIT,
            ShipmentStatus.ARRIVED,
            ShipmentStatus.DELIVERED
        ]
        
        if shipment.status in status_order:
            current_index = status_order.index(shipment.status)
            return int((current_index / (len(status_order) - 1)) * 100)
        
        return 0
    
    async def calculate_total_landed_cost(
        self,
        shipment_id: str,
        include_duties: bool = True,
        include_shipping: bool = True,
        include_insurance: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate total landed cost
        
        Product cost + Duties + VAT + Shipping + Insurance + Other fees
        """
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return {"error": "Shipment not found"}
        
        product_cost = shipment.total_value
        
        customs_costs = Decimal("0")
        if shipment.customs and include_duties:
            customs_costs = shipment.customs.total_duties + shipment.customs.total_vat
        
        # Shipping cost (mock)
        shipping_cost = Decimal("500") if include_shipping else Decimal("0")
        
        # Insurance (typically 0.5% of value)
        insurance_cost = (product_cost * Decimal("0.005")) if include_insurance else Decimal("0")
        
        # Other fees (handling, documentation, etc.)
        other_fees = Decimal("150")
        
        total_landed = product_cost + customs_costs + shipping_cost + insurance_cost + other_fees
        
        return {
            "shipment_id": shipment_id,
            "currency": shipment.currency,
            "breakdown": {
                "product_cost": float(product_cost),
                "customs_duties": float(shipment.customs.total_duties) if shipment.customs and include_duties else 0,
                "vat": float(shipment.customs.total_vat) if shipment.customs and include_duties else 0,
                "shipping": float(shipping_cost),
                "insurance": float(insurance_cost),
                "other_fees": float(other_fees)
            },
            "total_landed_cost": float(total_landed),
            "unit_landed_cost": float(total_landed / shipment.quantity) if shipment.quantity > 0 else 0
        }
    
    async def get_compliance_checklist(
        self,
        shipment_id: str
    ) -> List[Dict[str, Any]]:
        """Get compliance checklist for shipment"""
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return []
        
        required_documents = []
        
        if shipment.trade_type == TradeType.EXPORT:
            required_documents = [
                {"type": "commercial_invoice", "required": True, "status": "pending"},
                {"type": "packing_list", "required": True, "status": "pending"},
                {"type": "bill_of_lading", "required": True, "status": "pending"},
                {"type": "certificate_of_origin", "required": True, "status": "pending"},
                {"type": "export_license", "required": False, "status": "na"},
                {"type": "insurance_certificate", "required": True, "status": "pending"}
            ]
        else:  # IMPORT
            required_documents = [
                {"type": "commercial_invoice", "required": True, "status": "pending"},
                {"type": "packing_list", "required": True, "status": "pending"},
                {"type": "bill_of_lading", "required": True, "status": "pending"},
                {"type": "certificate_of_origin", "required": True, "status": "pending"},
                {"type": "import_license", "required": False, "status": "na"},
                {"type": "customs_declaration", "required": True, "status": "pending"}
            ]
        
        # Check existing documents
        existing_types = [d.document_type for d in shipment.documents]
        for doc in required_documents:
            if doc["type"] in existing_types:
                doc["status"] = "completed"
        
        return required_documents
    
    async def search_hs_code(
        self,
        product_description: str,
        country: str
    ) -> List[Dict[str, Any]]:
        """Search for HS codes by product description"""
        # In production: Query HS code database or API
        
        mock_results = [
            {
                "hs_code": "8517.12.00",
                "description": "Telephones for cellular networks",
                "duty_rate": "0%",
                "category": "Electronics"
            },
            {
                "hs_code": "8471.30.01",
                "description": "Portable automatic data processing machines",
                "duty_rate": "0%",
                "category": "Computers"
            },
            {
                "hs_code": "6204.62.11",
                "description": "Women's trousers of cotton",
                "duty_rate": "12%",
                "category": "Clothing"
            }
        ]
        
        return mock_results
