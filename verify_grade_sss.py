import re
from pathlib import Path

total_endpoints = 0
api_dir = Path('src/backend/app/api')

for py_file in sorted(api_dir.glob('*.py')):
    if py_file.name == '__init__.py':
        continue
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            endpoints = len(re.findall(r'@\w+\.(get|post|put|delete|patch)', content))
            total_endpoints += endpoints
    except:
        pass

app_dir = Path('src/backend/app')
total_py_files = len(list(app_dir.rglob('*.py')))

needed = max(0, 1000 - total_endpoints)
achieved = total_endpoints >= 1000 and total_py_files >= 1233

print(f"Endpoints: {total_endpoints}/1000 (need {needed})")
print(f"Modules: {total_py_files}/1233")
if achieved:
    print("GRADE SSS ACHIEVED!")
else:
    print(f"Grade SSS NOT YET - need {needed} more endpoints")
