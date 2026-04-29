"""GitHub Analyzer - Repository and developer analytics"""
from typing import Dict
from datetime import datetime

class GitHubAnalyzer:
    """Analyze GitHub repositories for investment signals"""
    
    def repo_valuation(self, stars: int,
                      forks: int,
                      contributors: int,
                      days_since_update: int) -> Dict:
        """Value open source project based on metrics"""
        # Network effect valuation
        star_value = stars * 0.5  # $0.50 per star
        fork_value = forks * 2.0  # $2 per fork (more engagement)
        contributor_value = contributors * 50  # $50 per active contributor
        
        total_value = star_value + fork_value + contributor_value
        
        # Decay factor for stale repos
        if days_since_update > 90:
            decay = 0.7
        elif days_since_update > 30:
            decay = 0.9
        else:
            decay = 1.0
        
        return {
            "network_value": round(total_value, 0),
            "adjusted_value": round(total_value * decay, 0),
            "community_health": "strong" if contributors > 10 else "moderate" if contributors > 3 else "weak",
            "activity_status": "active" if days_since_update < 7 else "stale" if days_since_update > 60 else "moderate",
            "engagement_score": round((stars + forks * 5) / max(contributors, 1), 1)
        }
    
    def developer_velocity(self, commits_per_week: float,
                          pr_merge_rate: float,
                          issue_resolution_days: float) -> Dict:
        """Measure development team velocity"""
        velocity_score = (commits_per_week * 10 + 
                        pr_merge_rate * 50 - 
                        issue_resolution_days * 2)
        
        return {
            "velocity_score": round(velocity_score, 1),
            "productivity_grade": "A" if velocity_score > 80 else "B" if velocity_score > 60 else "C",
            "commits_per_week": commits_per_week,
            "efficiency": "high" if pr_merge_rate > 0.8 else "medium" if pr_merge_rate > 0.5 else "low",
            "maintenance_burden": "low" if issue_resolution_days < 7 else "high" if issue_resolution_days > 30 else "medium"
        }
    
    def tokenomics_analysis(self, project_type: str,
                           token_supply: float,
                           staking_rate: float,
                           burn_rate: float) -> Dict:
        """Analyze tokenomics for crypto projects"""
        inflation = 100 - staking_rate
        deflationary_score = burn_rate * 100
        
        return {
            "inflation_rate": round(inflation, 2),
            "deflationary_pressure": round(deflationary_score, 2),
            "token_health": "strong" if deflationary_score > inflation else "inflationary",
            "project_type": project_type,
            "supply_stress": "low" if staking_rate > 60 else "medium" if staking_rate > 30 else "high"
        }
