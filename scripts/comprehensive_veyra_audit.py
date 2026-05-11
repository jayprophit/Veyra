#!/usr/bin/env python3
"""
Comprehensive Veyra Platform Audit
Analyzes: modules, API endpoints, services, architecture, gaps
"""
import os
import json
import re
from pathlib import Path
from collections import defaultdict

class VeyraAudit:
    def __init__(self):
        self.modules = []
        self.api_endpoints = []
        self.services = []
        self.integrations = []
        self.capabilities = defaultdict(list)
        self.issues = []

    def scan_modules(self):
        """Scan for all Python modules"""
        for root, dirs, files in os.walk('./src/backend/app'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_path = os.path.relpath(os.path.join(root, file))
                    module_name = module_path.replace('./src/backend/app/', '').replace('.py', '').replace('/', '.')
                    self.modules.append({
                        'name': module_name,
                        'path': module_path,
                        'filename': file
                    })

    def scan_api_endpoints(self):
        """Scan for API endpoints"""
        for root, dirs, files in os.walk('./src/backend/app/api'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Find route definitions
                            routes = re.findall(r'@(?:app|router|bp)\.(?:get|post|put|delete|patch|options)\(["\'](/[^"\']*)["\']', content)
                            self.api_endpoints.extend(routes)
                    except:
                        pass

    def scan_services(self):
        """Scan for service implementations"""
        service_patterns = {
            'Trading': ['trading', 'trade'],
            'Portfolio': ['portfolio'],
            'Risk Management': ['risk'],
            'Analytics': ['analytics'],
            'Data Provider': ['data_providers'],
            'Authentication': ['security', 'auth'],
            'Blockchain': ['blockchain', 'web3'],
            'AI/ML': ['ai', 'ml'],
            'Database': ['database'],
            'APIs': ['api'],
            'Monitoring': ['monitoring', 'observability'],
            'Compliance': ['compliance'],
            'Education': ['education'],
            'NLP': ['sentiment', 'nlp'],
            'DeFi': ['defi'],
            'Wealth': ['wealth'],
            'Treasury': ['treasury'],
            'Institutional': ['institutional'],
        }

        for module in self.modules:
            for service_name, patterns in service_patterns.items():
                for pattern in patterns:
                    if pattern in module['name'].lower():
                        self.services.append({
                            'service': service_name,
                            'module': module['name']
                        })
                        break

    def scan_integrations(self):
        """Scan for external integrations"""
        integrations_path = './src/backend/integrations'
        if os.path.exists(integrations_path):
            for item in os.listdir(integrations_path):
                if os.path.isdir(os.path.join(integrations_path, item)):
                    self.integrations.append(item)

    def analyze_capabilities(self):
        """Analyze platform capabilities"""
        capabilities = {
            'Core Trading': ['trading/', 'exchange'],
            'Automated Trading': ['strategy/', 'bot'],
            'Portfolio Management': ['portfolio/', 'optimization'],
            'Risk Analytics': ['risk/', 'analytics'],
            'AI Intelligence': ['ai/', 'ml/', 'agents'],
            'Blockchain': ['blockchain/', 'web3', 'defi'],
            'Data Integration': ['integrations/', 'data_providers'],
            'Visualizations': ['charts', 'dashboards'],
            'Database': ['database/', 'models'],
            'APIs': ['api/'],
            'Mobile Support': ['mobile'],
            'Desktop Support': ['desktop'],
        }

        for root, dirs, files in os.walk('./src'):
            for file in files:
                filepath = os.path.relpath(os.path.join(root, file))
                for cap, keywords in capabilities.items():
                    for keyword in keywords:
                        if keyword in filepath:
                            if filepath not in self.capabilities[cap]:
                                self.capabilities[cap].append(filepath)

    def print_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("🔍 VEYRA PLATFORM COMPREHENSIVE AUDIT REPORT")
        print("="*80)

        print(f"\n📦 MODULE INVENTORY")
        print(f"   Total modules: {len(self.modules)}")
        print(f"   Top modules:")
        for mod in sorted(self.modules, key=lambda x: x['name'])[:20]:
            print(f"      • {mod['name']}")

        print(f"\n🔌 API ENDPOINTS")
        unique_endpoints = len(set(self.api_endpoints))
        print(f"   Total unique endpoints: {unique_endpoints}")
        if unique_endpoints > 0:
            print(f"   Sample endpoints:")
            for endpoint in sorted(set(self.api_endpoints))[:15]:
                print(f"      • {endpoint}")

        print(f"\n🎯 SERVICES")
        service_counts = defaultdict(int)
        for item in self.services:
            service_counts[item['service']] += 1

        print(f"   Total services: {len(service_counts)}")
        for service, count in sorted(service_counts.items(), key=lambda x: -x[1]):
            print(f"      • {service}: {count} modules")

        print(f"\n🔗 INTEGRATIONS")
        print(f"   Total integrations: {len(self.integrations)}")
        for integration in sorted(self.integrations):
            print(f"      • {integration}")

        print(f"\n💪 CAPABILITIES")
        for cap, items in sorted(self.capabilities.items()):
            print(f"   {cap}: {len(items)} components")

        print(f"\n✅ AUDIT SUMMARY")
        print(f"   • {len(self.modules)} modules")
        print(f"   • {unique_endpoints} API endpoints")
        print(f"   • {len(self.integrations)} integrations")
        print(f"   • {len(self.services)} service mappings")
        print(f"   • {len(self.capabilities)} capability areas")

        print("\n" + "="*80)

    def run(self):
        print("\n🚀 Starting Veyra Platform Audit...")
        print("   Scanning modules...")
        self.scan_modules()
        print(f"   ✅ Found {len(self.modules)} modules")

        print("   Scanning API endpoints...")
        self.scan_api_endpoints()
        print(f"   ✅ Found {len(set(self.api_endpoints))} unique endpoints")

        print("   Scanning services...")
        self.scan_services()

        print("   Scanning integrations...")
        self.scan_integrations()

        print("   Analyzing capabilities...")
        self.analyze_capabilities()

        self.print_report()

if __name__ == '__main__':
    audit = VeyraAudit()
    audit.run()
