"""DeFi Analyzer - Decentralized Finance protocols"""
from typing import Dict, List

class DeFiAnalyzer:
    """Analyze DeFi protocols and yield opportunities"""
    
    def yield_farming_apr(self, reward_tokens: float,
                       token_price: float,
                       tvl: float,
                       investment: float) -> Dict:
        """Calculate yield farming APR"""
        annual_rewards = reward_tokens * token_price * 365
        apr = (annual_rewards / tvl) * 100 if tvl > 0 else 0
        
        user_daily = (investment / tvl) * reward_tokens if tvl > 0 else 0
        user_annual = user_daily * 365 * token_price
        
        return {
            "protocol_apr": round(apr, 2),
            "daily_rewards_tokens": round(user_daily, 4),
            "annual_rewards_usd": round(user_annual, 2),
            "impermanent_risk": "high" if apr > 50 else "medium" if apr > 20 else "low"
        }
    
    def impermanent_loss(self, price_ratio: float) -> Dict:
        """Calculate impermanent loss vs HODL"""
        sqrt_ratio = price_ratio ** 0.5
        il = (2 * sqrt_ratio / (1 + price_ratio)) - 1
        
        return {
            "price_ratio": round(price_ratio, 3),
            "impermanent_loss_pct": round(abs(il) * 100, 2),
            "hodl_value": 1.0,
            "lp_value": round(1 + il, 4),
            "loss_vs_hodl": "yes" if il < 0 else "no"
        }
    
    def liquidity_mining_roi(self, deposit: float,
                           reward_per_day: float,
                           token_price: float,
                           days: int) -> Dict:
        """Calculate liquidity mining ROI"""
        total_rewards = reward_per_day * days * token_price
        roi = (total_rewards / deposit) * 100 if deposit > 0 else 0
        
        return {
            "deposit": deposit,
            "total_rewards_usd": round(total_rewards, 2),
            "roi_percent": round(roi, 2),
            "apy": round(roi * (365 / days), 2) if days > 0 else 0
        }
    
    def flash_loan_arbitrage(self, loan_amount: float,
                            price_exchange_a: float,
                            price_exchange_b: float,
                            fee_pct: float = 0.003) -> Dict:
        """Calculate flash loan arbitrage profit"""
        fee = loan_amount * fee_pct
        amount_after_fee = loan_amount - fee
        
        # Buy low, sell high
        if price_exchange_a < price_exchange_b:
            tokens = amount_after_fee / price_exchange_a
            revenue = tokens * price_exchange_b
        else:
            tokens = amount_after_fee / price_exchange_b
            revenue = tokens * price_exchange_a
        
        profit = revenue - loan_amount
        
        return {
            "loan_amount": loan_amount,
            "profit": round(profit, 2),
            "roi": round((profit / loan_amount) * 100, 4),
            "viable": profit > 0,
            "execution_complexity": "high"
        }
