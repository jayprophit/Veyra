"""Windows System Tray Application - Quick access to Financial Master."""

import sys
import threading
import webbrowser

class SystemTrayApp:
    """Windows system tray icon with quick actions."""
    
    def __init__(self):
        self.icon = None
        self.menu = None
    
    def create_icon(self):
        """Create simple icon (requires PIL)."""
        try:
            from PIL import Image, ImageDraw
            # Create green square icon
            img = Image.new('RGB', (64, 64), color='green')
            draw = ImageDraw.Draw(img)
            draw.text((20, 25), "FM", fill='white')
            return img
        except:
            return None
    
    def on_open_dashboard(self, icon=None, item=None):
        """Open dashboard in browser."""
        webbrowser.open("http://localhost:5173")
    
    def on_open_api(self, icon=None, item=None):
        """Open API docs."""
        webbrowser.open("http://localhost:8000/docs")
    
    def on_run_setup(self, icon=None, item=None):
        """Run automated setup."""
        import subprocess
        subprocess.Popen(["powershell", "-Command", ".\AUTO_SETUP.ps1"], shell=True)
    
    def on_ollama_status(self, icon=None, item=None):
        """Check Ollama status."""
        import requests
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m['name'] for m in r.json().get('models', [])]
                self.show_notification(f"Ollama Ready: {len(models)} models")
            else:
                self.show_notification("Ollama: Not responding")
        except:
            self.show_notification("Ollama: Not running")
    
    def on_exit(self, icon=None, item=None):
        """Exit application."""
        if self.icon:
            self.icon.stop()
        sys.exit()
    
    def show_notification(self, message: str, title: str = "Financial Master"):
        """Show system notification."""
        if self.icon:
            self.icon.notify(message, title)
    
    def run(self):
        """Start system tray app."""
        try:
            import pystray
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Open Dashboard", self.on_open_dashboard),
                pystray.MenuItem("API Documentation", self.on_open_api),
                pystray.MenuItem("---", None),
                pystray.MenuItem("Run Setup", self.on_run_setup),
                pystray.MenuItem("Check Ollama", self.on_ollama_status),
                pystray.MenuItem("---", None),
                pystray.MenuItem("Exit", self.on_exit)
            )
            
            # Create icon
            self.icon = pystray.Icon("Financial Master", self.create_icon(), "Financial Master", menu)
            print("✓ System tray app running. Right-click icon for menu.")
            self.icon.run()
            
        except ImportError:
            print("pip install pystray PIL")
            print("Running in console mode...")
            self.console_mode()
    
    def console_mode(self):
        """Fallback console menu."""
        while True:
            print("\n=== Financial Master ===")
            print("1. Open Dashboard")
            print("2. Open API Docs")
            print("3. Run Setup")
            print("4. Check Ollama")
            print("5. Exit")
            
            choice = input("Select: ")
            
            if choice == "1":
                self.on_open_dashboard()
            elif choice == "2":
                self.on_open_api()
            elif choice == "3":
                self.on_run_setup()
            elif choice == "4":
                self.on_ollama_status()
            elif choice == "5":
                self.on_exit()
                break

if __name__ == "__main__":
    print("Starting Financial Master System Tray...")
    print("Requirements: pip install pystray pillow requests")
    app = SystemTrayApp()
    app.run()
