#!/usr/bin/env python3
"""
Financial Master - Critical Fixes Automation Script
Addresses: Logging, Exception Handling, Code Quality
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, List

class CodeQualityFixer:
    def __init__(self, root_dir: str = "src"):
        self.root_dir = root_dir
        self.stats = {
            'print_replaced': 0,
            'bare_except_fixed': 0,
            'files_processed': 0,
        }
        self.dry_run_mode = True

    def fix_print_statements(self, file_path: str) -> bool:
        """Replace print() calls with logger calls"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content

            # Replace print statements with logger.info calls
            # Pattern: print(f"...") or print("...")
            patterns = [
                (r'print\(f"([^"]*)"\)', r'logger.info(f"\1")'),
                (r"print\(f'([^']*)'\)", r"logger.info(f'\1')"),
                (r'print\("([^"]*)"\)', r'logger.info("\1")'),
                (r"print\('([^']*)'\)", r"logger.info('\1')"),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original:
                self.stats['print_replaced'] += content.count('logger.info') - original.count('logger.info')
                if not self.dry_run_mode:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing prints in {file_path}: {e}")

        return False

    def fix_bare_exceptions(self, file_path: str) -> bool:
        """Fix bare except clauses"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            original_lines = lines.copy()
            i = 0
            while i < len(lines):
                line = lines[i]
                # Match bare except:
                if re.match(r'\s*except\s*:', line):
                    # Re place with specific exception
                    indent = len(line) - len(line.lstrip())
                    insert_line = ' ' * indent + 'except Exception as e:\n'
                    insert_line += ' ' * indent + '    logger.error("unexpected_error", exc_info=True)\n'
                    lines[i] = insert_line
                    self.stats['bare_except_fixed'] += 1
                i += 1

            if lines != original_lines and not self.dry_run_mode:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing exceptions in {file_path}: {e}")

        return False

    def add_type_hints(self, file_path: str) -> bool:
        """Add type hints to functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple pattern: def function_name(param)
            pattern = r'def\s+(\w+)\s*\(([^)]*)\)\s*:'

            count = 0
            for match in re.finditer(pattern, content):
                # Check if already has return type hint
                if '->' not in match.group(0):
                    count += 1

            if count > 0 and not self.dry_run_mode:
                # This would require more sophisticated AST parsing in production
                pass

            return count > 0

        except Exception as e:
            print(f"Error analyzing types in {file_path}: {e}")

        return False

    def process_directory(self):
        """Process all Python files in directory"""
        print(f"Starting code quality fixes (DRY RUN: {self.dry_run_mode})")
        print("=" * 70)

        python_files = list(Path(self.root_dir).rglob("*.py"))
        print(f"Found {len(python_files)} Python files")

        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue

            self.stats['files_processed'] += 1

            print(f"Processing: {py_file}")

            self.fix_print_statements(str(py_file))
            self.fix_bare_exceptions(str(py_file))

            if self.stats['files_processed'] % 100 == 0:
                print(f"  Progress: {self.stats['files_processed']}/{len(python_files)}")

        self.print_summary()

    def print_summary(self):
        """Print summary of fixes"""
        print("\n" + "=" * 70)
        print("CODE QUALITY FIX SUMMARY")
        print("=" * 70)
        print(f"Files Processed: {self.stats['files_processed']}")
        print(f"Print Statements Fixed: {self.stats['print_replaced']}")
        print(f"Bare Exceptions Fixed: {self.stats['bare_except_fixed']}")

        print("\nNext Steps:")
        print("1. Run tests to validate fixes")
        print("2. Review git diff for changes")
        print("3. Set --dry-run=False to apply changes")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix code quality issues")
    parser.add_argument("--dry-run", type=bool, default=True,
                        help="Dry run mode (no file changes)")
    parser.add_argument("--root", type=str, default="src",
                        help="Root directory to process")

    args = parser.parse_args()

    fixer = CodeQualityFixer(root_dir=args.root)
    fixer.dry_run_mode = args.dry_run
    fixer.process_directory()
