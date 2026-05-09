#!/usr/bin/env python3

with open('src/backend/app/ai/biometric_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic function and fix indentation
old_function = '''def _simulate_variation(self) -> float:
        """Simulate natural biometric variation (-1 to 1)."""
        import random
        return random.gauss(0, 0.5)'''

new_function = '''    def _simulate_variation(self) -> float:
        """Simulate natural biometric variation (-1 to 1)."""
        import random
        return random.gauss(0, 0.5)'''

content = content.replace(old_function, new_function)

with open('src/backend/app/ai/biometric_monitor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comprehensive fix applied to biometric_monitor.py")
