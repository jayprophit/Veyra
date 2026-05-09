#!/usr/bin/env python3

with open('deploy_comprehensive_multi_cloud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all the indentation issues in the JSON structure
fixes = [
    # Fix storage section ending
    ('"features": ["Long-term storage", "Data retrieval options"]\n                }\n            }\n            },',
     '"features": ["Long-term storage", "Data retrieval options"]\n                }\n            },'),
    
    # Fix database section indentation
    ('            }\n            },\n            "database": {',
     '            },\n            },\n            "database": {'),
    
    # Fix any remaining structural issues
    ('                }\n            }\n            },',
     '                }\n            },'),
]

for old_text, new_text in fixes:
    content = content.replace(old_text, new_text)

# Fix the entire structure by ensuring proper JSON formatting
lines = content.split('\n')
fixed_lines = []
indent_level = 0

for line in lines:
    stripped = line.strip()
    if stripped.startswith('}'):
        indent_level = max(0, indent_level - 1)
    
    if stripped:
        fixed_lines.append('    ' * indent_level + stripped)
    else:
        fixed_lines.append('')
    
    if stripped.endswith('{'):
        indent_level += 1

content = '\n'.join(fixed_lines)

with open('deploy_comprehensive_multi_cloud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all indentation issues in deploy_comprehensive_multi_cloud.py")
