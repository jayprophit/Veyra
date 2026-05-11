"""Build Automation - Automated builds, tests, deployment."""

import subprocess
import os
import sys
from typing import List, Tuple

class BuildAutomator:
    def run(self, cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=True)
            return True, r.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def build_dashboard(self) -> bool:
        print("Building React dashboard...")
        s, out = self.run(["npm", "run", "build"], cwd="dashboard")
        if s: print("✓ Dashboard built")
        else: print(f"✗ Failed: {out}")
        return s
    
    def build_docker(self) -> bool:
        print("Building Docker image...")
        s, out = self.run(["docker", "build", "-t", "veyra:latest", "."])
        return s
    
    def run_tests(self) -> bool:
        print("Running tests...")
        s, out = self.run([sys.executable, "-m", "pytest", "tests/"])
        return s
    
    def full_build(self) -> bool:
        return all([
            self.build_dashboard(),
            self.build_docker(),
            self.run_tests()
        ])

if __name__ == "__main__":
    BuildAutomator().full_build()
