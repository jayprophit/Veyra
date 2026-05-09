#!/usr/bin/env python3

with open('src/backend/app/ai/biometric_monitor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the function definition issue
for i, line in enumerate(lines):
    if 'def _simulate_variation(self) -> float:' in line:
        # Replace with properly indented function including body
        lines[i] = '    def _simulate_variation(self) -> float:\n        """Simulate natural biometric variation (-1 to 1)."""\n        import random\n        return random.gauss(0, 0.5)\n'
        break

with open('src/backend/app/ai/biometric_monitor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Final comprehensive fix applied to biometric_monitor.py")
