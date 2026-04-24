"""MSYS2 Integration - MinGW/MinGW64 tools in Windows."""

import subprocess
import os
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger('MSYS2')

class MSYS2Manager:
    """Manage MSYS2 MinGW environment."""
    
    MSYS2_PATHS = [
        r"C:\msys64\usr\bin",
        r"C:\msys64\mingw64\bin",
        r"C:\msys64\mingw32\bin"
    ]
    
    def __init__(self):
        self.msys_path = self._find_msys2()
        self.available = self.msys_path is not None
    
    def _find_msys2(self) -> Optional[str]:
        """Find MSYS2 installation."""
        for path in [r"C:\msys64", r"C:\msys2", r"D:\msys64"]:
            if os.path.exists(os.path.join(path, "msys2.exe")):
                return path
        return None
    
    def _run_msys(self, command: str, shell: str = "bash") -> Tuple[bool, str, str]:
        """Run command in MSYS2 environment."""
        if not self.available:
            return False, "", "MSYS2 not found"
        
        msys_shell = os.path.join(self.msys_path, "usr", "bin", shell)
        
        try:
            result = subprocess.run(
                [msys_shell, "-c", command],
                capture_output=True,
                text=True,
                timeout=300,
                env=self._get_env()
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def _get_env(self) -> dict:
        """Get environment with MSYS2 paths."""
        env = os.environ.copy()
        env["PATH"] = ";".join(self.MSYS2_PATHS + [env.get("PATH", "")])
        return env
    
    def install_package(self, package: str) -> bool:
        """Install package via pacman."""
        logger.info(f"Installing MSYS2 package: {package}")
        
        success, out, err = self._run_msys(f"pacman -S --noconfirm {package}")
        
        if success:
            logger.info(f"✓ Installed: {package}")
        else:
            logger.error(f"✗ Failed to install {package}: {err}")
        
        return success
    
    def install_packages(self, packages: List[str]) -> bool:
        """Install multiple packages."""
        pkg_str = " ".join(packages)
        return self._run_msys(f"pacman -S --noconfirm {pkg_str}")[0]
    
    def setup_development_tools(self) -> bool:
        """Install essential development tools."""
        mingw_packages = [
            "mingw-w64-x86_64-toolchain",
            "mingw-w64-x86_64-cmake",
            "mingw-w64-x86_64-ninja",
            "mingw-w64-x86_64-python",
            "mingw-w64-x86_64-python-pip",
            "mingw-w64-x86_64-nodejs",
            "mingw-w64-x86_64-git",
            "mingw-w64-x86_64-sqlite3",
            "mingw-w64-x86_64-postgresql",
            "mingw-w64-x86_64-redis",
            "mingw-w64-x86_64-rust",
            "mingw-w64-x86_64-go"
        ]
        
        msys_packages = [
            "make",
            "gcc",
            "vim",
            "nano",
            "curl",
            "wget",
            "jq",
            "tree",
            "htop",
            "zip",
            "unzip",
            "tar",
            "gzip"
        ]
        
        logger.info("Installing MinGW64 packages...")
        self.install_packages(mingw_packages)
        
        logger.info("Installing MSYS2 base packages...")
        self.install_packages(msys_packages)
        
        logger.info("✓ MSYS2 development environment ready")
        return True
    
    def update_system(self) -> bool:
        """Update MSYS2 and all packages."""
        logger.info("Updating MSYS2...")
        
        # Update package database
        success, _, _ = self._run_msys("pacman -Sy")
        if not success:
            return False
        
        # Update core system packages
        success, _, _ = self._run_msys("pacman -S --noconfirm msys2-runtime")
        
        # Update all packages
        success, out, err = self._run_msys("pacman -Su --noconfirm")
        
        if success:
            logger.info("✓ MSYS2 updated")
        return success
    
    def run_mingw_command(self, command: str) -> Tuple[bool, str, str]:
        """Run command in MinGW64 environment."""
        # Use mingw64 bash specifically
        mingw_bash = os.path.join(self.msys_path, "mingw64.exe")
        
        try:
            result = subprocess.run(
                [mingw_bash, "-c", command],
                capture_output=True,
                text=True,
                timeout=300,
                env=self._get_env()
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def compile_c_project(self, source_dir: str) -> bool:
        """Compile C/C++ project with MinGW."""
        commands = [
            f"cd {source_dir}",
            "mkdir -p build",
            "cd build",
            "cmake .. -G 'MinGW Makefiles'",
            "mingw32-make -j$(nproc)"
        ]
        
        cmd = " && ".join(commands)
        success, out, err = self.run_mingw_command(cmd)
        
        if success:
            logger.info(f"✓ Compiled project in {source_dir}")
        else:
            logger.error(f"✗ Compilation failed: {err}")
        
        return success
    
    def install_python_packages(self, packages: List[str]) -> bool:
        """Install Python packages in MSYS2 Python."""
        pkg_str = " ".join(packages)
        success, _, _ = self.run_mingw_command(f"pip install {pkg_str}")
        
        if success:
            logger.info(f"✓ Python packages installed: {packages}")
        return success
    
    def setup_virtualenv(self, name: str = "venv") -> bool:
        """Create Python virtual environment."""
        success, _, _ = self.run_mingw_command(f"python -m venv {name}")
        
        if success:
            logger.info(f"✓ Created virtual environment: {name}")
        return success
    
    def get_gcc_version(self) -> str:
        """Get GCC version."""
        success, out, _ = self.run_mingw_command("gcc --version")
        if success:
            return out.split('\n')[0]
        return "GCC not found"
    
    def list_installed_packages(self) -> List[str]:
        """List installed MSYS2 packages."""
        success, out, _ = self._run_msys("pacman -Qe")
        if success:
            return [line.split()[0] for line in out.strip().split('\n') if line]
        return []
    
    def search_package(self, query: str) -> List[str]:
        """Search for packages."""
        success, out, _ = self._run_msys(f"pacman -Ss {query}")
        if success:
            return [line for line in out.strip().split('\n') if line.startswith('mingw') or line.startswith('msys')]
        return []
    
    def clean_cache(self) -> bool:
        """Clean package cache."""
        success, _, _ = self._run_msys("pacman -Sc --noconfirm")
        if success:
            logger.info("✓ Package cache cleaned")
        return success
    
    def add_to_path(self) -> bool:
        """Add MSYS2 to Windows PATH permanently."""
        try:
            current_path = os.environ.get("PATH", "")
            msys_paths = ";".join(self.MSYS2_PATHS)
            
            if msys_paths in current_path:
                logger.info("MSYS2 already in PATH")
                return True
            
            new_path = f"{msys_paths};{current_path}"
            
            # Use PowerShell to set system environment variable
            ps_cmd = f"[System.Environment]::SetEnvironmentVariable('PATH', '{new_path}', 'User')"
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            
            logger.info("✓ MSYS2 added to PATH (restart terminal)")
            return True
        except Exception as e:
            logger.error(f"Failed to add to PATH: {e}")
            return False
    
    def create_shortcuts(self) -> bool:
        """Create desktop shortcuts for MSYS2 shells."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            
            shells = [
                ("MSYS2 MinGW 64-bit", "mingw64.exe"),
                ("MSYS2 MinGW 32-bit", "mingw32.exe"),
                ("MSYS2 MSYS", "msys2.exe")
            ]
            
            for name, exe in shells:
                shortcut_path = os.path.join(desktop, f"{name}.lnk")
                target = os.path.join(self.msys_path, exe)
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = self.msys_path
                shortcut.IconLocation = target
                shortcut.save()
                
                logger.info(f"✓ Created shortcut: {name}")
            
            return True
        except ImportError:
            logger.warning("winshell not installed, skipping shortcuts")
            return False

class MinGWCompiler:
    """C/C++ compilation with MinGW."""
    
    def __init__(self, msys_manager: MSYS2Manager):
        self.msys = msys_manager
    
    def compile_c(self, source: str, output: str = None, flags: List[str] = None) -> bool:
        """Compile C source file."""
        if not output:
            output = source.replace('.c', '.exe')
        
        cmd_flags = " ".join(flags) if flags else "-O2"
        cmd = f"gcc {cmd_flags} '{source}' -o '{output}'"
        
        success, out, err = self.msys.run_mingw_command(cmd)
        
        if success:
            logger.info(f"✓ Compiled: {source} -> {output}")
        else:
            logger.error(f"✗ Compilation failed: {err}")
        
        return success
    
    def compile_cpp(self, source: str, output: str = None, flags: List[str] = None) -> bool:
        """Compile C++ source file."""
        if not output:
            output = source.replace('.cpp', '.exe').replace('.cc', '.exe')
        
        cmd_flags = " ".join(flags) if flags else "-O2 -std=c++17"
        cmd = f"g++ {cmd_flags} '{source}' -o '{output}'"
        
        success, out, err = self.msys.run_mingw_command(cmd)
        
        if success:
            logger.info(f"✓ Compiled: {source} -> {output}")
        else:
            logger.error(f"✗ Compilation failed: {err}")
        
        return success

if __name__ == "__main__":
    print("MSYS2 Integration ready")
    print("Usage:")
    print("  msys = MSYS2Manager()")
    print("  msys.setup_development_tools()")
    print("  msys.install_package('mingw-w64-x86_64-python')")
    print("  msys.compile_c_project('/path/to/project')")
    print()
    print("  compiler = MinGWCompiler(msys)")
    print("  compiler.compile_c('main.c', 'main.exe')")
