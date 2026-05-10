#!/usr/bin/env python3
"""
Automated Code Quality Fixer
Replaces print() with logging and fixes bare except clauses
"""
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

class CodeFixer:
    def __init__(self, root_dir="/workspaces/Financial-Master/src/backend"):
        self.root_dir = Path(root_dir)
        self.stats = defaultdict(int)
        self.changes = []

    def fix_print_statements(self, content: str, filename: str) -> str:
        """Replace print() with logger calls"""
        original = content

        # Pattern 1: print("msg") → logger.info("msg")
        content = re.sub(
            r'print\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'logger.info("\1")',
            content
        )

        # Pattern 2: print(f"msg {var}") → logger.info(f"msg {var}")
        content = re.sub(
            r'print\s*\(\s*f["\']([^"\']+)["\']\s*\)',
            r'logger.info(f"\1")',
            content
        )

        # Pattern 3: print(var) → logger.debug(f"Debug: {var}")
        content = re.sub(
            r'print\s*\(\s*(\w+)\s*\)',
            r'logger.debug(f"Debug: {\1}")',
            content
        )

        if content != original:
            self.stats['print_statements_fixed'] += len(re.findall(r'logger\.(?:info|debug|error)', content)) - \
                                                   len(re.findall(r'logger\.(?:info|debug|error)', original))
            self.stats['files_modified_prints'] += 1

        return content

    def fix_bare_exceptions(self, content: str, filename: str) -> str:
        """Fix bare except clauses"""
        original = content

        # Pattern: except:\n → except Exception as e:\n
        content = re.sub(
            r'except\s*:\s*\n',
            'except Exception as e:\n    logger.error("Exception occurred", exc_info=e)\n',
            content
        )

        if content != original:
            self.stats['bare_exceptions_fixed'] += 1
            self.stats['files_modified_exceptions'] += 1

        return content

    def ensure_logger_import(self, content: str) -> str:
        """Ensure module has logger import"""
        if 'logger' not in content or 'get_logger' not in content:
            # Add import at top of file
            if 'import logging' not in content:
                content = 'import logging\nlogger = logging.getLogger(__name__)\n\n' + content
                self.stats['logger_imports_added'] += 1

        return content

    def process_file(self, filepath: Path) -> bool:
        """Process a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            content = original_content

            # Skip test files for now
            if 'test_' in filepath.name or filepath.parent.name == 'tests':
                return False

            # Apply fixes
            content = self.fix_print_statements(content, filepath.name)
            content = self.fix_bare_exceptions(content, filepath.name)

            # Only add logger if we made changes involving logging
            if 'logger.' in content and 'logger = ' not in content and 'get_logger' not in content:
                content = self.ensure_logger_import(content)

            # Write back if changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.changes.append(str(filepath.relative_to(self.root_dir.parent)))
                self.stats['files_fixed'] += 1
                return True

            return False

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            self.stats['errors'] += 1
            return False

    def run(self):
        """Run fixer on all Python files"""
        print("=" * 60)
        print("Financial Master - Automated Code Quality Fixer")
        print("=" * 60)
        print()

        # Find all Python files
        py_files = list(self.root_dir.rglob("*.py"))
        print(f"Found {len(py_files)} Python files")
        print()

        # Process files
        for i, py_file in enumerate(py_files, 1):
            if self.process_file(py_file):
                print(f"[{i}/{len(py_files)}] ✅ Fixed {py_file.name}")
            else:
                if i % 50 == 0:
                    print(f"[{i}/{len(py_files)}] Processed...")

        # Print report
        print()
        print("=" * 60)
        print("AUTOMATED FIX REPORT")
        print("=" * 60)
        print(f"Files fixed: {self.stats['files_fixed']}")
        print(f"Files modified for prints: {self.stats['files_modified_prints']}")
        print(f"Files modified for exceptions: {self.stats['files_modified_exceptions']}")
        print(f"Print statements fixed: {self.stats['print_statements_fixed']}")
        print(f"Bare exceptions fixed: {self.stats['bare_exceptions_fixed']}")
        print(f"Logger imports added: {self.stats['logger_imports_added']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print()

        if self.changes:
            print(f"Modified files ({len(self.changes)}):")
            for f in self.changes[:20]:  # Show first 20
                print(f"  - {f}")
            if len(self.changes) > 20:
                print(f"  ... and {len(self.changes) - 20} more")

        return len(self.changes)

if __name__ == "__main__":
    fixer = CodeFixer()
    count = fixer.run()
    sys.exit(0 if count > 0 else 1)
