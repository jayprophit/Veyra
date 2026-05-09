#!/usr/bin/env python3

with open('src/backend/app/ai/biometric_monitor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the indentation issue on line 283
for i, line in enumerate(lines):
    if 'def _simulate_variation(self) -> float:' in line:
        lines[i] = '    def _simulate_variation(self) -> float:\n'
        break

with open('src/backend/app/ai/biometric_monitor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed final indentation issue in biometric_monitor.py")
