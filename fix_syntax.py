#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r') as f:
    content = f.read()

# Fix the missing comma after cognitive_services
old_text = """                "features": ["Pre-trained models", "Custom training", "Real-time APIs"]
                }"""
new_text = """                "features": ["Pre-trained models", "Custom training", "Real-time APIs"]
                },"""

content = content.replace(old_text, new_text)

with open('deploy_comprehensive_multi_cloud.py', 'w') as f:
    f.write(content)

print("Fixed missing comma in deploy_comprehensive_multi_cloud.py")
