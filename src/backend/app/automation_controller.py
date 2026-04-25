"""Financial Master - Master Automation Controller
Windows 11 + WSL + Docker + K8s + Ollama automation layer."""

import os, sys, json, time, subprocess, psutil, requests
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AutomationController')

class OllamaManager:
    """Manage Ollama models: download, verify, monitor."""
    
    MODELS = {
        "llama3.2:3b": {"size": "2.0GB", "ram": "8GB", "purpose": "Fast summaries"},
        "llama3.1:8b": {"size": "4.7GB", "ram": "16GB", "purpose": "Analysis"},
        "qwen2.5:7b": {"size": "4.4GB", "ram": "16GB", "purpose": "JSON/structured"},
        "phi4": {"size": "9.1GB", "ram": "24GB", "purpose": "Math/reasoning"},
        "nomic-embed-text": {"size": "274MB", "ram": "4GB", "purpose": "Embeddings"}
    }
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available: List[str] = []
        self._check()
    
    def _check(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if r.status_code == 200:
                self.available = [m["name"] for m in r.json().get("models", [])]
                return True
        except: pass
        return False
    
    def download(self, model: str, timeout: int = 600) -> bool:
        if model in self.available:
            return True
        logger.info(f"⬇️ Downloading {model}...")
        try:
            proc = subprocess.Popen(["ollama", "pull", model], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(timeout=timeout)
            if proc.returncode == 0:
                self.available.append(model)
                logger.info(f"✓ {model} ready")
                return True
        except Exception as e:
            logger.error(f"✗ Failed: {e}")
        return False
    
    def download_all(self) -> Dict[str, bool]:
        return {m: self.download(m) for m in self.MODELS.keys()}
    
    def start_server(self) -> bool:
        if self._check(): return True
        try:
            subprocess.Popen(["powershell", "-Command", "Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden"], shell=True)
            time.sleep(5)
            return self._check()
        except: return False

class DesktopAutomation:
    """Windows 11 desktop automation."""
    
    def __init__(self):
        self.pyautogui = None
        try:
            import pyautogui
            self.pyautogui = pyautogui
            pyautogui.FAILSAFE = True
        except: logger.warning("pip install pyautogui")
    
    def screenshot(self, filename: Optional[str] = None) -> str:
        if not self.pyautogui: return ""
        if not filename:
            filename = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
        self.pyautogui.screenshot().save(filename)
        return filename
    
    def open_app(self, app: str) -> bool:
        try:
            subprocess.Popen(["powershell", "-Command", f"Start-Process {app}"], shell=True)
            return True
        except: return False
    
    def open_browser(self, url: str) -> bool:
        import webbrowser
        webbrowser.open(url)
        return True

class BrowserAutomation:
    """Browser automation with Selenium/Playwright."""
    
    def __init__(self):
        self.driver = None
    
    def init_selenium(self, headless: bool = True) -> bool:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            opts = Options()
            if headless: opts.add_argument("--headless")
            self.driver = webdriver.Chrome(options=opts)
            return True
        except: return False
    
    def scrape_yahoo(self, ticker: str) -> Dict:
        if not self.driver and not self.init_selenium(): return {}
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            self.driver.get(f"https://finance.yahoo.com/quote/{ticker}")
            price = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-symbol='{ticker}'][data-field='regularMarketPrice']"))
            ).text
            return {"ticker": ticker, "price": price, "timestamp": datetime.now().isoformat()}
        except: return {}

class ContainerOrchestrator:
    """Docker and Kubernetes automation."""
    
    def __init__(self):
        self.docker = None
        try:
            import docker
            self.docker = docker.from_env()
        except: pass
    
    def docker_start(self, compose_file: str = "docker-compose.yml") -> bool:
        try:
            subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], check=True)
            return True
        except: return False
    
    def k8s_deploy(self, namespace: str = "financial-master") -> bool:
        try:
            from kubernetes import client, config
            config.load_kube_config()
            v1 = client.CoreV1Api()
            try: v1.read_namespace(name=namespace)
            except: v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))
            return True
        except: return False

