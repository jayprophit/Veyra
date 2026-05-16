"""Decentralized Platforms - Web3 content monetization"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Web3Platform:
    name: str
    blockchain: str
    token: str
    revenue_models: List[str]
    fee_pct: float

class DecentralizedPlatformManager:
    """Manage Web3 creator platforms"""
    
    PLATFORMS = {
        "odysee": Web3Platform("Odysee (LBRY)", "LBRY", "LBC", ["tips", "supports"], 5.0),
        "lens": Web3Platform("Lens Protocol", "Polygon", "None", ["collects", "mirrors"], 0.0),
        "farcaster": Web3Platform("Farcaster", "Optimism", "None", ["tips", "frames"], 0.0),
        "audius": Web3Platform("Audius", "Audius", "AUDIO", ["streaming", "tips"], 0.0),
        "steemit": Web3Platform("Steemit", "Steem", "STEEM", ["upvotes", "curation"], 0.0),
        "mirror": Web3Platform("Mirror.xyz", "Ethereum", "None", ["nft_drops", "crowdfund"], 2.5),
        "zora": Web3Platform("Zora", "Ethereum", "None", ["mint_fees", "rewards"], 0.0),
        "friend_tech": Web3Platform("Friend.tech", "Base", "None", ["keys", "fees"], 10.0),
        "theta": Web3Platform("Theta Network", "Theta", "THETA", ["streaming", "staking"], 0.0),
        "deso": Web3Platform("Diamond App (DeSo)", "DeSo", "DESO", ["diamonds", "nft"], 0.0),
    }
    
    def get_platform(self, name: str) -> Web3Platform:
        return self.PLATFORMS.get(name.lower())
    
    def list_by_chain(self, blockchain: str) -> List[str]:
        return [n for n, p in self.PLATFORMS.items() if p.blockchain.lower() == blockchain.lower()]
    
    def compare_fees(self) -> Dict:
        return {name: p.fee_pct for name, p in self.PLATFORMS.items()}
