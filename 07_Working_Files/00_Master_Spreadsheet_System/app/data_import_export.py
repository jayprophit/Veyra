"""Data Import/Export - CSV, Excel support"""

import pandas as pd
import csv
import io
from typing import Dict, List

class DataImportManager:
    """Import portfolio data from various formats"""
    
    def import_csv(self, content: str) -> Dict:
        """Import positions from CSV"""
        try:
            df = pd.read_csv(io.StringIO(content))
            required = ['symbol', 'shares']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                return {"success": False, "error": f"Missing: {missing}"}
            
            positions = []
            for _, row in df.iterrows():
                positions.append({
                    "symbol": str(row['symbol']).upper(),
                    "shares": float(row['shares']),
                    "cost_basis": float(row.get('cost_basis', 0))
                })
            
            return {
                "success": True,
                "positions": positions,
                "count": len(positions)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_excel(self, path: str) -> Dict:
        """Import from Excel with multiple sheets"""
        try:
            xls = pd.ExcelFile(path)
            results = []
            
            for sheet in xls.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet)
                result = self.import_csv(df.to_csv(index=False))
                results.append({"sheet": sheet, **result})
            
            return {"success": True, "sheets": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_portfolio_csv(
        self,
        positions: List[Dict],
        filename: str = "portfolio_export.csv"
    ) -> str:
        """Export positions to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['symbol', 'shares', 'cost_basis', 'current_price', 'value']
            )
            writer.writeheader()
            writer.writerows(positions)
        
        return filename

print("Data Import/Export loaded")