class PowerShellAutomation:
    """PowerShell automation for Windows tasks."""
    
    def run(self, cmd: str, admin: bool = False) -> Tuple[bool, str]:
        try:
            ps = f"powershell -Command \"{cmd}\""
            r = subprocess.run(ps, capture_output=True, text=True, shell=True)
            return r.returncode == 0, r.stdout + r.stderr
        except: return False, ""
    
    def winget_install(self, pkg: str) -> bool:
        s, _ = self.run(f"winget install --id {pkg} --silent --accept-package-agreements")
        return s
    
    def set_env(self, name: str, value: str) -> bool:
        s, _ = self.run(f"[System.Environment]::SetEnvironmentVariable('{name}', '{value}', 'User')")
        return s

class WSLManager:
    """WSL integration."""
    
    def run(self, cmd: str, distro: str = "Ubuntu") -> Tuple[bool, str]:
        try:
            r = subprocess.run(["wsl", "-d", distro, "-e", "bash", "-c", cmd], capture_output=True, text=True)
            return r.returncode == 0, r.stdout + r.stderr
        except: return False, "WSL not available"
    
    def install_packages(self, pkgs: List[str]) -> bool:
        s, _ = self.run(f"sudo apt-get update && sudo apt-get install -y {' '.join(pkgs)}")
        return s

class SystemMonitor:
    """Monitor system health."""
    
    def stats(self) -> Dict:
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    
    def is_healthy(self) -> bool:
        m = psutil.virtual_memory()
        return m.available > 2 * 1024 * 1024 * 1024  # 2GB free

class MasterAutomationController:
    """Central controller for all automation."""
    
    def __init__(self):
        self.ollama = OllamaManager()
        self.desktop = DesktopAutomation()
        self.browser = BrowserAutomation()
        self.docker = ContainerOrchestrator()
        self.powershell = PowerShellAutomation()
        self.wsl = WSLManager()
        self.monitor = SystemMonitor()
    
    def setup_ollama(self) -> bool:
        """Download all financial models."""
        if not self.ollama._check():
            self.ollama.start_server()
        results = self.ollama.download_all()
        return all(results.values())
    
    def setup_docker(self) -> bool:
        """Start Docker Compose stack."""
        return self.docker.docker_start()
    
    def setup_wsl_tools(self) -> bool:
        """Install tools in WSL."""
        return self.wsl.install_packages(["curl", "git", "python3", "python3-pip"])
    
    def open_dashboard(self) -> bool:
        """Open browser to dashboard."""
        return self.desktop.open_browser("http://localhost:5173")
    
    def system_report(self) -> Dict:
        """Generate system status report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.monitor.stats(),
            "ollama_models": self.ollama.available,
            "healthy": self.monitor.is_healthy()
        }
    
    def auto_setup(self) -> Dict[str, bool]:
        """Run complete automated setup."""
        logger.info("🚀 Starting automated setup...")
        results = {
            "ollama": self.setup_ollama(),
            "docker": self.setup_docker(),
            "wsl_tools": self.setup_wsl_tools(),
            "dashboard": self.open_dashboard()
        }
        logger.info(f"✅ Setup complete: {results}")
        return results

if __name__ == "__main__":
    controller = MasterAutomationController()
    print("="*60)
    print("Financial Master - Automation Controller")
    print("="*60)
    print("\nAvailable commands:")
    print("  controller.setup_ollama()      - Download all LLM models")
    print("  controller.setup_docker()       - Start Docker stack")
    print("  controller.auto_setup()         - Run everything")
    print("  controller.system_report()      - Get system status")
    print("\nExample: python -c \"from automation_controller import MasterAutomationController; c = MasterAutomationController(); c.auto_setup()\"")
