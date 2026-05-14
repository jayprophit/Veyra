"""Power BI & Tableau Connector
==============================
Export data to Microsoft Power BI and Tableau for visualization.
"""
import pandas as pd
import json
from typing import Dict, List, Optional
from datetime import datetime

class PowerBIConnector:
    """Export portfolio data to Power BI"""
    
    def __init__(self):
        self.datasets = {}
    
    def export_portfolio(self, portfolio_data: Dict) -> str:
        """Export portfolio to Power BI JSON format"""
        pbix_data = {
            "name": "Veyra Portfolio",
            "tables": [
                {
                    "name": "Holdings",
                    "columns": [
                        {"name": "symbol", "dataType": "string"},
                        {"name": "quantity", "dataType": "double"},
                        {"name": "price", "dataType": "double"},
                        {"name": "value", "dataType": "double"},
                        {"name": "asset_class", "dataType": "string"}
                    ],
                    "rows": [
                        [h["symbol"], h["quantity"], h["price"], h["value"], h.get("type", "stock")]
                        for h in portfolio_data.get("holdings", [])
                    ]
                },
                {
                    "name": "Performance",
                    "columns": [
                        {"name": "date", "dataType": "dateTime"},
                        {"name": "daily_pnl", "dataType": "double"},
                        {"name": "total_value", "dataType": "double"}
                    ],
                    "rows": portfolio_data.get("performance_history", [])
                }
            ]
        }
        return json.dumps(pbix_data, indent=2)
    
    def create_dax_measures(self) -> List[Dict]:
        """Create DAX measures for Power BI"""
        return [
            {
                "name": "Total Portfolio Value",
                "expression": "SUM(Holdings[value])",
                "format": "Currency"
            },
            {
                "name": "Daily Return %",
                "expression": "DIVIDE(SUM(Performance[daily_pnl]), [Total Portfolio Value], 0)",
                "format": "Percentage"
            },
            {
                "name": "Asset Allocation",
                "expression": "DIVIDE(SUM(Holdings[value]), [Total Portfolio Value], 0)",
                "format": "Percentage"
            }
        ]
    
    def export_to_csv_for_powerbi(self, data: Dict, filename: str = "portfolio.csv"):
        """Export to CSV for Power BI import"""
        df = pd.DataFrame(data.get("holdings", []))
        df.to_csv(filename, index=False)
        return filename


class TableauConnector:
    """Export data to Tableau format (.hyper or .tde)"""
    
    def __init__(self):
        self.extracts = {}
    
    def create_hyper_extract(self, data: Dict) -> bytes:
        """Create Tableau Hyper extract"""
        # Simulated Hyper format (would use tableauhyperapi in production)
        tableau_data = {
            "schema": "Veyra",
            "tables": {
                "Portfolio": data.get("holdings", []),
                "Trades": data.get("trades", []),
                "Performance": data.get("performance", [])
            }
        }
        return json.dumps(tableau_data).encode()
    
    def generate_tdsx(self, server_url: str, datasource_name: str) -> str:
        """Generate Tableau datasource XML"""
        tds_xml = f"""<?xml version='1.0'?>
<datasource formatted-name='{datasource_name}'>
  <connection class='sqlserver' server='{server_url}'>
    <relation name='Portfolio' connection='sqlserver'>
      SELECT * FROM portfolio_holdings
    </relation>
  </connection>
  <column name='symbol' datatype='string' />
  <column name='value' datatype='real' />
  <column name='return_pct' datatype='real' />
</datasource>"""
        return tds_xml


class UnifiedBIConnector:
    """Unified connector for all BI platforms"""
    
    SUPPORTED_PLATFORMS = ["powerbi", "tableau", "qlik", "looker"]
    
    def __init__(self):
        self.connectors = {
            "powerbi": PowerBIConnector(),
            "tableau": TableauConnector()
        }
    
    def export(self, platform: str, data: Dict) -> Optional[str]:
        """Export to specified BI platform"""
        if platform not in self.SUPPORTED_PLATFORMS:
            return None
        
        if platform == "powerbi":
            return self.connectors["powerbi"].export_portfolio(data)
        elif platform == "tableau":
            return self.connectors["tableau"].generate_tdsx(
                "localhost", "Veyra"
            )
        
        return None
    
    def auto_sync(self, platforms: List[str], interval_minutes: int = 60):
        """Auto-sync data to multiple platforms"""
        return {
            "platforms": platforms,
            "interval": interval_minutes,
            "last_sync": datetime.now().isoformat(),
            "status": "configured"
        }
