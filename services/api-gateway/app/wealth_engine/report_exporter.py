"""Report export utilities."""
import csv, json
from typing import Dict, List, Any

class ReportExporter:
    def to_csv(self, data: List[Dict], filename: str) -> str:
        if not data: return filename
        with open(filename, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)
        return filename

    def to_json(self, data: Any, filename: str) -> str:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return filename

    def generate_summary(self, d: Dict) -> str:
        return f"Final: {d.get('final', 0):,.2f}\nContributed: {d.get('contributed', 0):,.2f}\nGain: {d.get('gain', 0):,.2f}"