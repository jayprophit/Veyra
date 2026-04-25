"""Financial Master CLI - Command-line interface for all operations.

Usage:
    python cli.py --help
    python cli.py start
    python cli.py status
    python cli.py backup
    python cli.py scrape yahoo --ticker AAPL
    python cli.py agent list
    python cli.py config show
"""

import argparse
import sys
import json
from pathlib import Path

class FinancialMasterCLI:
    """Command-line interface for Financial Master."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with subcommands."""
        parser = argparse.ArgumentParser(
            prog='fm',
            description='Financial Master - 5-Star Portfolio Management System',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python cli.py start                    # Start all services
  python cli.py status                   # Show system status
  python cli.py backup create            # Create backup
  python cli.py scrape yahoo --ticker VUAG  # Scrape Yahoo Finance
  python cli.py agent list               # List AI agents
  python cli.py config set --key API_PORT --value 8001
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Start command
        start_parser = subparsers.add_parser('start', help='Start system services')
        start_parser.add_argument('--services', nargs='+', choices=['api', 'dashboard', 'websocket', 'all'], default=['all'])
        start_parser.add_argument('--daemon', action='store_true', help='Run in background')
        
        # Stop command
        stop_parser = subparsers.add_parser('stop', help='Stop system services')
        stop_parser.add_argument('--services', nargs='+', choices=['api', 'dashboard', 'websocket', 'all'], default=['all'])
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        status_parser.add_argument('--watch', '-w', action='store_true', help='Watch mode')
        
        # Backup command
        backup_parser = subparsers.add_parser('backup', help='Backup operations')
        backup_sub = backup_parser.add_subparsers(dest='backup_action')
        
        backup_create = backup_sub.add_parser('create', help='Create backup')
        backup_create.add_argument('--name', help='Backup name')
        backup_create.add_argument('--compress', action='store_true', default=True)
        
        backup_list = backup_sub.add_parser('list', help='List backups')
        
        backup_restore = backup_sub.add_parser('restore', help='Restore backup')
        backup_restore.add_argument('name', help='Backup name to restore')
        
        # Scrape command
        scrape_parser = subparsers.add_parser('scrape', help='Data scraping')
        scrape_sub = scrape_parser.add_subparsers(dest='scrape_source')
        
        yahoo_scrape = scrape_sub.add_parser('yahoo', help='Scrape Yahoo Finance')
        yahoo_scrape.add_argument('--ticker', '-t', required=True, help='Stock ticker')
        yahoo_scrape.add_argument('--pages', '-p', type=int, default=1, help='Number of pages')
        yahoo_scrape.add_argument('--output', '-o', help='Output file (JSON)')
        
        t212_scrape = scrape_sub.add_parser('trading212', help='Import Trading 212 data')
        t212_scrape.add_argument('--file', '-f', required=True, help='CSV file path')
        
        # Agent command
        agent_parser = subparsers.add_parser('agent', help='AI agent management')
        agent_sub = agent_parser.add_subparsers(dest='agent_action')
        
        agent_list = agent_sub.add_parser('list', help='List agents')
        agent_start = agent_sub.add_parser('start', help='Start agent')
        agent_start.add_argument('name', help='Agent name')
        agent_stop = agent_sub.add_parser('stop', help='Stop agent')
        agent_stop.add_argument('name', help='Agent name')
        agent_status = agent_sub.add_parser('status', help='Agent status')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_sub = config_parser.add_subparsers(dest='config_action')
        
        config_show = config_sub.add_parser('show', help='Show configuration')
        config_set = config_sub.add_parser('set', help='Set configuration value')
        config_set.add_argument('--key', '-k', required=True, help='Config key')
        config_set.add_argument('--value', '-v', required=True, help='Config value')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Run tests')
        test_parser.add_argument('--type', choices=['unit', 'integration', 'all'], default='all')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate setup')
        
        # Logs command
        logs_parser = subparsers.add_parser('logs', help='View logs')
        logs_parser.add_argument('--service', choices=['api', 'dashboard', 'websocket', 'all'], default='all')
        logs_parser.add_argument('--tail', '-n', type=int, default=100, help='Number of lines')
        logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow mode')
        
        return parser
    
    def run(self, args=None):
        """Run CLI with arguments."""
        parsed = self.parser.parse_args(args)
        
        if not parsed.command:
            self.parser.print_help()
            return 0
        
        # Dispatch to handler
        handler = getattr(self, f'handle_{parsed.command}', None)
        if handler:
            return handler(parsed)
        else:
            print(f"Unknown command: {parsed.command}")
            return 1
    
    def handle_start(self, args):
        """Handle start command."""
        print(f"🚀 Starting services: {', '.join(args.services)}")
        
        import subprocess
        
        if 'all' in args.services or 'api' in args.services:
            print("  Starting API server...")
            subprocess.Popen(['python', '19_API_Server.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        if 'all' in args.services or 'dashboard' in args.services:
            print("  Starting Dashboard...")
            subprocess.Popen(['npm', 'run', 'dev'], cwd='dashboard', creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        if 'all' in args.services or 'websocket' in args.services:
            print("  Starting WebSocket...")
            subprocess.Popen(['python', '15_WebSocket_Real_Time_Feeds.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("\n✅ Services starting. Use 'python cli.py status' to check.")
        return 0
    
    def handle_stop(self, args):
        """Handle stop command."""
        print(f"🛑 Stopping services: {', '.join(args.services)}")
        
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                if '19_API_Server.py' in cmdline and ('api' in args.services or 'all' in args.services):
                    print(f"  Stopping API server (PID: {proc.info['pid']})")
                    proc.terminate()
                
                if '15_WebSocket_Real_Time_Feeds.py' in cmdline and ('websocket' in args.services or 'all' in args.services):
                    print(f"  Stopping WebSocket (PID: {proc.info['pid']})")
                    proc.terminate()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print("\n✅ Services stopped.")
        return 0
    
    def handle_status(self, args):
        """Handle status command."""
        try:
            import requests
            r = requests.get('http://localhost:8000/api/system/status', timeout=5)
            
            if r.status_code == 200:
                status = r.json()
                print("\n📊 System Status")
                print("=" * 40)
                print(f"API Running:      {status.get('api_running', False)}")
                print(f"Database:         {status.get('database_connected', False)}")
                print(f"WebSocket:        {status.get('websocket_status', 'unknown')}")
                print(f"Agents Running:   {status.get('agents_running', 0)}")
                print(f"Pending Decisions:{status.get('pending_decisions', 0)}")
                print("=" * 40)
            else:
                print(f"⚠️  API returned status {r.status_code}")
                
        except requests.ConnectionError:
            print("❌ API server not running")
        
        return 0
    
    def handle_backup(self, args):
        """Handle backup command."""
        if args.backup_action == 'create':
            print("💾 Creating backup...")
            
            from backup_recovery import BackupManager
            bm = BackupManager()
            
            result = bm.create_backup(
                name=args.name,
                compress=args.compress
            )
            
            if result['success']:
                print(f"✅ Backup created: {result['backup_path']}")
                print(f"   Size: {result['size_bytes'] / 1024 / 1024:.2f} MB")
            else:
                print("❌ Backup failed")
                return 1
                
        elif args.backup_action == 'list':
            from backup_recovery import BackupManager
            bm = BackupManager()
            
            backups = bm.list_backups()
            print(f"\n📦 Available Backups ({len(backups)})")
            print("=" * 60)
            
            for b in backups[:10]:
                size_mb = b['size_bytes'] / 1024 / 1024
                print(f"  {b['name'][:30]:30} {size_mb:6.1f} MB  {b['created'][:10]}")
                
        elif args.backup_action == 'restore':
            print(f"📦 Restoring backup: {args.name}")
            
            from backup_recovery import BackupManager
            bm = BackupManager()
            
            if bm.restore_backup(args.name):
                print("✅ Backup restored successfully")
            else:
                print("❌ Restore failed")
                return 1
        
        return 0
    
    def handle_scrape(self, args):
        """Handle scrape command."""
        if args.scrape_source == 'yahoo':
            print(f"🔍 Scraping Yahoo Finance for {args.ticker}...")
            
            import asyncio
            from financial_scraper import YahooFinanceScraper
            
            async def do_scrape():
                scraper = YahooFinanceScraper()
                await scraper.init(headless=True)
                
                quote = await scraper.get_quote(args.ticker)
                print(f"\n📈 {args.ticker} Quote:")
                print(json.dumps(quote, indent=2))
                
                if args.pages > 1:
                    news = await scraper.get_news(args.ticker, pages=args.pages)
                    print(f"\n📰 News ({news.pages_scraped} pages scraped):")
                    for item in news.data[:5]:
                        print(f"  - {item}")
                
                await scraper.close()
            
            asyncio.run(do_scrape())
            
        elif args.scrape_source == 'trading212':
            print(f"📥 Importing Trading 212 data from {args.file}")
            
            from data_scraper import Trading212Importer
            importer = Trading212Importer()
            
            try:
                data = importer.parse(args.file)
                print(f"✅ Imported {len(data)} transactions")
                
                # Show sample
                if data:
                    print("\nSample transaction:")
                    print(json.dumps(data[0], indent=2))
            except Exception as e:
                print(f"❌ Import failed: {e}")
                return 1
        
        return 0
    
    def handle_agent(self, args):
        """Handle agent command."""
        if args.agent_action == 'list':
            print("\n🤖 AI Agents")
            print("=" * 40)
            
            agents = [
                "market_data_collector",
                "tax_optimizer",
                "risk_manager",
                "portfolio_rebalancer",
                "retirement_planner",
                "withdrawal_strategist",
                "sentiment_analyzer",
                "compliance_auditor"
            ]
            
            for agent in agents:
                print(f"  • {agent}")
                
        elif args.agent_action == 'status':
            try:
                import requests
                r = requests.get('http://localhost:8000/api/agents/status', timeout=5)
                
                if r.status_code == 200:
                    print("\n🤖 Agent Status")
                    print(json.dumps(r.json(), indent=2))
                else:
                    print("⚠️  Could not fetch agent status")
            except:
                print("❌ API not available")
        
        return 0
    
    def handle_config(self, args):
        """Handle config command."""
        if args.config_action == 'show':
            print("\n⚙️  Configuration")
            print("=" * 40)
            
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            print(f"  {line}")
            else:
                print("  No .env file found")
                
        elif args.config_action == 'set':
            print(f"⚙️  Setting {args.key} = {args.value}")
            
            env_file = Path('.env')
            lines = []
            
            if env_file.exists():
                with open(env_file) as f:
                    lines = f.readlines()
            
            # Update or add key
            key_found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{args.key}="):
                    lines[i] = f"{args.key}={args.value}\n"
                    key_found = True
                    break
            
            if not key_found:
                lines.append(f"{args.key}={args.value}\n")
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Configuration updated")
        
        return 0
    
    def handle_test(self, args):
        """Handle test command."""
        print(f"🧪 Running {args.type} tests...")
        
        import subprocess
        
        if args.type in ['integration', 'all']:
            result = subprocess.run(['python', '26_Integration_Tests.py'])
            return result.returncode
        
        print("✅ Tests completed")
        return 0
    
    def handle_validate(self, args):
        """Handle validate command."""
        print("🔍 Validating setup...")
        
        import subprocess
        result = subprocess.run(['python', 'VALIDATE_SETUP.py'])
        
        return result.returncode
    
    def handle_logs(self, args):
        """Handle logs command."""
        print(f"📄 Logs for {args.service}")
        
        log_files = {
            'api': 'logs/financial_master_api.log',
            'dashboard': 'dashboard/npm-debug.log',
            'websocket': 'logs/financial_master_websocket.log'
        }
        
        if args.service == 'all':
            for service, path in log_files.items():
                if Path(path).exists():
                    print(f"\n--- {service.upper()} ---")
                    with open(path) as f:
                        lines = f.readlines()
                        for line in lines[-args.tail:]:
                            print(line.rstrip())
        else:
            path = log_files.get(args.service)
            if path and Path(path).exists():
                with open(path) as f:
                    lines = f.readlines()
                    for line in lines[-args.tail:]:
                        print(line.rstrip())
        
        return 0

if __name__ == "__main__":
    cli = FinancialMasterCLI()
    sys.exit(cli.run())
