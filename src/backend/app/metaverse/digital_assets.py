"""Digital Assets and NFT Economics"""
from typing import Dict

class DigitalAssets:
    """Valuation models for digital collectibles and NFTs"""
    
    def __init__(self, asset_type: str = "collectible"):
        self.asset_type = asset_type  # collectible, gaming, utility, art
    
    def valuation_framework(self) -> Dict:
        factors = {
            "scarcity": 0.30,  # Total supply, unique attributes
            "utility": 0.25,   # In-game use, access, rewards
            "community": 0.20,  # Holder engagement, brand strength
            "history": 0.15,    # Provenance, first-of-kind
            "aesthetics": 0.10  # Visual appeal, design
        }
        
        return {
            "valuation_factors": factors,
            "price_floor": "Minimum market price",
            "price_ceiling": "Rarest comparable sale",
            "liquidity_premium": "Higher for active collections",
            "speculative_premium": "Expectations of future value"
        }
    
    def collection_economics(self, collection_size: int = 10000) -> Dict:
        # Typical PFP collection
        mint_price = 0.1  # ETH
        eth_price = 3000  # USD
        
        mint_revenue = collection_size * mint_price * eth_price
        
        # Royalties (secondary sales)
        secondary_volume_yearly = mint_revenue * 2  # 2x turnover
        royalty_rate = 0.05
        royalty_revenue = secondary_volume_yearly * royalty_rate
        
        # Team allocation (typical 20%)
        team_holdings = collection_size * 0.20
        
        return {
            "collection_size": collection_size,
            "mint_price_eth": mint_price,
            "mint_revenue_usd": mint_revenue,
            "annual_royalty_revenue": royalty_revenue,
            "team_allocation": team_holdings,
            "total_first_year_revenue": mint_revenue + royalty_revenue
        }
    
    def gaming_assets(self, item_type: str = "sword") -> Dict:
        gaming_items = {
            "sword": {"base_price": 10, "power_level": 100, "rarity": "common"},
            "legendary_armor": {"base_price": 500, "power_level": 1000, "rarity": "legendary"},
            "land_plot": {"base_price": 1000, "power_level": 0, "rarity": "unique"},
            "character": {"base_price": 50, "power_level": 50, "rarity": "varies"}
        }
        
        item = gaming_items.get(item_type, gaming_items["sword"])
        
        return {
            "item_type": item_type,
            "base_price_usd": item["base_price"],
            "rarity_multiplier": {"common": 1, "rare": 5, "legendary": 50, "unique": 200}[item["rarity"]],
            "utility_value": f"Power level: {item['power_level']}",
            "market_liquidity": "High for common, low for legendary"
        }
    
    def investment_returns(self) -> Dict:
        return {
            "blue_chip_collections": {
                "crypto_punks": "Launched free, floor peaked 150 ETH",
                "bored_apes": "0.08 ETH mint, floor peaked 150 ETH",
                "art_blocks": "0.08-5 ETH mint, some 1000+ ETH sales"
            },
            "typical_returns": {
                "winners": "10-100x for successful projects",
                "average": "Break even to 2x",
                "losers": "90% decline to zero"
            },
            "risk_factors": [
                "Platform risk (ETH gas, L2 migration)",
                "Regulatory risk (securities classification)",
                "Market risk (crypto correlation)",
                "Project risk (rug pull, abandonment)"
            ]
        }
