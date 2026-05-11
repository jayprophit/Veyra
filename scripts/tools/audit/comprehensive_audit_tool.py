#!/usr/bin/env python3
"""
Veyra - Comprehensive Codebase Audit Tool
==================================================
Systematic testing of all files, folders, and components for consistency and errors.
"""

import os
import sys
import ast
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
import importlib.util
import logging

# Try to import yaml, but don't fail if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class ComprehensiveAuditor:
    """Comprehensive auditor for Veyra codebase"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            'python_files': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'javascript_files': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'config_files': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'scripts': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'documentation': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'dependencies': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'imports': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []},
            'structure': {'checked': 0, 'errors': 0, 'warnings': 0, 'details': []}
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('comprehensive_audit.log')
            ]
        )
        self.logger = logging.getLogger('ComprehensiveAuditor')
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete audit of all codebase components"""
        self.logger.info("Starting comprehensive Veyra audit...")
        
        # 1. Check Python files
        self.audit_python_files()
        
        # 2. Check JavaScript/TypeScript files
        self.audit_javascript_files()
        
        # 3. Check configuration files
        self.audit_config_files()
        
        # 4. Check shell scripts
        self.audit_scripts()
        
        # 5. Check documentation
        self.audit_documentation()
        
        # 6. Check dependencies
        self.audit_dependencies()
        
        # 7. Check imports
        self.audit_imports()
        
        # 8. Check project structure
        self.audit_project_structure()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def audit_python_files(self):
        """Audit all Python files for syntax and errors"""
        self.logger.info("Auditing Python files...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files.extend(self.project_root.rglob("*.pyw"))
        
        for py_file in python_files:
            if 'node_modules' in str(py_file) or '.git' in str(py_file):
                continue
                
            self.results['python_files']['checked'] += 1
            
            try:
                # Check syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                ast.parse(content)
                
                # Check for common issues
                issues = self.check_python_issues(content, py_file)
                
                if issues['errors']:
                    self.results['python_files']['errors'] += len(issues['errors'])
                    self.results['python_files']['details'].extend(issues['errors'])
                
                if issues['warnings']:
                    self.results['python_files']['warnings'] += len(issues['warnings'])
                    self.results['python_files']['details'].extend(issues['warnings'])
                    
            except SyntaxError as e:
                error_msg = f"Syntax Error in {py_file}: {e}"
                self.results['python_files']['errors'] += 1
                self.results['python_files']['details'].append(error_msg)
                self.logger.error(error_msg)
            except Exception as e:
                error_msg = f"Error reading {py_file}: {e}"
                self.results['python_files']['errors'] += 1
                self.results['python_files']['details'].append(error_msg)
                self.logger.error(error_msg)
    
    def check_python_issues(self, content: str, file_path: Path) -> Dict[str, List[str]]:
        """Check for common Python issues"""
        issues = {'errors': [], 'warnings': []}
        
        # Check for imports
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for problematic imports
            if line.startswith('from app.'):
                module_path = line.split()[1].split('.')[0]
                full_path = self.project_root / 'src' / 'backend' / 'app' / module_path
                if not full_path.exists() and module_path != '__main__':
                    issues['errors'].append(f"Line {i}: Import error - module '{module_path}' not found in {file_path}")
            
            # Check for undefined variables in common patterns
            if 'os.getenv(' in line and '.env' not in line:
                env_var = line.split('os.getenv(')[1].split(')')[0].strip('"\'')
                if env_var and env_var not in ['NODE_ENV', 'PORT', 'DATABASE_URL', 'REDIS_URL']:
                    issues['warnings'].append(f"Line {i}: Environment variable '{env_var}' might not be defined in {file_path}")
        
        return issues
    
    def audit_javascript_files(self):
        """Audit all JavaScript/TypeScript files"""
        self.logger.info("Auditing JavaScript/TypeScript files...")
        
        js_files = list(self.project_root.rglob("*.js"))
        js_files.extend(self.project_root.rglob("*.ts"))
        js_files.extend(self.project_root.rglob("*.jsx"))
        js_files.extend(self.project_root.rglob("*.tsx"))
        
        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.git' in str(js_file):
                continue
                
            self.results['javascript_files']['checked'] += 1
            
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax checks
                issues = self.check_javascript_issues(content, js_file)
                
                if issues['errors']:
                    self.results['javascript_files']['errors'] += len(issues['errors'])
                    self.results['javascript_files']['details'].extend(issues['errors'])
                
                if issues['warnings']:
                    self.results['javascript_files']['warnings'] += len(issues['warnings'])
                    self.results['javascript_files']['details'].extend(issues['warnings'])
                    
            except Exception as e:
                error_msg = f"Error reading {js_file}: {e}"
                self.results['javascript_files']['errors'] += 1
                self.results['javascript_files']['details'].append(error_msg)
    
    def check_javascript_issues(self, content: str, file_path: Path) -> Dict[str, List[str]]:
        """Check for common JavaScript issues"""
        issues = {'errors': [], 'warnings': []}
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for import issues
            if line.startswith('import ') and 'from' in line:
                from_part = line.split('from ')[1].strip().strip('"\'').strip(';')
                if from_part.startswith('./') or from_part.startswith('../'):
                    # Check relative import path
                    import_path = file_path.parent / from_part
                    if not import_path.exists():
                        issues['errors'].append(f"Line {i}: Import path '{from_part}' not found in {file_path}")
        
        return issues
    
    def audit_config_files(self):
        """Audit configuration files"""
        self.logger.info("Auditing configuration files...")
        
        config_extensions = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg', '*.conf']
        config_files = []
        
        for ext in config_extensions:
            config_files.extend(self.project_root.rglob(ext))
        
        for config_file in config_files:
            if 'node_modules' in str(config_file) or '.git' in str(config_file):
                continue
                
            self.results['config_files']['checked'] += 1
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validate based on file type
                if config_file.suffix == '.json':
                    json.loads(content)
                elif config_file.suffix in ['.yaml', '.yml']:
                    if HAS_YAML:
                        yaml.safe_load(content)
                    else:
                        # Skip YAML validation if yaml not available
                        pass
                elif config_file.suffix == '.toml':
                    # Basic TOML validation
                    if '[tool.' in content and ']' in content:
                        pass  # Basic check
                    
            except json.JSONDecodeError as e:
                error_msg = f"JSON Error in {config_file}: {e}"
                self.results['config_files']['errors'] += 1
                self.results['config_files']['details'].append(error_msg)
            except Exception as e:
                if HAS_YAML and 'yaml' in str(type(e).__name__).lower():
                    error_msg = f"YAML Error in {config_file}: {e}"
                    self.results['config_files']['errors'] += 1
                    self.results['config_files']['details'].append(error_msg)
                else:
                    error_msg = f"Error reading {config_file}: {e}"
                    self.results['config_files']['errors'] += 1
                    self.results['config_files']['details'].append(error_msg)
    
    def audit_scripts(self):
        """Audit shell scripts and executables"""
        self.logger.info("Auditing scripts...")
        
        script_files = list(self.project_root.rglob("*.sh"))
        script_files.extend(self.project_root.rglob("*.ps1"))
        script_files.extend(self.project_root.rglob("*.bat"))
        
        for script_file in script_files:
            if 'node_modules' in str(script_file) or '.git' in str(script_file):
                continue
                
            self.results['scripts']['checked'] += 1
            
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common script issues
                issues = self.check_script_issues(content, script_file)
                
                if issues['errors']:
                    self.results['scripts']['errors'] += len(issues['errors'])
                    self.results['scripts']['details'].extend(issues['errors'])
                
                if issues['warnings']:
                    self.results['scripts']['warnings'] += len(issues['warnings'])
                    self.results['scripts']['details'].extend(issues['warnings'])
                    
            except Exception as e:
                error_msg = f"Error reading {script_file}: {e}"
                self.results['scripts']['errors'] += 1
                self.results['scripts']['details'].append(error_msg)
    
    def check_script_issues(self, content: str, file_path: Path) -> Dict[str, List[str]]:
        """Check for common script issues"""
        issues = {'errors': [], 'warnings': []}
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for potentially dangerous commands
            if line.startswith('rm -rf /') or line.startswith('sudo rm'):
                issues['warnings'].append(f"Line {i}: Potentially dangerous command in {file_path}")
            
            # Check for missing error handling
            if line.startswith('cd ') and '||' not in line and line.endswith('cd ' + line.split('cd ')[1]):
                issues['warnings'].append(f"Line {i}: Missing error handling for cd command in {file_path}")
        
        return issues
    
    def audit_documentation(self):
        """Audit documentation files"""
        self.logger.info("Auditing documentation...")
        
        doc_files = list(self.project_root.rglob("*.md"))
        doc_files.extend(self.project_root.rglob("*.rst"))
        doc_files.extend(self.project_root.rglob("*.txt"))
        
        for doc_file in doc_files:
            if 'node_modules' in str(doc_file) or '.git' in str(doc_file):
                continue
                
            self.results['documentation']['checked'] += 1
            
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for broken links
                issues = self.check_documentation_issues(content, doc_file)
                
                if issues['errors']:
                    self.results['documentation']['errors'] += len(issues['errors'])
                    self.results['documentation']['details'].extend(issues['errors'])
                
                if issues['warnings']:
                    self.results['documentation']['warnings'] += len(issues['warnings'])
                    self.results['documentation']['details'].extend(issues['warnings'])
                    
            except Exception as e:
                error_msg = f"Error reading {doc_file}: {e}"
                self.results['documentation']['errors'] += 1
                self.results['documentation']['details'].append(error_msg)
    
    def check_documentation_issues(self, content: str, file_path: Path) -> Dict[str, List[str]]:
        """Check for documentation issues"""
        issues = {'errors': [], 'warnings': []}
        
        # Check for broken internal links
        import re
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for text, link in links:
            if link.startswith('http'):
                continue  # External links
            
            # Check internal file links
            if link.startswith('./') or link.startswith('../'):
                link_path = file_path.parent / link
                if not link_path.exists():
                    issues['errors'].append(f"Broken link: '{link}' in {file_path}")
        
        return issues
    
    def audit_dependencies(self):
        """Audit dependency files"""
        self.logger.info("Auditing dependencies...")
        
        dep_files = ['requirements.txt', 'package.json', 'Pipfile', 'poetry.lock', 'yarn.lock']
        
        for dep_file in dep_files:
            file_path = self.project_root / dep_file
            if not file_path.exists():
                continue
                
            self.results['dependencies']['checked'] += 1
            
            try:
                if dep_file == 'requirements.txt':
                    self.check_requirements_txt(file_path)
                elif dep_file == 'package.json':
                    self.check_package_json(file_path)
                    
            except Exception as e:
                error_msg = f"Error checking {dep_file}: {e}"
                self.results['dependencies']['errors'] += 1
                self.results['dependencies']['details'].append(error_msg)
    
    def check_requirements_txt(self, file_path: Path):
        """Check requirements.txt file"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for invalid format
            if '==' not in line and '>=' not in line and '<=' not in line and '>' not in line and '<' not in line:
                self.results['dependencies']['warnings'].append(f"Unpinned dependency: {line} in {file_path}")
    
    def check_package_json(self, file_path: Path):
        """Check package.json file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ['name', 'version', 'dependencies']
        for field in required_fields:
            if field not in data:
                self.results['dependencies']['errors'].append(f"Missing field '{field}' in {file_path}")
    
    def audit_imports(self):
        """Audit import consistency"""
        self.logger.info("Auditing imports...")
        
        # Check main Python files for import consistency
        main_files = [
            'src/backend/app/main.py',
            'src/backend/app/api_server.py'
        ]
        
        for main_file in main_files:
            file_path = self.project_root / main_file
            if not file_path.exists():
                continue
                
            self.results['imports']['checked'] += 1
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module_name = node.module
                        if module_name and module_name.startswith('app.'):
                            # Check if the imported module exists
                            module_path = self.project_root / 'src' / 'backend' / module_name.replace('.', '/') + '.py'
                            if not module_path.exists():
                                # Check if it's a package
                                package_path = self.project_root / 'src' / 'backend' / module_name.replace('.', '/')
                                if not package_path.exists():
                                    self.results['imports']['errors'].append(f"Import module not found: {module_name} in {file_path}")
                    
            except Exception as e:
                error_msg = f"Error checking imports in {file_path}: {e}"
                self.results['imports']['errors'] += 1
                self.results['imports']['details'].append(error_msg)
    
    def audit_project_structure(self):
        """Audit project structure consistency"""
        self.logger.info("Auditing project structure...")
        
        # Check critical directories
        critical_dirs = [
            'src/backend',
            'src/frontend',
            'src/mobile',
            'docs',
            'scripts',
            'config'
        ]
        
        for dir_path in critical_dirs:
            full_path = self.project_root / dir_path
            self.results['structure']['checked'] += 1
            
            if not full_path.exists():
                self.results['structure']['errors'].append(f"Missing critical directory: {dir_path}")
            elif not full_path.is_dir():
                self.results['structure']['errors'].append(f"Path is not directory: {dir_path}")
        
        # Check critical files
        critical_files = [
            'README.md',
            'src/backend/requirements.txt',
            'src/frontend/package.json',
            'docker-compose.yml',
            '.env.example'
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            self.results['structure']['checked'] += 1
            
            if not full_path.exists():
                self.results['structure']['errors'].append(f"Missing critical file: {file_path}")
    
    def generate_summary(self):
        """Generate comprehensive audit summary"""
        self.logger.info("Generating audit summary...")
        
        total_checked = sum(result['checked'] for result in self.results.values())
        total_errors = sum(result['errors'] for result in self.results.values())
        total_warnings = sum(result['warnings'] for result in self.results.values())
        
        summary = f"""
# Veyra - Comprehensive Audit Report

## Summary
- **Total Files Checked**: {total_checked}
- **Total Errors**: {total_errors}
- **Total Warnings**: {total_warnings}
- **Status**: {'PASS' if total_errors == 0 else 'FAIL'}

## Detailed Results

"""
        
        for category, result in self.results.items():
            if result['checked'] > 0:
                status = 'PASS' if result['errors'] == 0 else 'FAIL'
                summary += f"### {category.replace('_', ' ').title()}\n"
                summary += f"- Status: {status}\n"
                summary += f"- Checked: {result['checked']}\n"
                summary += f"- Errors: {result['errors']}\n"
                summary += f"- Warnings: {result['warnings']}\n\n"
        
        # Add error details
        if total_errors > 0:
            summary += "## Error Details\n\n"
            for category, result in self.results.items():
                if result['details']:
                    summary += f"### {category.replace('_', ' ').title()}\n"
                    for detail in result['details']:
                        summary += f"- {detail}\n"
                    summary += "\n"
        
        # Save summary
        with open(self.project_root / 'AUDIT_REPORT.md', 'w') as f:
            f.write(summary)
        
        self.logger.info(f"Audit complete: {total_errors} errors, {total_warnings} warnings")
        
        return summary

def main():
    """Main audit function"""
    auditor = ComprehensiveAuditor()
    results = auditor.run_full_audit()
    
    # Print summary
    total_errors = sum(result['errors'] for result in results.values())
    total_warnings = sum(result['warnings'] for result in results.values())
    
    print(f"\n{'='*60}")
    print("FINANCIAL MASTER - COMPREHENSIVE AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Status: {'PASS' if total_errors == 0 else 'FAIL'}")
    print(f"Detailed report saved to: AUDIT_REPORT.md")
    print(f"{'='*60}")
    
    return total_errors == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
