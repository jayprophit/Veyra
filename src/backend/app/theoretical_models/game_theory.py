"""Game Theory Models for Trading"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Player(Enum):
    MARKET_MAKER = "market_maker"
    INSTITUTION = "institution"
    RETAIL = "retail"
    ALGO = "algorithmic"

class Strategy(Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"
    TIT_FOR_TAT = "tit_for_tat"
    GRIM_TRIGGER = "grim_trigger"

@dataclass
class PayoffMatrix:
    player1_strategy: Strategy
    player2_strategy: Strategy
    player1_payoff: float
    player2_payoff: float

class GameTheoryAnalyzer:
    """Apply game theory to trading decisions"""
    
    def __init__(self):
        self.players = [p.value for p in Player]
    
    def prisoners_dilemma_trade(self, 
                               player1_payoff: Dict[str, float],
                               player2_payoff: Dict[str, float]) -> Dict:
        """Analyze trade as prisoner's dilemma"""
        # Payoff matrix: (Cooperate, Defect)
        # Cooperate = share liquidity, Defect = front-run
        
        matrix = {
            (Strategy.COOPERATE, Strategy.COOPERATE): (3, 3),    # Both win
            (Strategy.COOPERATE, Strategy.DEFECT): (0, 5),       # Sucker payoff
            (Strategy.DEFECT, Strategy.COOPERATE): (5, 0),       # Temptation
            (Strategy.DEFECT, Strategy.DEFECT): (1, 1)           # Both lose
        }
        
        # Nash equilibrium
        nash = (Strategy.DEFECT, Strategy.DEFECT)
        
        # Pareto optimal
        pareto = (Strategy.COOPERATE, Strategy.COOPERATE)
        
        return {
            "nash_equilibrium": nash[0].value,
            "pareto_optimal": pareto[0].value,
            "dilemma": "Individual rationality leads to suboptimal group outcome",
            "trading_implication": "Without enforcement, expect front-running",
            "solution": "Repeated games enable cooperation via Tit-for-Tat"
        }
    
    def zero_sum_analysis(self, market_participants: List[Dict]) -> Dict:
        """Analyze zero-sum aspects of trading"""
        total_profit = sum(p.get("profit", 0) for p in market_participants)
        
        # In pure zero-sum, total should be 0 (minus transaction costs)
        transaction_costs = sum(p.get("volume", 0) * 0.001 for p in market_participants)
        
        zero_sum_check = abs(total_profit + transaction_costs) < 0.01
        
        winners = [p for p in market_participants if p.get("profit", 0) > 0]
        losers = [p for p in market_participants if p.get("profit", 0) < 0]
        
        return {
            "is_zero_sum": zero_sum_check,
            "total_pnl": round(total_profit, 2),
            "transaction_costs": round(transaction_costs, 2),
            "winner_count": len(winners),
            "loser_count": len(losers),
            "concentration": "HIGH" if len(winners) < len(losers) / 2 else "MODERATE",
            "implication": "Market is zero-sum; your gain is another's loss"
        }
    
    def nash_equilibrium_price(self, buyers: List[Dict], sellers: List[Dict]) -> Dict:
        """Find Nash equilibrium price"""
        # Simplified: intersection of supply and demand
        
        buy_prices = sorted([b["max_price"] for b in buyers], reverse=True)
        sell_prices = sorted([s["min_price"] for s in sellers])
        
        # Find clearing price
        equilibrium = None
        for buy in buy_prices:
            for sell in sell_prices:
                if buy >= sell:
                    equilibrium = (buy + sell) / 2
                    break
            if equilibrium:
                break
        
        if not equilibrium:
            return {"equilibrium": None, "market_state": "No trade zone"}
        
        # Calculate surplus
        buyer_surplus = sum(b["max_price"] - equilibrium for b in buyers if b["max_price"] > equilibrium)
        seller_surplus = sum(equilibrium - s["min_price"] for s in sellers if s["min_price"] < equilibrium)
        
        return {
            "equilibrium_price": round(equilibrium, 2),
            "buyer_surplus": round(buyer_surplus, 2),
            "seller_surplus": round(seller_surplus, 2),
            "total_welfare": round(buyer_surplus + seller_surplus, 2),
            "trades_executed": min(len([b for b in buyers if b["max_price"] > equilibrium]),
                                  len([s for s in sellers if s["min_price"] < equilibrium]))
        }
    
    def auction_theory_optimal_bid(self, 
                                  valuation: float,
                                  num_competitors: int,
                                  auction_type: str = "second_price") -> Dict:
        """Calculate optimal bid using auction theory"""
        
        if auction_type == "second_price":
            # In second-price (Vickrey), bid your true value
            optimal_bid = valuation
            strategy = "Bid true valuation"
            expected_profit = valuation - (valuation * 0.9)  # Assume 2nd bid at 90%
        
        elif auction_type == "first_price":
            # In first-price, shade your bid
            optimal_bid = valuation * (1 - 1/num_competitors)
            strategy = f"Shade bid by {100/num_competitors:.0f}%"
            expected_profit = valuation - optimal_bid
        
        else:
            optimal_bid = valuation * 0.95
            strategy = "Conservative shading"
            expected_profit = valuation * 0.05
        
        return {
            "optimal_bid": round(optimal_bid, 2),
            "true_valuation": valuation,
            "strategy": strategy,
            "expected_profit": round(expected_profit, 2),
            "win_probability": f"{100/num_competitors:.0f}%" if num_competitors > 0 else "N/A"
        }
