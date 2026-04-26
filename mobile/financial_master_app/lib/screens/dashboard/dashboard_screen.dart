import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';

import '../../blocs/portfolio/portfolio_bloc.dart';
import '../../blocs/market/market_bloc.dart';
import '../../models/portfolio.dart';
import '../../widgets/charts/portfolio_chart.dart';
import '../../widgets/cards/asset_card.dart';
import '../../widgets/cards/ai_insight_card.dart';
import '../../widgets/common/loading_indicator.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final currencyFormat = NumberFormat.currency(symbol: '\$', decimalDigits: 2);
  final percentFormat = NumberFormat.percentPattern();
  
  @override
  void initState() {
    super.initState();
    context.read<PortfolioBloc>().add(LoadPortfolio());
    context.read<MarketBloc>().add(LoadMarketData());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            _buildAppBar(),
            SliverToBoxAdapter(
              child: BlocBuilder<PortfolioBloc, PortfolioState>(
                builder: (context, state) {
                  if (state is PortfolioLoading) {
                    return const LoadingIndicator();
                  } else if (state is PortfolioLoaded) {
                    return _buildDashboardContent(state.portfolio);
                  } else if (state is PortfolioError) {
                    return _buildErrorWidget(state.message);
                  }
                  return const SizedBox.shrink();
                },
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      expandedHeight: 120,
      floating: true,
      pinned: true,
      backgroundColor: const Color(0xFF0D1117),
      elevation: 0,
      flexibleSpace: FlexibleSpaceBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            const Text(
              'Financial Master',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
            BlocBuilder<PortfolioBloc, PortfolioState>(
              builder: (context, state) {
                if (state is PortfolioLoaded) {
                  return Text(
                    currencyFormat.format(state.portfolio.totalValue),
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  );
                }
                return const Text(
                  '\$0.00',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                );
              },
            ),
          ],
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.notifications, color: Colors.white),
          onPressed: () => Navigator.pushNamed(context, '/notifications'),
        ),
        IconButton(
          icon: const Icon(Icons.settings, color: Colors.white),
          onPressed: () => Navigator.pushNamed(context, '/settings'),
        ),
      ],
    );
  }

  Widget _buildDashboardContent(Portfolio portfolio) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Portfolio Change
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: portfolio.dayChange >= 0 
                    ? Colors.green.withOpacity(0.2) 
                    : Colors.red.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    Icon(
                      portfolio.dayChange >= 0 ? Icons.arrow_upward : Icons.arrow_downward,
                      color: portfolio.dayChange >= 0 ? Colors.green : Colors.red,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${portfolio.dayChange >= 0 ? '+' : ''}${currencyFormat.format(portfolio.dayChange)}',
                      style: TextStyle(
                        color: portfolio.dayChange >= 0 ? Colors.green : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '(${percentFormat.format(portfolio.dayChangePercent / 100)})',
                      style: TextStyle(
                        color: portfolio.dayChange >= 0 ? Colors.green : Colors.red,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: () => Navigator.pushNamed(context, '/analysis'),
                icon: const Icon(Icons.insights, size: 16),
                label: const Text('AI Analysis'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.blue,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Portfolio Chart
        SizedBox(
          height: 200,
          child: PortfolioChart(
            data: portfolio.historicalData,
            isPositive: portfolio.totalReturn >= 0,
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Quick Actions
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              _buildQuickAction(
                icon: Icons.add_chart,
                label: 'Trade',
                color: Colors.blue,
                onTap: () => Navigator.pushNamed(context, '/trading'),
              ),
              const SizedBox(width: 12),
              _buildQuickAction(
                icon: Icons.people,
                label: 'Social',
                color: Colors.purple,
                onTap: () => Navigator.pushNamed(context, '/social'),
              ),
              const SizedBox(width: 12),
              _buildQuickAction(
                icon: Icons.visibility,
                label: 'Oracle',
                color: Colors.orange,
                onTap: () => Navigator.pushNamed(context, '/oracle_vision'),
              ),
              const SizedBox(width: 12),
              _buildQuickAction(
                icon: Icons.savings,
                label: 'Auto-Save',
                color: Colors.green,
                onTap: () => Navigator.pushNamed(context, '/savings'),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // AI Insights
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'AI Insights',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ),
        
        const SizedBox(height: 12),
        
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              AIInsightCard(
                title: 'Pattern Detected',
                description: 'Head & Shoulders pattern on AAPL 4H chart',
                confidence: 0.82,
                action: 'Review',
                onTap: () {},
              ),
              const SizedBox(width: 12),
              AIInsightCard(
                title: 'Market Alert',
                description: 'VIX spike detected - consider hedging',
                confidence: 0.75,
                action: 'Hedge',
                isWarning: true,
                onTap: () {},
              ),
              const SizedBox(width: 12),
              AIInsightCard(
                title: 'Tax Opportunity',
                description: 'TSLA position showing -$1,200 unrealized loss',
                confidence: 0.91,
                action: 'Harvest',
                onTap: () {},
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Top Holdings
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'Top Holdings',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ),
        
        const SizedBox(height: 12),
        
        ...portfolio.topHoldings.map((holding) => AssetCard(
          symbol: holding.symbol,
          name: holding.name,
          quantity: holding.quantity,
          currentPrice: holding.currentPrice,
          dayChange: holding.dayChange,
          totalValue: holding.totalValue,
          allocation: holding.allocation,
        )).toList(),
        
        const SizedBox(height: 32),
        
        // Watchlist
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Watchlist',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              TextButton(
                onPressed: () {},
                child: Text('See All'),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Watchlist items
        BlocBuilder<MarketBloc, MarketState>(
          builder: (context, state) {
            if (state is MarketLoaded) {
              return Column(
                children: state.watchlist.map((stock) => ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.blue.withOpacity(0.2),
                    child: Text(
                      stock.symbol.substring(0, 1),
                      style: const TextStyle(color: Colors.blue),
                    ),
                  ),
                  title: Text(
                    stock.symbol,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  subtitle: Text(
                    stock.name,
                    style: const TextStyle(color: Colors.grey),
                  ),
                  trailing: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        currencyFormat.format(stock.price),
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${stock.change >= 0 ? '+' : ''}${percentFormat.format(stock.changePercent / 100)}',
                        style: TextStyle(
                          color: stock.change >= 0 ? Colors.green : Colors.red,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                )).toList(),
              );
            }
            return const LoadingIndicator();
          },
        ),
        
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorWidget(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 48),
          const SizedBox(height: 16),
          Text(
            message,
            style: const TextStyle(color: Colors.white),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              context.read<PortfolioBloc>().add(LoadPortfolio());
            },
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        border: Border(
          top: BorderSide(
            color: Colors.white.withOpacity(0.1),
          ),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(Icons.dashboard, 'Home', true),
              _buildNavItem(Icons.pie_chart, 'Portfolio', false, onTap: () => Navigator.pushNamed(context, '/portfolio')),
              _buildNavItem(Icons.show_chart, 'Trade', false, onTap: () => Navigator.pushNamed(context, '/trading')),
              _buildNavItem(Icons.insights, 'Vision', false, onTap: () => Navigator.pushNamed(context, '/oracle_vision')),
              _buildNavItem(Icons.person, 'Profile', false),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, bool isActive, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? Colors.blue : Colors.grey,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: isActive ? Colors.blue : Colors.grey,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
