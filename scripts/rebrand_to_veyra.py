#!/usr/bin/env python3
"""
Comprehensive Veyra Rebranding Tool
Replaces all "Veyra" references with "Veyra"
"""
import os
import re
from pathlib import Path

def should_process_file(filepath):
    """Check if file should be processed"""
    skip_dirs = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache', '.coverage'}
    skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.bin', '.pyc', '.so', '.o'}

    path = Path(filepath)
    if any(skip_dir in path.parts for skip_dir in skip_dirs):
        return False
    if path.suffix.lower() in skip_extensions:
        return False
    return True

def rebrand_content(content: str) -> tuple[str, int]:
    """Replace Veyra with Veyra in content"""
    count = 0

    # Replace variations of Veyra
    replacements = [
        (r'\bFinancial\s+Master\\\b', 'Veyra'),  # Veyra
        (r'\bfinancial\s+master\\\b', 'veyra'),  # veyra
        (r'\bfinancial-master\\\b', 'veyra'),    # veyra
        (r'\bfinancial_master\\\b', 'veyra'),    # veyra
        (r'\bFinancialMaster\\\b', 'Veyra'),     # Veyra
        (r'\bfinancialmaster\\\b', 'veyra'),     # veyra
        (r'\bFINANCIAL_MASTER\\\b', 'VEYRA'),    # VEYRA
        (r'\bfm\\\b', 'vra'),                    # vra -> vra
    ]

    for pattern, replacement in replacements:
        new_content, replacements_count = re.subn(pattern, replacement, content)
        if new_content != content:
            content = new_content
            count += replacements_count

    return content, count

def process_file(filepath):
    """Process a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        new_content, count = rebrand_content(original_content)

        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return count
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return 0

def main():
    """Main rebrand function"""
    total_replacements = 0
    total_files = 0

    for root, dirs, files in os.walk('.'):
        # Remove skipped directories from traversal
        dirs[:] = [d for d in dirs if d not in {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv'}]

        for file in files:
            filepath = os.path.join(root, file)
            if should_process_file(filepath):
                total_files += 1
                replacements = process_file(filepath)
                if replacements > 0:
                    print(f"✅ {filepath}: {replacements} replacements")
                    total_replacements += replacements

    print(f"\n📊 Rebranding Summary:")
    print(f"   Files processed: {total_files}")
    print(f"   Total replacements: {total_replacements}")
    print(f"✅ Rebrand to Veyra complete!")

if __name__ == '__main__':
    main()
