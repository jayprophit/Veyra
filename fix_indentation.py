#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the indentation issue
old_text = """                "security": {
                "azure_security_center": {"""
new_text = """                "security": {
                    "azure_security_center": {"""

content = content.replace(old_text, new_text)

# Also fix the closing brace indentation
content = content.replace("""                }
            }""", """                }
                }
            }""")

with open('deploy_comprehensive_multi_cloud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed indentation issue in deploy_comprehensive_multi_cloud.py")
