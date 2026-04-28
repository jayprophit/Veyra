"""NFT Valuation - NFT pricing and analytics"""
from typing import Dict, List

class NFTValuation:
    """Value NFTs and analyze collections"""
    
    def floor_price_analysis(self, recent_sales: List[float]) -> Dict:
        """Calculate floor price metrics"""
        if not recent_sales:
            return {"floor": 0, "avg": 0}
        
        floor = min(recent_sales)
        avg = sum(recent_sales) / len(recent_sales)
        median = sorted(recent_sales)[len(recent_sales) // 2]
        
        return {
            "floor_price": floor,
            "average_price": round(avg, 3),
            "median_price": median,
            "sales_count": len(recent_sales),
            "premium_to_floor": round((avg / floor - 1) * 100, 1) if floor > 0 else 0
        }
    
    def rarity_score(self, trait_counts: Dict[str, int],
                    total_supply: int) -> Dict:
        """Calculate NFT rarity score"""
        scores = {}
        total_score = 0
        
        for trait, count in trait_counts.items():
            rarity = 1 / (count / total_supply) if count > 0 else 0
            scores[trait] = round(rarity, 2)
            total_score += rarity
        
        return {
            "rarity_score": round(total_score, 2),
            "trait_scores": scores,
            "rarity_tier": "legendary" if total_score > 100 else "epic" if total_score > 50 else "rare" if total_score > 20 else "common"
        }
    
    def nft_valuation(self, floor_price: float,
                     rarity_multiplier: float,
                     collection_premium: float) -> Dict:
        """Calculate NFT fair value"""
        base_value = floor_price
        adjusted = base_value * rarity_multiplier * (1 + collection_premium)
        
        return {
            "floor_price": floor_price,
            "rarity_adj": rarity_multiplier,
            "collection_premium": collection_premium,
            "fair_value": round(adjusted, 3),
            "max_bid": round(adjusted * 0.95, 3)
        }
    
    def wash_trading_detection(self, trades: List[Dict]) -> Dict:
        """Detect suspicious wash trading"""
        suspicious = 0
        
        for i, trade in enumerate(trades):
            if i > 0:
                time_diff = trade.get("timestamp", 0) - trades[i-1].get("timestamp", 0)
                same_buyer_seller = trade.get("buyer") == trades[i-1].get("seller")
                
                if time_diff < 60 and same_buyer_seller:  # Within 60 seconds
                    suspicious += 1
        
        total = len(trades)
        wash_ratio = suspicious / total if total > 0 else 0
        
        return {
            "total_trades": total,
            "suspicious_wash_trades": suspicious,
            "wash_ratio": round(wash_ratio * 100, 2),
            "risk_level": "high" if wash_ratio > 0.3 else "medium" if wash_ratio > 0.1 else "low"
        }
