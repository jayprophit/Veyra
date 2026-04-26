import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:provider/provider.dart';

import 'blocs/auth/auth_bloc.dart';
import 'blocs/portfolio/portfolio_bloc.dart';
import 'blocs/market/market_bloc.dart';
import 'blocs/trading/trading_bloc.dart';

import 'services/api_service.dart';
import 'services/websocket_service.dart';
import 'services/biometric_service.dart';
import 'services/local_storage.dart';

import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/trading/trading_screen.dart';
import 'screens/portfolio/portfolio_screen.dart';
import 'screens/analysis/analysis_screen.dart';
import 'screens/vision/oracle_vision_screen.dart';
import 'screens/social/social_trading_screen.dart';
import 'screens/settings/settings_screen.dart';

import 'themes/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
    ),
  );
  
  runApp(const FinancialMasterApp());
}

class FinancialMasterApp extends StatelessWidget {
  const FinancialMasterApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(create: (_) => ApiService()),
        Provider<WebSocketService>(create: (_) => WebSocketService()),
        Provider<BiometricService>(create: (_) => BiometricService()),
        Provider<LocalStorage>(create: (_) => LocalStorage()),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<AuthBloc>(
            create: (context) => AuthBloc(
              apiService: context.read<ApiService>(),
              biometricService: context.read<BiometricService>(),
            ),
          ),
          BlocProvider<PortfolioBloc>(
            create: (context) => PortfolioBloc(
              apiService: context.read<ApiService>(),
              websocketService: context.read<WebSocketService>(),
            ),
          ),
          BlocProvider<MarketBloc>(
            create: (context) => MarketBloc(
              apiService: context.read<ApiService>(),
              websocketService: context.read<WebSocketService>(),
            ),
          ),
          BlocProvider<TradingBloc>(
            create: (context) => TradingBloc(
              apiService: context.read<ApiService>(),
            ),
          ),
        ],
        child: MaterialApp(
          title: 'Financial Master',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.darkTheme,
          initialRoute: '/',
          routes: {
            '/': (context) => const SplashScreen(),
            '/login': (context) => const LoginScreen(),
            '/dashboard': (context) => const DashboardScreen(),
            '/trading': (context) => const TradingScreen(),
            '/portfolio': (context) => const PortfolioScreen(),
            '/analysis': (context) => const AnalysisScreen(),
            '/oracle_vision': (context) => const OracleVisionScreen(),
            '/social': (context) => const SocialTradingScreen(),
            '/settings': (context) => const SettingsScreen(),
          },
        ),
      ),
    );
  }
}
