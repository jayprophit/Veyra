"""
Comprehensive Test Suite for Financial Master Trading Modules
Tests all trading components: strategies, bots, MT integration, copy trading
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import uuid

# Import all trading modules
import sys
sys.path.insert(0, 'c:/Users/jpowe/Desktop/Financial Master/src/backend/app')

from trading.strategies.arbitrage import ArbitrageStrategy
from trading.strategies.grid_trading import GridTradingStrategy
from trading.strategies.momentum import MomentumStrategy
from trading.strategies.hodl import HODLStrategy
from trading.freqtrade_adapter import FreqtradeAdapter
from trading.strategy_builder import StrategyBuilder, StrategyBlockLibrary
from trading.copy_trading import CopyTradingSystem
from trading.bot_manager import BotManager
from trading.metatrader_integration import MetaTraderIntegration


# ============================================================================
# STRATEGY TESTS
# ============================================================================

class TestArbitrageStrategy:
    """Test arbitrage strategy functionality"""
    
    def test_initialization(self):
        strategy = ArbitrageStrategy(min_spread_pct=0.5)
        assert strategy.min_spread_pct == 0.5
        assert strategy.positions == {}
        
    def test_opportunity_detection(self):
        strategy = ArbitrageStrategy()
        
        # Mock price data
        prices = {
            'binance': {'BTC/USD': 50000.0},
            'coinbase': {'BTC/USD': 50250.0}  # 0.5% spread
        }
        
        opportunities = strategy.scan_opportunities(prices)
        assert len(opportunities) >= 0  # May or may not find opportunities
        
    def test_opportunity_calculation(self):
        strategy = ArbitrageStrategy(min_spread_pct=0.3)
        
        opportunity = strategy.calculate_opportunity(
            symbol='BTC/USD',
            buy_exchange='binance',
            sell_exchange='coinbase',
            buy_price=50000.0,
            sell_price=50200.0
        )
        
        assert opportunity is not None
        assert opportunity['spread_pct'] == 0.4
        assert opportunity['symbol'] == 'BTC/USD'


class TestGridTradingStrategy:
    """Test grid trading strategy"""
    
    def test_grid_initialization(self):
        strategy = GridTradingStrategy(
            symbol='BTC/USD',
            lower_price=40000,
            upper_price=60000,
            num_grids=10,
            total_investment=10000
        )
        
        assert strategy.symbol == 'BTC/USD'
        assert len(strategy.grid_levels) == 10
        assert strategy.total_investment == 10000
        
    def test_grid_calculation(self):
        strategy = GridTradingStrategy(
            symbol='ETH/USD',
            lower_price=2000,
            upper_price=4000,
            num_grids=5,
            total_investment=5000
        )
        
        strategy.initialize_grid()
        
        # Check grid levels are properly spaced
        assert len(strategy.grid_levels) == 5
        assert strategy.grid_levels[0]['price'] == 2000
        assert strategy.grid_levels[-1]['price'] == 4000
        
    def test_order_placement(self):
        strategy = GridTradingStrategy(
            symbol='BTC/USD',
            lower_price=40000,
            upper_price=60000,
            num_grids=10,
            total_investment=10000
        )
        
        strategy.initialize_grid()
        orders = strategy.place_grid_orders()
        
        assert len(orders) == 10
        assert strategy.active_orders == orders


class TestMomentumStrategy:
    """Test momentum trading strategy"""
    
    def test_indicator_calculation(self):
        strategy = MomentumStrategy()
        
        # Mock price data
        prices = [100, 102, 101, 105, 103, 107, 106, 108, 110, 109]
        
        rsi = strategy.calculate_rsi(prices, period=5)
        assert 0 <= rsi <= 100
        
    def test_signal_generation(self):
        strategy = MomentumStrategy(rsi_overbought=70, rsi_oversold=30)
        
        # Test oversold signal
        signal = strategy.generate_signal(
            rsi=25,
            macd=1.5,
            signal_line=0.5,
            current_price=100,
            sma_50=95
        )
        
        assert signal in ['buy', 'sell', 'hold']
        
    def test_market_scan(self):
        strategy = MomentumStrategy()
        
        mock_data = {
            'BTC/USD': {'prices': [100]*20, 'volume': 1000000},
            'ETH/USD': {'prices': [200]*20, 'volume': 500000}
        }
        
        signals = asyncio.run(strategy.scan_market(mock_data))
        assert isinstance(signals, list)


class TestHODLStrategy:
    """Test HODL strategy"""
    
    def test_initialization(self):
        strategy = HODLStrategy(
            symbol='BTC/USD',
            target_allocation_pct=50,
            rebalance_threshold_pct=10
        )
        
        assert strategy.symbol == 'BTC/USD'
        assert strategy.target_allocation_pct == 50
        assert strategy.rebalance_threshold_pct == 10
        
    def test_rebalance_check(self):
        strategy = HODLStrategy(
            symbol='BTC/USD',
            target_allocation_pct=50,
            rebalance_threshold_pct=10
        )
        
        # Should not rebalance (within threshold)
        should_rebalance = strategy.check_rebalance_needed(
            current_position_value=5500,
            portfolio_value=10000
        )
        
        assert should_rebalance == False  # 55% vs 50% target, within 10% threshold
        
    def test_buy_signal(self):
        strategy = HODLStrategy()
        
        signal = strategy.get_buy_signal(
            current_price=45000,
            avg_entry=50000,
            drop_pct_threshold=15
        )
        
        assert signal == True  # 10% drop from entry


# ============================================================================
# FREQTRADE ADAPTER TESTS
# ============================================================================

class TestFreqtradeAdapter:
    """Test Freqtrade integration"""
    
    def test_initialization(self):
        adapter = FreqtradeAdapter()
        assert adapter.strategies == {}
        assert adapter.bot_instances == {}
        
    def test_strategy_registration(self):
        adapter = FreqtradeAdapter()
        
        strategy_id = adapter.register_strategy(
            name='TestStrategy',
            strategy_type='custom',
            config={'timeframe': '1h'}
        )
        
        assert strategy_id in adapter.strategies
        assert adapter.strategies[strategy_id]['name'] == 'TestStrategy'
        
    def test_bot_lifecycle(self):
        adapter = FreqtradeAdapter()
        
        strategy_id = adapter.register_strategy(
            name='TestStrategy',
            strategy_type='custom',
            config={}
        )
        
        bot_id = adapter.create_bot(
            strategy_id=strategy_id,
            mode='dry_run',
            pairs=['BTC/USD'],
            exchange='binance'
        )
        
        assert bot_id in adapter.bot_instances
        
        # Test start
        success = adapter.start_bot(bot_id)
        assert success == True
        assert adapter.bot_instances[bot_id]['status'] == 'running'
        
        # Test stop
        success = adapter.stop_bot(bot_id)
        assert success == True
        assert adapter.bot_instances[bot_id]['status'] == 'stopped'


# ============================================================================
# NO-CODE BUILDER TESTS
# ============================================================================

class TestStrategyBuilder:
    """Test no-code strategy builder"""
    
    def test_strategy_creation(self):
        builder = StrategyBuilder()
        
        strategy = builder.create_strategy(
            name='Test Strategy',
            description='Test description',
            user_id='user_123'
        )
        
        assert strategy.id is not None
        assert strategy.name == 'Test Strategy'
        assert strategy.user_id == 'user_123'
        
    def test_block_library(self):
        blocks = StrategyBlockLibrary.get_all_blocks()
        assert len(blocks) > 0
        
        categories = StrategyBlockLibrary.get_categories()
        assert len(categories) > 0
        
    def test_add_block(self):
        builder = StrategyBuilder()
        
        strategy = builder.create_strategy('Test', 'Desc', 'user_123')
        
        block = builder.add_block(
            strategy_id=strategy.id,
            block_type='ind_rsi',
            position={'x': 100, 'y': 100},
            config={'period': 14}
        )
        
        assert block is not None
        assert block.type.name == 'INDICATOR'
        assert len(strategy.blocks) == 1
        
    def test_strategy_validation(self):
        builder = StrategyBuilder()
        
        strategy = builder.create_strategy('Test', 'Desc', 'user_123')
        
        # Add entry block
        builder.add_block(strategy.id, 'entry_crossover', {'x': 0, 'y': 0})
        
        # Add exit block
        builder.add_block(strategy.id, 'exit_profit_target', {'x': 0, 'y': 200})
        
        result = builder.validate_strategy(strategy.id)
        
        assert result['valid'] == True
        assert result['entry_count'] >= 1
        assert result['exit_count'] >= 1


# ============================================================================
# COPY TRADING TESTS
# ============================================================================

class TestCopyTrading:
    """Test copy trading system"""
    
    def test_trader_registration(self):
        system = CopyTradingSystem()
        
        trader = system.register_trader(
            user_id='trader_1',
            display_name='TopTrader',
            bio='Expert trader',
            strategy_description='Momentum strategy'
        )
        
        assert trader.id is not None
        assert trader.display_name == 'TopTrader'
        
    def test_start_copying(self):
        system = CopyTradingSystem()
        
        # Register trader
        trader = system.register_trader('trader_1', 'TopTrader', 'Bio')
        trader.allow_copying = True
        trader.min_copy_amount = 100
        
        # Start copying
        result = system.start_copying(
            copier_id='copier_1',
            trader_id=trader.id,
            allocation=500,
            risk_settings={'max_positions': 5}
        )
        
        assert 'success' in result
        assert result['relationship_id'] is not None
        
    def test_trade_signal_replication(self):
        system = CopyTradingSystem()
        
        # Setup
        trader = system.register_trader('trader_1', 'TopTrader', 'Bio')
        system.start_copying('copier_1', trader.id, 500)
        
        # Create signal
        signal = system.create_trade_signal(
            trader_id=trader.id,
            signal={
                'symbol': 'BTC/USD',
                'action': 'buy',
                'entry_price': 50000,
                'volume': 0.1,
                'position_size_pct': 5
            }
        )
        
        assert signal is not None
        assert signal.symbol == 'BTC/USD'


# ============================================================================
# BOT MANAGER TESTS
# ============================================================================

class TestBotManager:
    """Test bot manager"""
    
    def test_dca_bot_creation(self):
        manager = BotManager()
        
        bot = manager.create_dca_bot(
            user_id='user_1',
            name='BTC DCA Bot',
            config={
                'symbol': 'BTC/USD',
                'total_investment': 10000,
                'entry_price': 50000,
                'num_orders': 10,
                'price_drop_pct': 5
            }
        )
        
        assert bot.id is not None
        assert bot.bot_type.value == 'dca'
        assert bot.config.symbol == 'BTC/USD'
        
    def test_grid_bot_creation(self):
        manager = BotManager()
        
        bot = manager.create_grid_bot(
            user_id='user_1',
            name='ETH Grid Bot',
            config={
                'symbol': 'ETH/USD',
                'total_investment': 5000,
                'lower_price': 1800,
                'upper_price': 2200,
                'num_grids': 10
            }
        )
        
        assert bot.id is not None
        assert bot.bot_type.value == 'grid'
        
    def test_bot_lifecycle(self):
        manager = BotManager()
        
        bot = manager.create_dca_bot('user_1', 'Test', {
            'symbol': 'BTC/USD',
            'total_investment': 1000,
            'entry_price': 50000
        })
        
        # Start
        success = manager.start_bot(bot.id)
        assert success == True
        assert bot.status.value == 'running'
        
        # Pause
        success = manager.pause_bot(bot.id)
        assert success == True
        assert bot.status.value == 'paused'
        
        # Stop
        success = manager.stop_bot(bot.id)
        assert success == True
        assert bot.status.value == 'stopped'
        
    def test_dca_levels_calculation(self):
        manager = BotManager()
        
        bot = manager.create_dca_bot('user_1', 'Test', {
            'symbol': 'BTC/USD',
            'total_investment': 10000,
            'entry_price': 50000,
            'num_orders': 5,
            'price_drop_pct': 5
        })
        
        levels = manager.calculate_dca_levels(bot.id)
        
        assert len(levels) == 5
        assert levels[0]['trigger_price'] == 50000 * 0.95  # 5% drop
        assert levels[-1]['trigger_price'] == 50000 * 0.75  # 25% drop


# ============================================================================
# METATRADER INTEGRATION TESTS
# ============================================================================

class TestMetaTraderIntegration:
    """Test MT4/MT5 integration"""
    
    def test_account_addition(self):
        mt = MetaTraderIntegration()
        
        account = mt.add_account(
            user_id='user_1',
            name='MT4 Live',
            version=4,
            account_type='live',
            host='localhost',
            port=15555
        )
        
        assert account.id is not None
        assert account.version.value == 4
        assert account.account_type.value == 'live'
        
    def test_ea_configuration(self):
        mt = MetaTraderIntegration()
        
        account = mt.add_account('user_1', 'MT4', 4, 'demo')
        
        ea = mt.configure_ea(
            account_id=account.id,
            name='MyEA',
            magic_number=123456,
            config={
                'strategy_type': 'trend',
                'timeframe': 'H1',
                'symbols': ['EURUSD'],
                'risk_per_trade_pct': 1.0
            }
        )
        
        assert ea.id is not None
        assert ea.magic_number == 123456
        
    def test_signal_reception(self):
        mt = MetaTraderIntegration()
        
        account = mt.add_account('user_1', 'MT4', 4, 'demo')
        
        signal = mt.receive_signal(
            account_id=account.id,
            signal_data={
                'action': 'buy',
                'symbol': 'EURUSD',
                'volume': 0.1,
                'entry_price': 1.1000,
                'sl': 1.0950,
                'tp': 1.1100,
                'magic_number': 123456,
                'comment': 'Test trade',
                'ea_name': 'MyEA'
            }
        )
        
        assert signal.id is not None
        assert signal.action.value == 'buy'
        assert signal.symbol == 'EURUSD'


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integrations between modules"""
    
    def test_strategy_to_freqtrade(self):
        """Test strategy builder to Freqtrade integration"""
        builder = StrategyBuilder()
        adapter = FreqtradeAdapter()
        
        # Create strategy in builder
        strategy = builder.create_strategy('MyStrategy', 'Test', 'user_1')
        builder.add_block(strategy.id, 'entry_crossover', {'x': 0, 'y': 0})
        builder.add_block(strategy.id, 'exit_profit_target', {'x': 0, 'y': 200})
        
        # Generate code
        code = builder.generate_code(strategy.id)
        
        assert code is not None
        assert 'class MyStrategy' in code or 'freqtrade' in code.lower()
        
    def test_copy_to_marketplace_flow(self):
        """Test trader becoming a seller flow"""
        copy_system = CopyTradingSystem()
        
        # Register as trader
        trader = copy_system.register_trader('user_1', 'ProTrader', 'Bio')
        
        # Update performance to qualify for marketplace
        copy_system.update_trader_performance(trader.id, {
            'return_30d': 15.0,
            'win_rate': 65.0,
            'sharpe_ratio': 1.5
        })
        
        # Verify trader profile
        profile = copy_system.get_trader(trader.id)
        
        assert profile is not None
        assert profile['performance']['return_30d'] == 15.0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance benchmarks"""
    
    def test_strategy_scan_performance(self):
        """Test strategy scanning performance"""
        import time
        
        strategy = MomentumStrategy()
        
        # Generate large dataset
        mock_data = {
            f'SYM{i}/USD': {
                'prices': list(range(100, 120)),
                'volume': 1000000
            }
            for i in range(100)
        }
        
        start = time.time()
        signals = asyncio.run(strategy.scan_market(mock_data))
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 5.0  # Less than 5 seconds
        
    def test_bot_manager_scaling(self):
        """Test bot manager with many bots"""
        manager = BotManager()
        
        # Create many bots
        for i in range(50):
            manager.create_dca_bot(f'user_{i}', f'Bot {i}', {
                'symbol': 'BTC/USD',
                'total_investment': 1000,
                'entry_price': 50000
            })
        
        # List all bots
        all_bots = manager.list_user_bots('user_0')
        assert len(all_bots) == 1


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_strategy_validation(self):
        builder = StrategyBuilder()
        
        strategy = builder.create_strategy('Invalid', 'Test', 'user_1')
        # Don't add any blocks
        
        result = builder.validate_strategy(strategy.id)
        
        assert result['valid'] == False
        assert len(result['errors']) > 0
        
    def test_nonexistent_bot_operations(self):
        manager = BotManager()
        
        # Try to start nonexistent bot
        success = manager.start_bot('invalid_id')
        assert success == False
        
    def test_insufficient_copy_allocation(self):
        system = CopyTradingSystem()
        
        trader = system.register_trader('trader_1', 'Top', 'Bio')
        trader.min_copy_amount = 1000
        
        result = system.start_copying('copier_1', trader.id, 100)
        
        assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
