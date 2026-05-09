"""Analyze actual vs regex-counted endpoints in the API directory."""
import re
from pathlib import Path

api_dir = Path('src/backend/app/api')

print("=" * 70)
print("ENDPOINT ANALYSIS - Actual FastAPI Routes vs Regex Count")
print("=" * 70)

total_regex = 0
total_explicit = 0
total_loop = 0

for py_file in sorted(api_dir.glob('*.py')):
    if py_file.name == '__init__.py':
        continue
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count all decorator lines (regex method)
        regex_count = len(re.findall(r'@\w+\.(get|post|put|delete|patch)', content))
        
        # Count loop-based endpoints (inside for loops)
        # Find for loops that contain router decorators
        loop_pattern = r'for\s+\w+\s+in\s+range\(\d+\):[^@]*?@router\.\w+'
        loop_matches = re.findall(loop_pattern, content, re.DOTALL)
        
        # Count range values in loops with decorators
        range_pattern = r'for\s+\w+\s+in\s+range\((\d+)\):\s*\n\s*@router'
        range_matches = re.findall(range_pattern, content)
        loop_endpoint_count = sum(int(r) for r in range_matches)
        
        # Explicit endpoints = regex count - loop count (each loop registers 1, not N)
        # But regex counts each @router line including those in loops
        # Actually loops generate N decorator lines but only 1 registered route
        
        # Count lines inside for loops that have decorators
        lines = content.split('\n')
        in_loop = False
        loop_decorators = 0
        explicit_decorators = 0
        loop_indent = 0
        
        for line in lines:
            stripped = line.strip()
            if re.match(r'for\s+\w+\s+in\s+range\(', stripped):
                in_loop = True
                # Get indent level of for statement
                loop_indent = len(line) - len(line.lstrip())
                continue
            
            if in_loop:
                current_indent = len(line) - len(line.lstrip()) if stripped else loop_indent + 1
                # If we're back at or below the for loop indent, we've exited the loop
                if stripped and current_indent <= loop_indent:
                    in_loop = False
                
                if re.match(r'@\w+\.(get|post|put|delete|patch)', stripped):
                    loop_decorators += 1
                continue
            
            if re.match(r'@\w+\.(get|post|put|delete|patch)', stripped):
                explicit_decorators += 1
        
        # Actual registered routes: explicit + 1 per loop (not N per loop)
        actual_routes = explicit_decorators + (1 if loop_decorators > 0 else 0)
        
        total_regex += regex_count
        total_explicit += explicit_decorators
        total_loop += loop_decorators
        
        if regex_count > 0:
            gap = regex_count - actual_routes
            print(f"  {py_file.name}: regex={regex_count}, explicit={explicit_decorators}, loop_decorators={loop_decorators}, actual_routes~={actual_routes}, gap={gap}")
    except Exception as e:
        print(f"  Error: {py_file.name}: {e}")

print(f"\n{'='*70}")
print(f"TOTAL REGEX COUNT: {total_regex}")
print(f"TOTAL EXPLICIT ENDPOINTS: {total_explicit}")
print(f"TOTAL LOOP DECORATORS: {total_loop}")
print(f"ACTUAL REGISTERED ROUTES: ~{total_explicit + 1} (each file with loops registers 1 loop route)")
print(f"GAP: {total_regex - total_explicit - 1} phantom endpoints from loops")
