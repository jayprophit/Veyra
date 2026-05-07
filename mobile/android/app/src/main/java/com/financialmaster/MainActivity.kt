package com.financialmaster

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.NavHostController
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.financialmaster.ui.theme.FinancialMasterTheme
import com.financialmaster.ui.navigation.BottomNavigationBar
import com.financialmaster.ui.screens.LoginScreen
import com.financialmaster.ui.screens.PortfolioScreen
import com.financialmaster.ui.screens.TradingScreen
import com.financialmaster.ui.screens.MarketsScreen
import com.financialmaster.ui.screens.ResearchScreen
import com.financialmaster.ui.screens.ProfileScreen
import com.financialmaster.viewmodel.AuthenticationViewModel
import com.financialmaster.viewmodel.PortfolioViewModel
import com.financialmaster.viewmodel.TradingViewModel
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FinancialMasterTheme {
                FinancialMasterApp()
            }
        }
    }
}

@Composable
fun FinancialMasterApp() {
    val navController = rememberNavController()
    val authViewModel: AuthenticationViewModel = viewModel()
    val portfolioViewModel: PortfolioViewModel = viewModel()
    val tradingViewModel: TradingViewModel = viewModel()
    
    val isAuthenticated by authViewModel.isAuthenticated
    
    if (isAuthenticated) {
        MainNavigation(
            navController = navController,
            authViewModel = authViewModel,
            portfolioViewModel = portfolioViewModel,
            tradingViewModel = tradingViewModel
        )
    } else {
        LoginScreen(
            viewModel = authViewModel,
            onLoginSuccess = {
                // Navigation will be handled by state change
            }
        )
    }
}

@Composable
fun MainNavigation(
    navController: NavHostController,
    authViewModel: AuthenticationViewModel,
    portfolioViewModel: PortfolioViewModel,
    tradingViewModel: TradingViewModel
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    
    Scaffold(
        bottomBar = {
            BottomNavigationBar(
                currentRoute = currentRoute,
                onNavigate = { route ->
                    navController.navigate(route) {
                        popUpTo(navController.graph.startDestinationId) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = "portfolio",
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            composable("portfolio") {
                PortfolioScreen(
                    viewModel = portfolioViewModel,
                    onNavigateToTrading = { symbol ->
                        navController.navigate("trading?symbol=$symbol")
                    }
                )
            }
            
            composable("trading") {
                TradingScreen(
                    viewModel = tradingViewModel
                )
            }
            
            composable("trading?symbol={symbol}") { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: ""
                TradingScreen(
                    viewModel = tradingViewModel,
                    initialSymbol = symbol
                )
            }
            
            composable("markets") {
                MarketsScreen(
                    onNavigateToTrading = { symbol ->
                        navController.navigate("trading?symbol=$symbol")
                    }
                )
            }
            
            composable("research") {
                ResearchScreen()
            }
            
            composable("profile") {
                ProfileScreen(
                    viewModel = authViewModel,
                    onLogout = {
                        authViewModel.logout()
                    }
                )
            }
        }
    }
}
