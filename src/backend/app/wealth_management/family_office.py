"""Family Office - Multi-generational wealth management"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FamilyMember:
    name: str
    age: int
    generation: int  # 1, 2, 3...
    risk_tolerance: str  # Conservative, Moderate, Aggressive
    annual_spending: float
    inheritance_expected: float

class FamilyOffice:
    """Manage multi-generational family wealth"""
    
    def __init__(self, family_name: str, total_aum: float):
        self.family_name = family_name
        self.total_aum = total_aum
        self.members: List[FamilyMember] = []
        self.generational_wealth: Dict[int, float] = {}
        self.legacy_goals: Dict = {}
    
    def add_member(self, member: FamilyMember):
        """Add family member"""
        self.members.append(member)
    
    def set_legacy_goal(self, goal_type: str, target_amount: float, timeline_years: int):
        """Set long-term family goal"""
        self.legacy_goals[goal_type] = {
            "target": target_amount,
            "timeline": timeline_years,
            "annual_requirement": target_amount / timeline_years if timeline_years > 0 else 0
        }
    
    def calculate_generational_allocation(self) -> Dict:
        """Calculate optimal allocation across generations"""
        if not self.members:
            return {"error": "No family members defined"}
        
        # Group by generation
        gen_data = {}
        for member in self.members:
            gen = member.generation
            if gen not in gen_data:
                gen_data[gen] = {"members": [], "total_spending": 0}
            gen_data[gen]["members"].append(member)
            gen_data[gen]["total_spending"] += member.annual_spending
        
        allocations = []
        remaining_aum = self.total_aum
        
        # Allocate starting from oldest generation
        for gen in sorted(gen_data.keys()):
            data = gen_data[gen]
            
            # Calculate required capital for spending (4% rule adjusted)
            spending_need = data["total_spending"]
            years_to_support = self._estimate_years(gen, data["members"])
            
            # Conservative allocation for near-term needs
            if gen == 1:
                # First generation needs immediate liquidity
                allocation_pct = 0.30
                strategy = "INCOME_WITH_GROWTH"
            elif gen == 2:
                # Second generation: balanced growth
                allocation_pct = 0.35
                strategy = "BALANCED_GROWTH"
            else:
                # Third+ generation: maximum growth
                allocation_pct = 0.35
                strategy = "MAXIMUM_GROWTH"
            
            allocation_amount = self.total_aum * allocation_pct
            
            allocations.append({
                "generation": gen,
                "num_members": len(data["members"]),
                "allocation_pct": round(allocation_pct * 100, 1),
                "allocation_amount": round(allocation_amount, 0),
                "annual_spending_need": spending_need,
                "years_to_support": years_to_support,
                "investment_strategy": strategy,
                "sustainable_withdrawal_rate": 0.04 if gen == 1 else 0.05
            })
        
        return {
            "family_name": self.family_name,
            "total_aum": self.total_aum,
            "generations": allocations,
            "liquidity_buffer_pct": 5.0,
            "recommended_structure": self._recommend_structure(len(gen_data))
        }
    
    def _estimate_years(self, generation: int, members: List[FamilyMember]) -> int:
        """Estimate years of support needed"""
        max_age = max(m.age for m in members) if members else 50
        
        if generation == 1:
            # First gen: assume 30 more years
            return 30
        elif generation == 2:
            # Second gen: assume 50 more years
            return 50
        else:
            # Third+: assume 70 more years
            return 70
    
    def _recommend_structure(self, num_generations: int) -> str:
        """Recommend family office structure"""
        if self.total_aum > 500e6:
            return "DEDICATED_SINGLE_FAMILY_OFFICE"
        elif self.total_aum > 100e6:
            return "VIRTUAL_FAMILY_OFFICE"
        elif self.total_aum > 20e6:
            return "MULTI_FAMILY_OFFICE"
        else:
            return "PRIVATE_WEALTH_MANAGER"
    
    def calculate_heritage_preservation(self, inflation_rate: float = 0.03,
                                       target_generations: int = 3) -> Dict:
        """Calculate wealth preservation across generations"""
        # Real wealth preservation calculation
        # Goal: Maintain purchasing power across target generations
        
        current_gen_spending = sum(m.annual_spending for m in self.members if m.generation == 1)
        
        # Calculate required growth to maintain real wealth
        # After n generations, spending needs grow with inflation and family size
        
        # Assume family grows 50% per generation
        family_growth_rate = 0.50
        num_descendants = 1
        
        total_future_spending = 0
        for gen in range(1, target_generations + 1):
            num_descendants = num_descendants * (1 + family_growth_rate)
            gen_spending = current_gen_spending * num_descendants * ((1 + inflation_rate) ** (gen * 25))
            total_future_spending += gen_spending
        
        # Required portfolio growth
        years = target_generations * 25  # 25 years per generation
        required_cagr = ((total_future_spending / self.total_aum) ** (1/years)) - 1 if years > 0 else 0
        
        # Recommended allocation
        if required_cagr > 0.07:
            equity_pct = 70
            alt_pct = 20
        elif required_cagr > 0.05:
            equity_pct = 60
            alt_pct = 15
        else:
            equity_pct = 50
            alt_pct = 10
        
        return {
            "target_generations": target_generations,
            "required_cagr": round(required_cagr * 100, 2),
            "current_aum": self.total_aum,
            "projected_spending": round(total_future_spending, 0),
            "recommended_allocation": {
                "equities_pct": equity_pct,
                "fixed_income_pct": 100 - equity_pct - alt_pct - 10,
                "alternatives_pct": alt_pct,
                "cash_pct": 10
            },
            "preservation_probability": "HIGH" if required_cagr < 0.06 else "MODERATE" if required_cagr < 0.08 else "LOW"
        }
    
    def estate_planning_analysis(self, estate_tax_rate: float = 0.40,
                                  annual_gift_exclusion: float = 17000) -> Dict:
        """Analyze estate planning strategies"""
        gross_estate = self.total_aum
        
        # Calculate estate tax exposure
        estate_tax_exemption = 13.61e6  # 2024 limit per person
        num_members = len(self.members)
        
        # Total exemption for couple (assuming married)
        total_exemption = estate_tax_exemption * 2
        
        taxable_estate = max(0, gross_estate - total_exemption)
        estimated_tax = taxable_estate * estate_tax_rate
        
        # Gifting strategy
        annual_gifting_capacity = len(self.members) * annual_gift_exclusion
        
        # Annual gifting to reduce estate
        years_to_gift = 20  # Planning horizon
        total_gifting_potential = annual_gifting_capacity * years_to_gift
        
        # GRAT strategy
        grat_discount = gross_estate * 0.20  # Assume 20% valuation discount
        
        # Charitable strategies
        charitable_deduction = gross_estate * 0.30  # Assume 30% to charity
        tax_savings_charity = charitable_deduction * estate_tax_rate
        
        return {
            "gross_estate": round(gross_estate, 0),
            "estate_tax_exemption": round(total_exemption, 0),
            "taxable_estate": round(taxable_estate, 0),
            "estimated_estate_tax": round(estimated_tax, 0),
            "effective_tax_rate": round((estimated_tax / gross_estate) * 100, 2) if gross_estate > 0 else 0,
            "strategies": {
                "annual_gifting": {
                    "annual_capacity": annual_gifting_capacity,
                    "20_year_potential": total_gifting_potential,
                    "tax_savings": round(total_gifting_potential * estate_tax_rate, 0)
                },
                "grat": {
                    "valuation_discount": round(grat_discount, 0),
                    "tax_savings": round(grat_discount * estate_tax_rate, 0)
                },
                "charitable": {
                    "donation_amount": round(charitable_deduction, 0),
                    "tax_savings": round(tax_savings_charity, 0)
                }
            },
            "total_potential_savings": round(
                (total_gifting_potential * estate_tax_rate) + 
                (grat_discount * estate_tax_rate) + 
                tax_savings_charity, 0
            ),
            "net_estate_after_planning": round(gross_estate - estimated_tax + 
                (total_gifting_potential * estate_tax_rate) + 
                (grat_discount * estate_tax_rate) + 
                tax_savings_charity, 0)
        }
    
    def family_constitution_recommendations(self) -> Dict:
        """Recommend family governance structure"""
        num_generations = len(set(m.generation for m in self.members))
        
        if num_generations >= 3:
            governance = {
                "structure": "FAMILY_COUNCIL_WITH_BOARD",
                "components": [
                    "Family Assembly (all members)",
                    "Family Council (decision making)",
                    "Investment Committee",
                    "Next Generation Education Program"
                ],
                "meeting_frequency": "Quarterly council, Annual assembly",
                "succession_planning": "MANDATORY"
            }
        elif num_generations == 2:
            governance = {
                "structure": "FAMILY_COUNCIL",
                "components": [
                    "Family Council",
                    "Investment Oversight",
                    "Education Initiatives"
                ],
                "meeting_frequency": "Quarterly",
                "succession_planning": "RECOMMENDED"
            }
        else:
            governance = {
                "structure": "DIRECT_MANAGEMENT",
                "components": ["Family Head", "External Advisors"],
                "meeting_frequency": "As needed",
                "succession_planning": "OPTIONAL"
            }
        
        return {
            "family_name": self.family_name,
            "num_members": len(self.members),
            "num_generations": num_generations,
            "governance": governance,
            "key_documents_needed": [
                "Family Constitution",
                "Investment Policy Statement",
                "Estate Plan",
                "Succession Plan",
                "Philanthropic Mission Statement"
            ] if num_generations >= 2 else ["Estate Plan", "Investment Policy"]
        }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate complete family office report"""
        return {
            "family_profile": {
                "name": self.family_name,
                "aum": self.total_aum,
                "members": len(self.members),
                "generations": len(set(m.generation for m in self.members))
            },
            "generational_allocation": self.calculate_generational_allocation(),
            "wealth_preservation": self.calculate_heritage_preservation(),
            "estate_planning": self.estate_planning_analysis(),
            "governance": self.family_constitution_recommendations(),
            "legacy_goals": self.legacy_goals,
            "recommended_actions": self._generate_action_items()
        }
    
    def _generate_action_items(self) -> List[str]:
        """Generate recommended action items"""
        items = []
        
        if self.total_aum > 100e6:
            items.append("Establish formal family governance structure")
        
        if len(self.members) > 5:
            items.append("Create next-generation education program")
        
        estate = self.estate_planning_analysis()
        if estate["estimated_estate_tax"] > 1e6:
            items.append("Implement comprehensive estate planning strategy")
            items.append("Consider GRAT and annual gifting programs")
        
        preservation = self.calculate_heritage_preservation()
        if preservation["preservation_probability"] == "LOW":
            items.append("Review spending rates to ensure multi-generational sustainability")
        
        items.append("Draft Investment Policy Statement")
        items.append("Establish regular family meetings")
        
        return items
