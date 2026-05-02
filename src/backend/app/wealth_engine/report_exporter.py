import csv
import json

class ReportExporter:
    def to_csv(self, data, filename):
        if not data:
            return
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return filename
    
    def to_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    
    def generate_summary(self, simulation_data):
        lines = [
            'WEALTH SIMULATION REPORT',
            f\"Final Capital: £{simulation_data.get('final', 0):,.2f}\",
            f\"Total Contributed: £{simulation_data.get('contributed', 0):,.2f}\",
            f\"Total Return: £{simulation_data.get('gain', 0):,.2f}\",
        ]
        return '\n'.join(lines)

if __name__ == '__main__':
    from escalation_sim import EscalationSim
    sim = EscalationSim()
    result = sim.simulate(20, 100, 5)
    
    exporter = ReportExporter()
    print(exporter.generate_summary(result))
    csv_file = exporter.to_csv([{'month': i, 'value': i*100} for i in range(5)], 'test.csv')
    print(f'Exported: {csv_file}')