"""WSL2 and Ubuntu Integration - Native Linux tools in Windows."""

import subprocess
import os
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger('WSL2Ubuntu')

class WSL2Manager:
    """Manage WSL2 distributions and tools."""
    
    def __init__(self, distro: str = "Ubuntu"):
        self.distro = distro
        self.available = self._check_wsl()
    
    def _check_wsl(self) -> bool:
        """Check if WSL2 is available."""
        try:
            result = subprocess.run(
                ["wsl", "-l", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
            return "Ubuntu" in result.stdout or any(d in result.stdout for d in ['Ubuntu', 'Debian', 'Fedora'])
        except:
            return False
    
    def list_distros(self) -> List[Dict[str, str]]:
        """List all WSL distributions."""
        try:
            result = subprocess.run(
                ["wsl", "-l", "-v"],
                capture_output=True,
                text=True
            )
            
            distros = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    distros.append({
                        "name": parts[0],
                        "state": parts[1],
                        "version": parts[2]
                    })
            
            return distros
        except:
            return []
    
    def run_command(self, command: str, user: str = None) -> Tuple[bool, str, str]:
        """Run command in WSL."""
        if not self.available:
            return False, "", "WSL not available"
        
        cmd = ["wsl", "-d", self.distro]
        if user:
            cmd.extend(["-u", user])
        cmd.extend(["-e", "bash", "-c", command])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def install_packages(self, packages: List[str]) -> bool:
        """Install packages in WSL Ubuntu."""
        logger.info(f"Installing packages: {packages}")
        
        # Update first
        success, _, _ = self.run_command("sudo apt-get update")
        if not success:
            return False
        
        # Install packages
        pkg_str = " ".join(packages)
        success, out, err = self.run_command(f"sudo apt-get install -y {pkg_str}")
        
        if success:
            logger.info(f"✓ Packages installed: {packages}")
        else:
            logger.error(f"✗ Failed to install: {err}")
        
        return success
    
    def setup_development_environment(self) -> bool:
        """Setup complete dev environment in WSL."""
        packages = [
            "build-essential",
            "git",
            "curl",
            "wget",
            "python3",
            "python3-pip",
            "python3-venv",
            "nodejs",
            "npm",
            "docker.io",
            "docker-compose",
            "sqlite3",
            "postgresql-client",
            "redis-tools",
            "htop",
            "vim",
            "nano",
            "jq"
        ]
        
        return self.install_packages(packages)
    
    def setup_docker_in_wsl(self) -> bool:
        """Setup Docker inside WSL2 (not Docker Desktop)."""
        commands = [
            "curl -fsSL https://get.docker.com -o get-docker.sh",
            "sudo sh get-docker.sh",
            "sudo usermod -aG docker $USER",
            "sudo service docker start || sudo systemctl start docker"
        ]
        
        for cmd in commands:
            success, out, err = self.run_command(cmd)
            if not success and "already" not in err.lower():
                logger.warning(f"Command failed (may be already installed): {err}")
        
        logger.info("✓ Docker setup in WSL2")
        return True
    
    def copy_to_windows(self, wsl_path: str, windows_path: str) -> bool:
        """Copy file from WSL to Windows."""
        # Convert Windows path to WSL mount path
        drive = windows_path[0].lower()
        normalized_windows_path = windows_path[3:].replace('\\', '/')
        wsl_windows_path = f"/mnt/{drive}/{normalized_windows_path}"
        
        success, _, err = self.run_command(f"cp '{wsl_path}' '{wsl_windows_path}'")
        
        if success:
            logger.info(f"✓ Copied {wsl_path} to {windows_path}")
        else:
            logger.error(f"✗ Copy failed: {err}")
        
        return success
    
    def copy_to_wsl(self, windows_path: str, wsl_path: str) -> bool:
        """Copy file from Windows to WSL."""
        # Use wsl command with wslpath
        success, _, _ = self.run_command(f"cp '{windows_path}' '{wsl_path}'")
        
        if not success:
            # Alternative: use PowerShell
            try:
                ps_cmd = f'wsl -d {self.distro} -e bash -c "cp \'{windows_path}\' \'{wsl_path}\'"'
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
                success = True
            except:
                pass
        
        if success:
            logger.info(f"✓ Copied {windows_path} to {wsl_path}")
        else:
            logger.error(f"✗ Copy failed")
        
        return success
    
    def run_python_script(self, script_path: str, args: List[str] = None) -> Tuple[bool, str]:
        """Run Python script in WSL."""
        cmd = f"python3 {script_path}"
        if args:
            cmd += " " + " ".join(args)
        
        success, out, err = self.run_command(cmd)
        return success, out + err
    
    def start_service(self, service: str) -> bool:
        """Start a service in WSL."""
        success, _, _ = self.run_command(f"sudo service {service} start")
        return success
    
    def stop_service(self, service: str) -> bool:
        """Stop a service in WSL."""
        success, _, _ = self.run_command(f"sudo service {service} stop")
        return success
    
    def get_ip_address(self) -> str:
        """Get WSL2 IP address."""
        success, out, _ = self.run_command("hostname -I")
        if success:
            return out.strip().split()[0]
        return ""
    
    def create_systemd_service(self, name: str, command: str, description: str = "") -> bool:
        """Create systemd service in WSL."""
        service_content = f"""[Unit]
Description={description or name}
After=network.target

[Service]
Type=simple
User=%I
ExecStart={command}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = f"/etc/systemd/system/{name}.service"
        
        # Write service file
        success, _, _ = self.run_command(
            f"echo '{service_content}' | sudo tee {service_file}"
        )
        
        if success:
            self.run_command(f"sudo systemctl enable {name}")
            self.run_command(f"sudo systemctl start {name}")
            logger.info(f"✓ Created systemd service: {name}")
        
        return success
    
    def setup_port_forwarding(self, windows_port: int, wsl_port: int) -> bool:
        """Setup port forwarding from Windows to WSL."""
        try:
            # Add port proxy
            ps_cmd = (
                f"netsh interface portproxy add v4tov4 "
                f"listenport={windows_port} listenaddress=0.0.0.0 "
                f"connectport={wsl_port} connectaddress=172.17.0.1"
            )
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            
            # Open firewall
            fw_cmd = f"netsh advfirewall firewall add rule name=WSL2_Port_{windows_port} dir=in action=allow protocol=TCP localport={windows_port}"
            subprocess.run(["powershell", "-Command", fw_cmd], check=True)
            
            logger.info(f"✓ Port {windows_port} forwarded to WSL:{wsl_port}")
            return True
        except Exception as e:
            logger.error(f"Port forwarding failed: {e}")
            return False

class UbuntuAutomation:
    """Ubuntu-specific automation."""
    
    def __init__(self, wsl_manager: WSL2Manager):
        self.wsl = wsl_manager
    
    def install_snaps(self, snaps: List[str]) -> bool:
        """Install snap packages."""
        for snap in snaps:
            success, _, _ = self.wsl.run_command(f"sudo snap install {snap}")
            if success:
                logger.info(f"✓ Installed snap: {snap}")
        return True
    
    def add_ppa(self, ppa: str) -> bool:
        """Add PPA repository."""
        success, _, _ = self.wsl.run_command(f"sudo add-apt-repository -y ppa:{ppa}")
        if success:
            self.wsl.run_command("sudo apt-get update")
        return success
    
    def setup_nodejs(self, version: int = 20) -> bool:
        """Setup Node.js via NodeSource."""
        commands = [
            f"curl -fsSL https://deb.nodesource.com/setup_{version}.x | sudo -E bash -",
            "sudo apt-get install -y nodejs"
        ]
        
        for cmd in commands:
            success, _, _ = self.wsl.run_command(cmd)
            if not success:
                return False
        
        logger.info(f"✓ Node.js {version} installed")
        return True
    
    def setup_postgres(self) -> bool:
        """Setup PostgreSQL database."""
        self.wsl.install_packages(["postgresql", "postgresql-contrib"])
        
        # Start service
        self.wsl.start_service("postgresql")
        
        # Create database
        self.wsl.run_command(
            "sudo -u postgres psql -c \"CREATE DATABASE veyra;\""
        )
        
        logger.info("✓ PostgreSQL setup complete")
        return True
    
    def setup_redis(self) -> bool:
        """Setup Redis cache."""
        self.wsl.install_packages(["redis-server"])
        self.wsl.start_service("redis")
        logger.info("✓ Redis setup complete")
        return True
    
    def create_swap_file(self, size_gb: int = 4) -> bool:
        """Create swap file for memory-intensive operations."""
        commands = [
            f"sudo fallocate -l {size_gb}G /swapfile",
            "sudo chmod 600 /swapfile",
            "sudo mkswap /swapfile",
            "sudo swapon /swapfile"
        ]
        
        for cmd in commands:
            success, _, _ = self.wsl.run_command(cmd)
            if not success:
                return False
        
        # Make permanent
        self.wsl.run_command("echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab")
        
        logger.info(f"✓ Created {size_gb}GB swap file")
        return True
    
    def optimize_for_ollama(self) -> bool:
        """Optimize WSL2 for running Ollama models."""
        # Create swap for large models
        self.create_swap_file(8)
        
        # Increase file descriptors
        self.wsl.run_command("echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf")
        self.wsl.run_command("echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf")
        
        # Optimize network
        self.wsl.run_command("echo 'net.core.rmem_max=134217728' | sudo tee -a /etc/sysctl.conf")
        self.wsl.run_command("echo 'net.core.wmem_max=134217728' | sudo tee -a /etc/sysctl.conf")
        
        logger.info("✓ WSL2 optimized for Ollama")
        return True
    
    def clone_repo(self, url: str, dest: str = None) -> bool:
        """Clone git repository."""
        if not dest:
            dest = url.split('/')[-1].replace('.git', '')
        
        success, _, _ = self.wsl.run_command(f"git clone {url} {dest}")
        
        if success:
            logger.info(f"✓ Cloned {url} to {dest}")
        return success
    
    def setup_project(self, project_path: str) -> bool:
        """Setup Veyra project in WSL."""
        # Create Python venv
        self.wsl.run_command(f"cd {project_path} && python3 -m venv .venv")
        
        # Install requirements
        self.wsl.run_command(
            f"cd {project_path} && source .venv/bin/activate && pip install -r requirements.txt"
        )
        
        # Setup dashboard
        self.wsl.run_command(
            f"cd {project_path}/dashboard && npm install"
        )
        
        logger.info("✓ Project setup in WSL")
        return True

if __name__ == "__main__":
    print("WSL2/Ubuntu Integration ready")
    print("Usage:")
    print("  wsl = WSL2Manager('Ubuntu')")
    print("  wsl.setup_development_environment()")
    print("  wsl.setup_docker_in_wsl()")
    print("  wsl.run_command('python3 --version')")
    print()
    print("  ubuntu = UbuntuAutomation(wsl)")
    print("  ubuntu.setup_nodejs(20)")
    print("  ubuntu.setup_postgres()")
    print("  ubuntu.optimize_for_ollama()")
