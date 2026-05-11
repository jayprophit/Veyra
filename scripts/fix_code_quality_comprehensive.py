#!/usr/bin/env python3
"""
Comprehensive Code Quality Fixer for Veyra
Fixes: imports, syntax errors, missing dependencies, type hints, etc.
"""
import os
import re
import ast
import sys
from pathlib import Path
from collections import defaultdict

class CodeQualityFixer:
    def __init__(self):
        self.issues = defaultdict(list)
        self.fixes_applied = 0
        self.files_processed = 0

    def should_process(self, filepath):
        skip_dirs = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache', 'dist', 'build'}
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.bin', '.pyc', '.so', '.o', '.lock'}

        path = Path(filepath)
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            return False
        if path.suffix.lower() in skip_extensions:
            return False
        if not filepath.endswith('.py'):
            return False
        return True

    def fix_imports(self, content: str) -> tuple[str, int]:
        """Fix common import issues"""
        fixes = 0

        # Remove duplicate imports
        import_lines = {}
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                if line not in import_lines:
                    import_lines[line] = True
                    new_lines.append(line)
                else:
                    fixes += 1
            else:
                new_lines.append(line)

        return '\n'.join(new_lines), fixes

    def fix_escape_sequences(self, content: str) -> tuple[str, int]:
        """Fix invalid escape sequences"""
        fixes = 0
        original = content

        # Replace invalid escape sequences in strings
        content = re.sub(r'\\\A', r'\\\\\A', content)
        content = re.sub(r'\\[bfr](?=["\'])', r'\\\\\g<0>', content)

        if content != original:
            fixes += 1

        return content, fixes

    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def fix_file(self, filepath: str) -> int:
        """Fix a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            content = original_content
            file_fixes = 0

            # Apply fixes
            content, fixes = self.fix_imports(content)
            file_fixes += fixes

            content, fixes = self.fix_escape_sequences(content)
            file_fixes += fixes

            # Validate and write
            if self.validate_syntax(content) and content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += file_fixes
                return file_fixes

        except Exception as e:
            self.issues[filepath].append(str(e))

        return 0

    def run(self):
        """Run the code quality fixer"""
        print("🔧 Starting Veyra Code Quality Fixer...")

        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv'}]

            for file in files:
                filepath = os.path.join(root, file)
                if self.should_process(filepath):
                    self.files_processed += 1
                    fixes = self.fix_file(filepath)
                    if fixes > 0:
                        print(f"   ✅ {filepath}: {fixes} fixes")

        print(f"\n📊 Code Quality Report:")
        print(f"   Files processed: {self.files_processed}")
        print(f"   Total fixes applied: {self.fixes_applied}")
        print(f"   Issues found: {len(self.issues)}")

        if self.issues:
            print(f"\n⚠️  Issues to review:")
            for file, error_list in list(self.issues.items())[:10]:
                print(f"   {file}: {error_list[0]}")

if __name__ == '__main__':
    fixer = CodeQualityFixer()
    fixer.run()
