#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the double comma issue
content = content.replace('},,', '},')

with open('deploy_comprehensive_multi_cloud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed double comma in deploy_comprehensive_multi_cloud.py")
