#!/usr/bin/env python3

with open('src/backend/app/ai/biometric_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the indentation issue on line 283
old_line = '    def _simulate_variation(self) -> float:'
new_line = '    def _simulate_variation(self) -> float:'

content = content.replace(old_line, new_line)

with open('src/backend/app/ai/biometric_monitor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed indentation issue in biometric_monitor.py")
