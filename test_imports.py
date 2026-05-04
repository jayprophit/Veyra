#!/usr/bin/env python3
"""Test module imports to identify failures"""
import sys

modules = [
    'app.alternative_investments.commodity_tracker',
    'app.arbitrage.merger_arbitrage', 
    'app.behavioral_finance.bias_detector'
]

failed = []
for mod in modules:
    try:
        __import__(mod)
        print(f'✓ {mod}')
    except Exception as e:
        print(f'✗ {mod}: {e}')
        failed.append((mod, str(e)))

print(f'\nFailed: {len(failed)}')
for mod, err in failed:
    print(f'  - {mod}: {err}')
