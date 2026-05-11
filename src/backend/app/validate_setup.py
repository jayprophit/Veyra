"""Setup Validator - Check all prerequisites and system health."""

import subprocess
import sys
import os
import json
from datetime import datetime

class SetupValidator:
    """Validate Veyra setup."""
    
    def __init__(self):
        self.results = {}
        self.recommendations = []
    
    def check_python(self):
        """Check Python version."""
        version = sys.version_info
        ok = version >= (3, 11)
        self.results['python'] = {
            'ok': ok,
            'version': f"{version.major}.{version.minor}.{version.micro}",
            'message': "Python 3.11+ required" if not ok else "OK"
        }
        return ok
    
    def check_node(self):
        """Check Node.js."""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            ok = result.returncode == 0
            version = result.stdout.strip()
            self.results['node'] = {'ok': ok, 'version': version, 'message': 'OK' if ok else 'Node.js not found'}
            return ok
        except:
            self.results['node'] = {'ok': False, 'version': None, 'message': 'Node.js not found'}
            return False
    
    def check_ollama(self):
        """Check Ollama."""
        try:
            import requests
            r = requests.get('http://localhost:11434/api/tags', timeout=3)
            ok = r.status_code == 200
            models = [m['name'] for m in r.json().get('models', [])]
            self.results['ollama'] = {'ok': ok, 'models': models, 'message': f"{len(models)} models" if ok else "Not running"}
            return ok
        except:
            self.results['ollama'] = {'ok': False, 'models': [], 'message': 'Ollama not installed or not running'}
            return False
    
    def check_docker(self):
        """Check Docker."""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            ok = result.returncode == 0
            self.results['docker'] = {'ok': ok, 'message': 'OK' if ok else 'Docker not found'}
            return ok
        except:
            self.results['docker'] = {'ok': False, 'message': 'Docker not found'}
            return False
    
    def check_wsl(self):
        """Check WSL2."""
        try:
            result = subprocess.run(['wsl', '--status'], capture_output=True, text=True)
            ok = result.returncode == 0
            self.results['wsl'] = {'ok': ok, 'message': 'WSL2 available' if ok else 'WSL not installed'}
            return ok
        except:
            self.results['wsl'] = {'ok': False, 'message': 'WSL not installed'}
            return False
    
    def check_git(self):
        """Check Git."""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            ok = result.returncode == 0
            self.results['git'] = {'ok': ok, 'version': result.stdout.strip(), 'message': 'OK' if ok else 'Git not found'}
            return ok
        except:
            self.results['git'] = {'ok': False, 'message': 'Git not found'}
            return False
    
    def check_msys2(self):
        """Check MSYS2."""
        paths = [r"C:\msys64", r"C:\msys2", r"D:\msys64"]
        found = any(os.path.exists(p) for p in paths)
        self.results['msys2'] = {'ok': found, 'message': 'Found' if found else 'Not installed (optional)'}
        return found
    
    def check_python_packages(self):
        """Check critical Python packages."""
        required = ['fastapi', 'uvicorn', 'websockets', 'pandas', 'numpy', 'playwright', 'selenium']
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        ok = len(missing) == 0
        self.results['python_packages'] = {
            'ok': ok,
            'missing': missing,
            'message': 'All installed' if ok else f"Missing: {', '.join(missing)}"
        }
        return ok
    
    def check_dashboard(self):
        """Check React dashboard."""
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard')
        node_modules = os.path.join(dashboard_path, 'node_modules')
        
        exists = os.path.exists(dashboard_path)
        installed = os.path.exists(node_modules)
        
        self.results['dashboard'] = {
            'ok': exists and installed,
            'exists': exists,
            'installed': installed,
            'message': 'Ready' if (exists and installed) else 'Run npm install in dashboard/'
        }
        return exists and installed
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "="*60)
        print("Veyra - Setup Validation Report")
        print("="*60)
        
        all_ok = True
        for name, result in self.results.items():
            status = "✓" if result['ok'] else "✗"
            color = "\033[92m" if result['ok'] else "\033[91m"
            reset = "\033[0m"
            print(f"{color}{status}\033[0m {name:20} {result['message']}")
            if not result['ok']:
                all_ok = False
        
        print("="*60)
        
        if all_ok:
            print("\033[92m✓ All checks passed! System is ready.\033[0m")
            print("\nNext steps:")
            print("  1. Run: .\\QUICKSTART.bat")
            print("  2. Or: python main.py")
        else:
            print("\033[91m✗ Some checks failed. See above.\033[0m")
            print("\nQuick fixes:")
            print("  1. Run: .\\COMPLETE_SETUP.bat")
            print("  2. Or: .\\\AUTO_SETUP.ps1 -FullSetup")
        
        print("="*60)
        
        # Save report
        report_file = f"setup_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nReport saved: {report_file}")
        
        return all_ok
    
    def run_all(self):
        """Run all validation checks."""
        self.check_python()
        self.check_node()
        self.check_ollama()
        self.check_docker()
        self.check_wsl()
        self.check_git()
        self.check_msys2()
        self.check_python_packages()
        self.check_dashboard()
        return self.generate_report()

if __name__ == "__main__":
    validator = SetupValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)
