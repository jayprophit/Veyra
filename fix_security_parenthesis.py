#!/usr/bin/env python3

with open('src/backend/app/api/security_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the missing closing parenthesis on line 547
old_line = '        raise HTTPException(status_code=500, detail(str(e))'
new_line = '        raise HTTPException(status_code=500, detail=str(e))'

content = content.replace(old_line, new_line)

with open('src/backend/app/api/security_api.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed missing parenthesis in security_api.py")
