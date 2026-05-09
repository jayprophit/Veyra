#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the storage section indentation and extra brace
old_section = """                "lambda": {
                    "description": "Serverless compute",
                    "components": ["Lambda Functions", "API Gateway", "EventBridge"],
                    "cost_range": "$5-100/month",
                    "features": ["Event-driven", "Pay-per-use", "Auto-scaling"]
                }
            }
            },
            "storage": {"""

new_section = """                "lambda": {
                    "description": "Serverless compute",
                    "components": ["Lambda Functions", "API Gateway", "EventBridge"],
                    "cost_range": "$5-100/month",
                    "features": ["Event-driven", "Pay-per-use", "Auto-scaling"]
                },
            },
            "storage": {"""

content = content.replace(old_section, new_section)

with open('deploy_comprehensive_multi_cloud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed storage section indentation and extra brace")
