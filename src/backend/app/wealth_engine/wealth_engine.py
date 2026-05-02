"""Wealth Engine - Main orchestrator with human oversight"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base_allocator import UserProfile, AllocationDecision, AllocationStrategy
from .adaptive_allocator import AdaptiveAllocator
from .holistic_orchestrator import HolisticOrchestrator
from .aggressive_growth_allocator import AggressiveGrowthAllocator
from .conservative_preservation_allocator import ConservativePreservationAllocator
from .multi_pot_allocator import MultiPotAllocator
from .ai_decision_engine import AIDecisionEngine

class WealthEngine:
    """
    Autonomous AI/ML wealth generation engine.
    Makes decisions, executes via APIs, reports to human for oversight.
    """
    
    def __init__(self, profile: UserProfile, mode: str = 'auto'):
        self.profile = profile
        self.mode = mode  # 'manual', 'semi', 'auto'
        self.allocators = {
            'conservative': ConservativePreservationAllocator(profile),
            'adaptive': AdaptiveAllocator(profile.current_capital),
            'holistic': HolisticOrchestrator(profile),
            'aggressive': AggressiveGrowthAllocator(profile),
            'multi_pot': MultiPotAllocator(profile)
        }
        self.ai_engine = AIDecisionEngine()
        self.execution_queue = []
        self.pending_approvals = []
        self.performance_log = []
    
    def run_cycle(self, contribution: float, source: str = 'regular') -> Dict:
        """
        Main execution cycle. Runs daily/weekly.
        1. Detect contribution
        2. AI selects best allocator(s)
        3. Generate allocation plan
        4. Queue for execution (or approval)
        5. Execute if auto mode
        """
        # Step 1: Update profile with new capital
        old_capital = self.profile.current_capital
        self.profile.current_capital += contribution
        
        # Step 2: AI selects strategy
        market_conditions = self._get_market_conditions()
        selected = self.ai_engine.select_allocator(
            self.profile, contribution, market_conditions
        )
        
        # Step 3: Generate allocation
        if selected.startswith('blend:'):
            # Use multiple allocators
            alloc_names = selected.replace('blend:', '').split(',')
            decision = self._blend_allocators(alloc_names, contribution, source)
        else:
            # Use single allocator
            allocator = self.allocators[selected]
            context = {'source': source, 'market': market_conditions}
            decision = allocator.allocate(contribution, context)
        
        # Step 4: Handle based on mode
        if self.mode == 'manual':
            self.pending_approvals.append(decision)
            return {
                'status': 'pending_approval',
                'decision': decision,
                'action_required': 'Review and approve allocation'
            }
        
        elif self.mode == 'semi':
            self.pending_approvals.append(decision)
            # Auto-execute if confidence high
            if decision.confidence > 0.8:
                return self._execute(decision)
            return {
                'status': 'pending_approval_low_confidence',
                'decision': decision,
                'action_required': 'Review recommended'
            }
        
        else:  # auto
            return self._execute(decision)
    
    def _execute(self, decision: AllocationDecision) -> Dict:
        """Execute allocation decision via APIs"""
        results = []
        
        for alloc in decision.allocations:
            try:
                result = self._execute_allocation(alloc)
                results.append({'allocation': alloc, 'status': 'success', 'result': result})
            except Exception as e:
                results.append({'allocation': alloc, 'status': 'failed', 'error': str(e)})
        
        self.performance_log.append({
            'timestamp': datetime.now(),
            'decision': decision,
            'results': results
        })
        
        return {
            'status': 'executed',
            'decision': decision,
            'results': results,
            'next_run': datetime.now() + timedelta(days=7)
        }
    
    def _execute_allocation(self, alloc: Dict) -> Dict:
        """Execute single allocation via API"""
        # Placeholder for actual API calls
        return {
            'platform': alloc.get('platform', 'unknown'),
            'amount': alloc['amount'],
            'strategy': alloc.get('module', 'unknown'),
            'tx_id': f"simulated_{datetime.now().timestamp()}",
            'status': 'completed'
        }
    
    def approve_pending(self, decision_id: Optional[str] = None) -> Dict:
        """Human approves pending decision"""
        if not self.pending_approvals:
            return {'status': 'no_pending'}
        
        if decision_id:
            decision = next((d for d in self.pending_approvals if str(d.timestamp) == decision_id), None)
        else:
            decision = self.pending_approvals[0]
        
        if decision:
            self.pending_approvals.remove(decision)
            return self._execute(decision)
        
        return {'status': 'decision_not_found'}
    
    def get_dashboard(self) -> Dict:
        """Get current wealth status"""
        return {
            'profile': self.profile,
            'current_capital': self.profile.current_capital,
            'target_progress': self.profile.current_capital / self.profile.target_capital if self.profile.target_capital else 0,
            'active_allocators': list(self.allocators.keys()),
            'pending_approvals': len(self.pending_approvals),
            'total_allocations': len(self.performance_log),
            'mode': self.mode
        }
    
    def _get_market_conditions(self) -> Dict:
        """Fetch current market data"""
        return {
            'volatility': 0.5,  # Placeholder
            'trend': 'neutral',
            'interest_rates': 0.05,
            'timestamp': datetime.now()
        }
    
    def _blend_allocators(self, names: List[str], amount: float, source: str) -> AllocationDecision:
        """Blend multiple allocator outputs"""
        # Simplified - take 50/50 of first two
        allocs = []
        
        for name in names[:2]:
            allocator = self.allocators.get(name.strip())
            if allocator:
                context = {'source': source}
                decision = allocator.allocate(amount / 2, context)
                allocs.extend(decision.allocations)
        
        return AllocationDecision(
            timestamp=datetime.now(),
            amount=amount,
            source=source,
            strategy=AllocationStrategy.AI_OPTIMIZED,
            allocations=allocs,
            expected_return_annual=0.07,
            risk_score=0.4,
            liquidity_score=0.75,
            confidence=0.7,
            reasoning=f"Blended strategy: {', '.join(names)}"
        )
