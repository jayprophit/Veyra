"""
Financial Master Agent Command Center
Central Controller for Multi-Agent AI System
Coordinates 8 specialized agents with existing automation engine
Version: 2.0 | Agent-Oriented Architecture
"""

import asyncio
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import time

# Import existing modules
from ai_automation_engine import FinancialEngine
from ml_prediction_model import MLPredictionEngine
from data_ingestion_engine import DataIngestionEngine
from autonomous_master_controller import AutonomousMasterController

# Import new multi-agent architecture
from multi_agent_ai_architecture import (
    MultiAgentOrchestrator, SystemState, AgentDecision, AgentType
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_command_center.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Agent_Command_Center')


class AgentCommandCenter:
    """
    Command Center that orchestrates:
    1. Existing Financial Automation Engine
    2. ML Prediction Engine
    3. Data Ingestion Engine
    4. NEW: Multi-Agent Architecture (8 specialized agents)
    
    Provides unified control, logging, and human interface
    """
    
    def __init__(self, config_path: str = "00_Master_System_Config.json"):
        self.config = self._load_config(config_path)
        
        # Initialize existing engines
        self.financial_engine = FinancialEngine(self.config)
        self.ml_engine = MLPredictionEngine(self.config)
        self.data_engine = DataIngestionEngine(self.config)
        self.master_controller = AutonomousMasterController(self.config)
        
        # Initialize multi-agent orchestrator
        self.agent_orchestrator = MultiAgentOrchestrator(self.config)
        
        # Command center state
        self.is_running = False
        self.cycle_count = 0
        self.start_time = None
        self.decision_history = []
        
        logger.info("Agent Command Center initialized")
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from JSON"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {path}")
            return {}
    
    async def run_unified_cycle(self) -> Dict:
        """
        Run complete unified cycle:
        1. Data ingestion (prices, market data)
        2. ML predictions (price forecasting)
        3. Financial analysis (calculations, rebalancing)
        4. Multi-agent analysis (8 specialized agents)
        5. Decision synthesis and execution
        """
        logger.info(f"Starting unified cycle #{self.cycle_count + 1}")
        cycle_start = datetime.now()
        
        results = {
            'cycle_number': self.cycle_count + 1,
            'timestamp': cycle_start.isoformat(),
            'data_ingestion': {},
            'ml_predictions': {},
            'financial_analysis': {},
            'multi_agent_analysis': {},
            'unified_decisions': [],
            'execution_results': {}
        }
        
        try:
            # Step 1: Data Ingestion
            logger.info("[1/5] Running data ingestion...")
            portfolio_snapshot = self.data_engine.get_portfolio_snapshot()
            results['data_ingestion'] = {
                'status': 'success',
                'assets_tracked': len(portfolio_snapshot),
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 2: ML Predictions
            logger.info("[2/5] Running ML predictions...")
            for symbol in ['BTC', 'ETH', 'VWRL']:
                prediction = self.ml_engine.predict_returns(symbol, days=7)
                results['ml_predictions'][symbol] = prediction
            
            # Step 3: Financial Analysis
            logger.info("[3/5] Running financial analysis...")
            financial_state = self.financial_engine.calculate_financial_state()
            rebalance_recommendation = self.financial_engine.rebalance_portfolio(
                portfolio_snapshot, financial_state
            )
            results['financial_analysis'] = {
                'financial_state': financial_state,
                'rebalance_recommendation': rebalance_recommendation
            }
            
            # Step 4: Multi-Agent Analysis
            logger.info("[4/5] Running multi-agent analysis...")
            system_state = self._create_system_state(
                portfolio_snapshot, financial_state, rebalance_recommendation
            )
            agent_results = await self.agent_orchestrator.run_analysis_cycle(system_state)
            results['multi_agent_analysis'] = agent_results
            
            # Step 5: Decision Synthesis
            logger.info("[5/5] Synthesizing and executing decisions...")
            unified_decisions = self._synthesize_decisions(
                rebalance_recommendation, 
                agent_results.get('decisions', [])
            )
            results['unified_decisions'] = unified_decisions
            
            # Execute approved decisions
            execution_results = await self._execute_unified_decisions(unified_decisions)
            results['execution_results'] = execution_results
            
            # Log to history
            self._log_cycle_results(results)
            
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            results['cycle_duration_seconds'] = cycle_duration
            
            logger.info(f"Cycle #{self.cycle_count + 1} completed in {cycle_duration:.2f}s")
            self.cycle_count += 1
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _create_system_state(
        self, 
        portfolio: Dict, 
        financial_state: Dict,
        rebalance_rec: Dict
    ) -> SystemState:
        """Create system state for multi-agent analysis"""
        
        # Build active positions dict
        active_positions = {}
        for asset_id, data in portfolio.items():
            if data.get('quantity', 0) > 0:
                active_positions[asset_id] = {
                    'quantity': data.get('quantity', 0),
                    'current_price': data.get('current_price', 0),
                    'cost_basis': data.get('avg_price', 0),
                    'platform': data.get('platform', 'unknown'),
                    'type': data.get('type', 'unknown'),
                    'value_gbp': data.get('current_value_usd', 0) * 0.79  # USD to GBP
                }
        
        return SystemState(
            timestamp=datetime.now(),
            portfolio_value=financial_state.get('total_value', 0),
            cash_position=financial_state.get('cash_position', 0),
            active_positions=active_positions,
            open_orders=[],
            pending_decisions=[],
            alerts=[],
            phase=self.config.get('current_phase', 'Phase_1'),
            risk_metrics={'var_95': rebalance_rec.get('metrics', {}).get('risk_level', 0.05)},
            compliance_status={'fca': 'compliant'},
            last_audit=datetime.now() - timedelta(hours=24)
        )
    
    def _synthesize_decisions(
        self, 
        rebalance_rec: Dict, 
        agent_decisions: List[Dict]
    ) -> List[Dict]:
        """Synthesize decisions from all sources into unified action plan"""
        
        unified = []
        
        # Add financial rebalancing decisions
        if rebalance_rec.get('needs_rebalance', False):
            unified.append({
                'source': 'FinancialEngine',
                'type': 'REBALANCE',
                'priority': 'HIGH',
                'description': f"Rebalance needed: {rebalance_rec.get('description', '')}",
                'actions': rebalance_rec.get('actions', []),
                'requires_approval': True,
                'auto_executable': False,
                'estimated_impact_gbp': None
            })
        
        # Add agent decisions
        for decision_data in agent_decisions:
            unified.append({
                'source': f"Agent:{decision_data.get('id', 'unknown')[:8]}",
                'type': decision_data.get('priority', 'MEDIUM'),
                'priority': decision_data.get('priority', 'MEDIUM'),
                'description': decision_data.get('title', ''),
                'actions': [decision_data.get('recommended_action', '')],
                'requires_approval': True,
                'auto_executable': False,
                'estimated_impact_gbp': None
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        unified.sort(key=lambda d: priority_order.get(d['priority'], 4))
        
        return unified
    
    async def _execute_unified_decisions(self, decisions: List[Dict]) -> Dict:
        """Execute the unified decision set"""
        results = {
            'executed': 0,
            'pending_approval': 0,
            'failed': 0,
            'actions': []
        }
        
        for decision in decisions:
            if decision.get('auto_executable', False) and not decision.get('requires_approval', True):
                # Auto-execute
                results['executed'] += 1
                results['actions'].append({
                    'decision': decision,
                    'status': 'auto_executed',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                # Queue for approval
                results['pending_approval'] += 1
                results['actions'].append({
                    'decision': decision,
                    'status': 'pending_human_approval',
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _log_cycle_results(self, results: Dict):
        """Log cycle results to history"""
        self.decision_history.append({
            'cycle': results['cycle_number'],
            'timestamp': results['timestamp'],
            'summary': {
                'decisions_generated': len(results.get('unified_decisions', [])),
                'critical_alerts': results.get('multi_agent_analysis', {}).get('critical_alerts', 0),
                'agents_active': results.get('multi_agent_analysis', {}).get('agents_run', 0)
            }
        })
    
    def get_command_dashboard(self) -> Dict:
        """Get current system status dashboard"""
        return {
            'system_status': {
                'running': self.is_running,
                'cycles_completed': self.cycle_count,
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
                'last_cycle': self.decision_history[-1]['timestamp'] if self.decision_history else None
            },
            'agents': self.agent_orchestrator.get_agent_status(),
            'engines': {
                'financial_engine': 'active',
                'ml_engine': 'active',
                'data_engine': 'active',
                'multi_agent': 'active'
            },
            'recent_decisions': self.decision_history[-5:] if self.decision_history else []
        }
    
    def generate_executive_report(self) -> str:
        """Generate executive summary report"""
        dashboard = self.get_command_dashboard()
        
        report = f"""
================================================================================
FINANCIAL MASTER - AGENT COMMAND CENTER
Executive Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

SYSTEM STATUS
-------------
Status: {'RUNNING' if dashboard['system_status']['running'] else 'STOPPED'}
Cycles Completed: {dashboard['system_status']['cycles_completed']}
Uptime: {dashboard['system_status']['uptime_hours']:.1f} hours
Last Cycle: {dashboard['system_status']['last_cycle'] or 'N/A'}

ACTIVE AGENTS ({len(dashboard['agents'])} Total)
---------------
"""
        
        for agent_name, status in dashboard['agents'].items():
            report += f"  • {agent_name.upper():20} | {'Active' if status['active'] else 'Inactive':8} | Memory: {status['memory_size']:3d} decisions\n"
        
        report += f"""
ENGINE STATUS
-------------
"""
        for engine, status in dashboard['engines'].items():
            report += f"  • {engine:20} | {status.upper()}\n"
        
        if dashboard['recent_decisions']:
            report += f"""
RECENT ACTIVITY (Last {len(dashboard['recent_decisions'])} Cycles)
----------------
"""
            for entry in dashboard['recent_decisions']:
                report += f"  Cycle #{entry['cycle']:3d} | {entry['timestamp'][:19]} | {entry['summary']['decisions_generated']:2d} decisions | {entry['summary']['critical_alerts']} critical\n"
        
        report += f"""
AGENT SPECIALIZATIONS
---------------------
AI Accountant       → Tax optimization, HMRC compliance, CGT/ISA allowances
AI Lawyer           → FCA/SEC monitoring, platform authorization, legal compliance
AI Governance       → Policy enforcement, audit trails, quorum decisions
AI Regulations      → HMRC CARF, MiCA, tax treaty updates
AI Protocols        → DeFi risk, smart contract audits, yield farming
AI Cyber Security   → Wallet security, API key health, threat detection
AI Blockchain       → Gas optimization, MEV protection, cross-chain
AI Analyst          → Market research, opportunities, sentiment analysis

COMMANDS AVAILABLE
-----------------
run cycle           → Execute one analysis cycle
start continuous    → Begin 24/7 autonomous operation
stop                → Stop continuous operation
status              → Show current system status
report              → Generate executive report
agents              → List all agents and their status
approve <id>        → Approve a pending decision
reject <id>         → Reject a pending decision

================================================================================
"""
        return report
    
    def start_continuous(self):
        """Start continuous autonomous operation"""
        self.is_running = True
        self.start_time = datetime.now()
        logger.info("Starting continuous autonomous operation")
        
        # Schedule regular cycles
        schedule.every(1).hours.do(self._run_async_cycle)  # Hourly analysis
        schedule.every().day.at("09:00").do(self._run_async_cycle)  # Daily morning
        schedule.every().day.at("18:00").do(self._run_async_cycle)  # Daily evening
        schedule.every().sunday.at("10:00").do(self._generate_weekly_report)  # Weekly
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_async_cycle(self):
        """Wrapper to run async cycle from scheduler"""
        asyncio.run(self.run_unified_cycle())
    
    def _generate_weekly_report(self):
        """Generate and save weekly report"""
        report = self.generate_executive_report()
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d')
        with open(f'weekly_report_{timestamp}.txt', 'w') as f:
            f.write(report)
        
        logger.info(f"Weekly report generated: weekly_report_{timestamp}.txt")
    
    def stop(self):
        """Stop continuous operation"""
        self.is_running = False
        logger.info("Stopping continuous operation")


def interactive_mode(command_center: AgentCommandCenter):
    """Interactive command mode"""
    print("\n" + "="*80)
    print("AGENT COMMAND CENTER - INTERACTIVE MODE")
    print("Type 'help' for commands, 'quit' to exit")
    print("="*80 + "\n")
    
    while True:
        try:
            cmd = input("AGENT-CC> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                break
            elif cmd == 'help':
                print("""
Commands:
  run cycle        - Execute one analysis cycle
  status           - Show system status
  report           - Generate executive report
  agents           - List all agents
  dashboard        - Show full dashboard
  help             - Show this help
  quit             - Exit interactive mode
                """)
            elif cmd == 'run cycle':
                print("Running unified cycle...")
                results = asyncio.run(command_center.run_unified_cycle())
                print(f"Cycle #{results['cycle_number']} complete")
                print(f"Decisions: {len(results.get('unified_decisions', []))}")
                print(f"Critical Alerts: {results.get('multi_agent_analysis', {}).get('critical_alerts', 0)}")
            elif cmd == 'status':
                dashboard = command_center.get_command_dashboard()
                print(f"Status: {'Running' if dashboard['system_status']['running'] else 'Stopped'}")
                print(f"Cycles: {dashboard['system_status']['cycles_completed']}")
                print(f"Agents: {len(dashboard['agents'])} active")
            elif cmd == 'report':
                print(command_center.generate_executive_report())
            elif cmd == 'agents':
                dashboard = command_center.get_command_dashboard()
                for agent, status in dashboard['agents'].items():
                    print(f"  {agent:20} | {'Active' if status['active'] else 'Inactive'}")
            elif cmd == 'dashboard':
                print(json.dumps(command_center.get_command_dashboard(), indent=2, default=str))
            else:
                print(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nExiting interactive mode...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Financial Master Agent Command Center')
    parser.add_argument('--mode', choices=['single', 'interactive', 'continuous'], 
                       default='single',
                       help='Operation mode')
    parser.add_argument('--config', default='00_Master_System_Config.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Initialize command center
    command_center = AgentCommandCenter(args.config)
    
    if args.mode == 'single':
        print("Running single unified cycle...")
        results = asyncio.run(command_center.run_unified_cycle())
        print("\n" + "="*80)
        print("CYCLE RESULTS")
        print("="*80)
        print(f"Cycle: #{results['cycle_number']}")
        print(f"Duration: {results.get('cycle_duration_seconds', 0):.2f}s")
        print(f"Decisions Generated: {len(results.get('unified_decisions', []))}")
        print(f"Critical Alerts: {results.get('multi_agent_analysis', {}).get('critical_alerts', 0)}")
        print(f"Pending Approval: {results.get('execution_results', {}).get('pending_approval', 0)}")
        print(f"Auto-Executed: {results.get('execution_results', {}).get('executed', 0)}")
        
        if results.get('unified_decisions'):
            print("\nTop Decisions:")
            for i, d in enumerate(results['unified_decisions'][:5], 1):
                print(f"  {i}. [{d.get('priority', 'MEDIUM')}] {d.get('description', '')[:60]}...")
        
    elif args.mode == 'interactive':
        interactive_mode(command_center)
        
    elif args.mode == 'continuous':
        print("Starting continuous operation. Press Ctrl+C to stop.")
        try:
            command_center.start_continuous()
        except KeyboardInterrupt:
            command_center.stop()
            print("\nStopped.")


if __name__ == "__main__":
    main()
