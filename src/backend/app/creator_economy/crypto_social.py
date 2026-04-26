"""Crypto Social Earnings - Web3 social monetization, tokens, NFTs, tips"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class CryptoPlatform(Enum):
    LENS = "lens"; FARCASTER = "farcaster"; DESO = "deso"
    MIRROR = "mirror"; ZORA = "zora"; SOUND = "sound"
    RODEO = "rodeo"; DRakks = "drakks"; FriendTech = "friendtech"
    STARS_ARENA = "stars_arena"; POST_TECH = "post_tech"

@dataclass
class CryptoEarning:
    platform: CryptoPlatform; amount_eth: Decimal
    amount_usd: Decimal; earning_type: str
    date: date; token_price_eth: Decimal

class CryptoSocialEarnings:
    """Track Web3 social media earnings and NFT sales"""
    
    def __init__(self, eth_price: Decimal = Decimal("3500.00")):
        self.eth_price_usd = eth_price
        self.earnings: List[CryptoEarning] = []
        self.platform_configs = self._init_platforms()
        
    def _init_platforms(self):
        return {
            CryptoPlatform.LENS: {
                "token": "LENS",
                "monetization": ["collect_fees", "tips", "nft_posts"],
                "avg_earning_per_1k_followers": Decimal("0.01"),  # ETH
                "gas_cost_per_action": Decimal("0.0001"),
                "follower_quality": "high"
            },
            CryptoPlatform.FARCASTER: {
                "token": "DEGEN",
                "monetization": ["frame_actions", "tips", "nft_mints"],
                "avg_earning_per_1k_followers": Decimal("0.02"),
                "gas_cost_per_action": Decimal("0"),  # On Base L2, very low
                "follower_quality": "very_high"
            },
            CryptoPlatform.MIRROR: {
                "token": "ETH",
                "monetization": ["crowdfunding", "nft_essays", "splits"],
                "avg_earning_per_1000_reads": Decimal("0.05"),
                "gas_cost_per_publish": Decimal("0.001"),
                "follower_quality": "high"
            },
            CryptoPlatform.ZORA: {
                "token": "ETH",
                "monetization": ["nft_mints", "rewards"],
                "mint_fee": Decimal("0.000777"),
                "creator_reward_per_mint": Decimal("0.0004"),
                "follower_quality": "medium"
            },
            CryptoPlatform.SOUND: {
                "token": "ETH",
                "monetization": ["music_nfts", "royalties"],
                "avg_sale_price_eth": Decimal("0.05"),
                "platform_fee_pct": Decimal("0.15"),
                "follower_quality": "high"
            },
            CryptoPlatform.FriendTech: {
                "token": "ETH",
                "monetization": ["share_trading", "chat_fees"],
                "protocol_fee_pct": Decimal("0.10"),
                "creator_fee_pct": Decimal("0.05"),
                "follower_quality": "speculative"
            }
        }
    
    def calculate_lens_earnings(self, followers: int, 
                              posts_per_week: int = 5,
                              collect_rate: float = 0.01,
                              collect_price_eth: Decimal = Decimal("0.001")) -> Dict:
        """Calculate potential Lens Protocol earnings"""
        config = self.platform_configs[CryptoPlatform.LENS]
        
        weekly_posts = posts_per_week
        monthly_posts = weekly_posts * 4
        
        # Collects (people minting your posts as NFTs)
        total_monthly_collects = int(followers * collect_rate * monthly_posts)
        collect_revenue_eth = Decimal(total_monthly_collects) * collect_price_eth
        
        # Tips (assume 0.1% of followers tip avg 0.01 ETH/month)
        tips_eth = Decimal(followers * 0.001) * Decimal("0.01")
        
        # NFT posts (special content)
        nft_posts_monthly = 2
        nft_mints_per_post = int(followers * 0.005)
        nft_price = Decimal("0.005")
        nft_revenue_eth = Decimal(nft_posts_monthly * nft_mints_per_post) * nft_price
        
        total_eth = collect_revenue_eth + tips_eth + nft_revenue_eth
        
        # Gas costs
        gas_per_post = config["gas_cost_per_action"]
        monthly_gas = gas_per_post * Decimal(monthly_posts)
        
        net_eth = total_eth - monthly_gas
        net_usd = net_eth * self.eth_price_usd
        
        return {
            "platform": "Lens Protocol",
            "followers": followers,
            "monthly_posts": monthly_posts,
            "collects": total_monthly_collects,
            "collect_revenue_eth": float(collect_revenue_eth),
            "tips_eth": float(tips_eth),
            "nft_revenue_eth": float(nft_revenue_eth),
            "gross_eth": float(total_eth),
            "gas_costs_eth": float(monthly_gas),
            "net_eth": float(net_eth),
            "net_usd": float(net_usd),
            "annual_projection_usd": float(net_usd * 12)
        }
    
    def calculate_farcaster_earnings(self, followers: int,
                                     casts_per_day: int = 3,
                                     frame_engagement_rate: float = 0.05) -> Dict:
        """Calculate Farcaster/Degen earnings"""
        config = self.platform_configs[CryptoPlatform.FARCASTER]
        
        monthly_casts = casts_per_day * 30
        
        # Degen tips (very active tipping culture)
        avg_tips_per_cast = followers * 0.0005  # Small % tip
        avg_tip_amount = Decimal("50")  # ~50 DEGEN
        # Assume DEGEN at $0.01
        degen_price = Decimal("0.01")
        tip_revenue = Decimal(avg_tips_per_cast * monthly_casts) * avg_tip_amount * degen_price / self.eth_price_usd
        
        # Frame interactions (mini-apps in casts)
        frame_interactions = int(followers * frame_engagement_rate)
        frame_revenue_per_interaction = Decimal("0.0001")  # ETH
        frame_revenue = Decimal(frame_interactions) * frame_revenue_per_interaction
        
        # Allowlist/NFT mints
        allowlist_mints = int(followers * 0.01)
        mint_price = Decimal("0.01")
        mint_revenue = Decimal(allowlist_mints) * mint_price
        
        total_eth = tip_revenue + frame_revenue + mint_revenue
        total_usd = total_eth * self.eth_price_usd
        
        return {
            "platform": "Farcaster",
            "followers": followers,
            "monthly_casts": monthly_casts,
            "tip_revenue_eth": float(tip_revenue),
            "frame_revenue_eth": float(frame_revenue),
            "mint_revenue_eth": float(mint_revenue),
            "total_eth": float(total_eth),
            "total_usd": float(total_usd),
            "annual_usd": float(total_usd * 12)
        }
    
    def calculate_mirror_earnings(self, subscribers: int,
                                  essays_per_month: int = 2,
                                  crowdfunding_frequency: int = 1) -> Dict:
        """Calculate Mirror.xyz publishing earnings"""
        config = self.platform_configs[CryptoPlatform.MIRROR]
        
        # Essay NFTs
        readers_per_essay = subscribers * 0.3
        mint_rate = 0.02  # 2% of readers mint
        mints_per_month = int(readers_per_essay * mint_rate * essays_per_month)
        mint_price = Decimal("0.01")
        essay_revenue = Decimal(mints_per_month) * mint_price
        
        # Crowdfunding (1 per quarter = 0.33 per month average)
        cf_per_month = crowdfunding_frequency / 3
        avg_cf_goal = Decimal("3.0")  # ETH
        cf_success_rate = 0.7
        cf_revenue = Decimal(cf_per_month) * avg_cf_goal * Decimal(cf_success_rate)
        
        # Splits (revenue sharing with collaborators)
        split_income = Decimal("0.1")  # Assumed monthly from participating in splits
        
        total_eth = essay_revenue + cf_revenue + split_income
        gas_cost = config["gas_cost_per_publish"] * Decimal(essays_per_month)
        net_eth = total_eth - gas_cost
        
        return {
            "platform": "Mirror.xyz",
            "subscribers": subscribers,
            "essays_per_month": essays_per_month,
            "essay_nft_revenue_eth": float(essay_revenue),
            "crowdfunding_eth": float(cf_revenue),
            "splits_eth": float(split_income),
            "total_eth": float(total_eth),
            "gas_costs_eth": float(gas_cost),
            "net_eth": float(net_eth),
            "net_usd": float(net_eth * self.eth_price_usd),
            "annual_usd": float(net_eth * self.eth_price_usd * 12)
        }
    
    def social_token_launch(self, follower_count: int,
                          token_name: str = "CREATOR") -> Dict:
        """Calculate potential social token economics"""
        # Social tokens allow creators to monetize their community
        
        # Typical launch parameters
        total_supply = 10_000_000
        creator_allocation_pct = 20  # Creator gets 20%
        community_allocation_pct = 50  # 50% for community rewards/liquidity
        
        # Estimate initial market cap based on follower count
        # Rough heuristic: $0.10-$1.00 per 1000 engaged followers
        market_cap_per_1k = Decimal("0.50")
        estimated_market_cap = Decimal(follower_count / 1000) * market_cap_per_1k * 1000
        
        creator_tokens = int(total_supply * creator_allocation_pct / 100)
        creator_value = estimated_market_cap * Decimal(creator_allocation_pct / 100)
        
        # Revenue streams from token
        trading_fees_annual = estimated_market_cap * Decimal("0.20") * Decimal("0.003")  # 0.3% of 20% vol
        staking_rewards_annual = estimated_market_cap * Decimal("0.05")  # 5% yield on staked
        
        return {
            "token_name": token_name,
            "total_supply": total_supply,
            "creator_allocation_pct": creator_allocation_pct,
            "creator_tokens": creator_tokens,
            "estimated_initial_market_cap": float(estimated_market_cap),
            "creator_portfolio_value": float(creator_value),
            "trading_fee_revenue_annual": float(trading_fees_annual),
            "potential_staking_rewards": float(staking_rewards_annual),
            "platforms": ["Rally", "Roll", "Coinvise", "Bonfire"],
            "launch_cost_eth": 0.5,
            "risk_level": "high"
        }
    
    def compare_web3_platforms(self, followers: int = 5000) -> List[Dict]:
        """Compare all Web3 social platforms"""
        results = []
        
        lens = self.calculate_lens_earnings(followers)
        results.append({
            "platform": "Lens",
            "monthly_usd": lens["net_usd"],
            "annual_usd": lens["annual_projection_usd"],
            "difficulty": "medium",
            "audience": "Quality over quantity",
            "key_feature": "Own your content"
        })
        
        farcaster = self.calculate_farcaster_earnings(followers)
        results.append({
            "platform": "Farcaster",
            "monthly_usd": farcaster["total_usd"],
            "annual_usd": farcaster["annual_usd"],
            "difficulty": "easy",
            "audience": "Crypto-native",
            "key_feature": "Frames economy"
        })
        
        mirror = self.calculate_mirror_earnings(followers // 2)  # Subscribers, not followers
        results.append({
            "platform": "Mirror",
            "monthly_usd": mirror["net_usd"],
            "annual_usd": mirror["annual_usd"],
            "difficulty": "medium",
            "audience": "Writer-focused",
            "key_feature": "Crowdfunding"
        })
        
        # Sound.xyz for musicians
        results.append({
            "platform": "Sound.xyz",
            "monthly_usd": 500,  # Highly variable
            "annual_usd": 6000,
            "difficulty": "hard",
            "audience": "Music collectors",
            "key_feature": "Music NFTs"
        })
        
        return sorted(results, key=lambda x: x["annual_usd"], reverse=True)
    
    def get_airdrop_opportunities(self) -> List[Dict]:
        """Potential airdrops for active Web3 social users"""
        return [
            {
                "protocol": "Farcaster",
                "token": "DEGEN",
                "status": "active_farming",
                "estimated_value": 1000,
                "requirements": "Be active, get tips, tip others",
                "effort": "medium"
            },
            {
                "protocol": "Lens",
                "token": "LENS",
                "status": "rumored",
                "estimated_value": 2000,
                "requirements": "Collect posts, engagement",
                "effort": "medium"
            },
            {
                "protocol": "Zora",
                "token": "ZORA",
                "status": "confirmed_2024",
                "estimated_value": 500,
                "requirements": "Mint/collect NFTs",
                "effort": "low"
            },
            {
                "protocol": "Rainbow Wallet",
                "token": "RAIN",
                "status": "active",
                "estimated_value": 300,
                "requirements": "Use Rainbow, bridge assets",
                "effort": "low"
            }
        ]
    
    def nft_royalty_projections(self, collection_size: int = 10000,
                               mint_price_eth: Decimal = Decimal("0.05"),
                               royalty_pct: Decimal = Decimal("0.05")) -> Dict:
        """Calculate NFT royalty revenue projections"""
        # Primary sale
        primary_revenue = Decimal(collection_size) * mint_price_eth
        
        # Secondary market assumptions
        secondary_volume_yearly = primary_revenue * Decimal("2.5")  # 2.5x flip rate
        royalty_revenue_yearly = secondary_volume_yearly * royalty_pct
        
        # 3 year projection
        years = [1, 2, 3]
        projections = []
        
        for year in years:
            decay = Decimal("0.7") ** (year - 1)  # 30% decay per year
            vol = secondary_volume_yearly * decay
            royalty = vol * royalty_pct
            projections.append({
                "year": year,
                "secondary_volume_eth": float(vol),
                "royalty_revenue_eth": float(royalty),
                "royalty_revenue_usd": float(royalty * self.eth_price_usd)
            })
        
        return {
            "collection_size": collection_size,
            "mint_price_eth": float(mint_price_eth),
            "primary_revenue_eth": float(primary_revenue),
            "primary_revenue_usd": float(primary_revenue * self.eth_price_usd),
            "royalty_rate_pct": float(royalty_pct * 100),
            "projections": projections,
            "total_3_year_royalties_eth": sum(p["royalty_revenue_eth"] for p in projections),
            "total_3_year_royalties_usd": sum(p["royalty_revenue_usd"] for p in projections)
        }
