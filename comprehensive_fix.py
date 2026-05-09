#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix multiple indentation and syntax issues
fixes = [
    # Fix storage section indentation
    ('                }\n                }', '                }\n            }'),
    
    # Fix azure_security_center indentation
    ('                "security": {\n                "azure_security_center": {', 
     '                "security": {\n                    "azure_security_center": {'),
    
    # Fix any remaining double commas
    ('},,', '},'),
    
    # Fix missing commas after closing braces in various sections
    ('"features": ["Long-term storage", "Data retrieval options"]\n                }\n                }', 
     '"features": ["Long-term storage", "Data retrieval options"]\n                }\n            },'),
]

for old_text, new_text in fixes:
    content = content.replace(old_text, new_text)

with open('deploy_comprehensive_multi_cloud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied comprehensive syntax fixes to deploy_comprehensive_multi_cloud.py")
