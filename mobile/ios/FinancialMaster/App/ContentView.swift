import SwiftUI
import Combine

@main
struct FinancialMasterApp: App {
    @StateObject private var authenticationManager = AuthenticationManager()
    @StateObject private var portfolioManager = PortfolioManager()
    @StateObject private var tradingManager = TradingManager()
    @StateObject private var notificationManager = NotificationManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authenticationManager)
                .environmentObject(portfolioManager)
                .environmentObject(tradingManager)
                .environmentObject(notificationManager)
                .onAppear {
                    setupApp()
                }
        }
    }
    
    private func setupApp() {
        // Initialize app services
        Task {
            await notificationManager.requestPermissions()
            await portfolioManager.loadPortfolio()
            await tradingManager.initialize()
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var authenticationManager: AuthenticationManager
    
    var body: some View {
        Group {
            if authenticationManager.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .animation(.easeInOut, value: authenticationManager.isAuthenticated)
    }
}

struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            PortfolioView()
                .tabItem {
                    Label("Portfolio", systemImage: "chart.pie.fill")
                }
                .tag(0)
            
            TradingView()
                .tabItem {
                    Label("Trading", systemImage: "arrow.up.arrow.down")
                }
                .tag(1)
            
            MarketsView()
                .tabItem {
                    Label("Markets", systemImage: "globe")
                }
                .tag(2)
            
            ResearchView()
                .tabItem {
                    Label("Research", systemImage: "magnifyingglass")
                }
                .tag(3)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(4)
        }
        .accentColor(.blue)
    }
}

struct LoginView: View {
    @EnvironmentObject var authenticationManager: AuthenticationManager
    @State private var username = ""
    @State private var password = ""
    @State private var showingBiometric = false
    @State private var errorMessage = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Logo and Title
                VStack(spacing: 10) {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                    
                    Text("Financial Master")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Enterprise Trading Platform")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 50)
                
                // Login Form
                VStack(spacing: 15) {
                    TextField("Username", text: $username)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                    
                    Button(action: login) {
                        Text("Sign In")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(username.isEmpty || password.isEmpty)
                    
                    Button(action: biometricLogin) {
                        HStack {
                            Image(systemName: "faceid")
                            Text("Sign in with Face ID")
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.horizontal)
                
                Spacer()
                
                // Footer
                VStack(spacing: 5) {
                    Text("Version 1.0.0")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text("© 2026 Financial Master")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.bottom)
            }
            .navigationTitle("Login")
            .navigationBarHidden(true)
        }
    }
    
    private func login() {
        Task {
            do {
                try await authenticationManager.login(username: username, password: password)
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
    
    private func biometricLogin() {
        Task {
            do {
                try await authenticationManager.authenticateWithBiometrics()
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}

struct PortfolioView: View {
    @EnvironmentObject var portfolioManager: PortfolioManager
    @State private var portfolio: Portfolio?
    @State private var isLoading = true
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading portfolio...")
                } else if let portfolio = portfolio {
                    PortfolioContentView(portfolio: portfolio)
                } else {
                    Text("No portfolio data available")
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Portfolio")
            .task {
                await loadPortfolio()
            }
            .refreshable {
                await loadPortfolio()
            }
        }
    }
    
    private func loadPortfolio() async {
        isLoading = true
        portfolio = await portfolioManager.getPortfolio()
        isLoading = false
    }
}

struct PortfolioContentView: View {
    let portfolio: Portfolio
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Portfolio Summary Card
                PortfolioSummaryCard(portfolio: portfolio)
                
                // Performance Chart
                PerformanceChartView(portfolio: portfolio)
                
                // Holdings List
                HoldingsListView(holdings: portfolio.holdings)
                
                // Recent Transactions
                RecentTransactionsView(transactions: portfolio.recentTransactions)
            }
            .padding()
        }
    }
}

struct PortfolioSummaryCard: View {
    let portfolio: Portfolio
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Portfolio Summary")
                .font(.headline)
                .fontWeight(.bold)
            
            HStack {
                VStack(alignment: .leading) {
                    Text("Total Value")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("$\(portfolio.totalValue, specifier: "%.2f")")
                        .font(.title2)
                        .fontWeight(.bold)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("Today's Change")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("\(portfolio.todayChange, specifier: "%+.2f")")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(portfolio.todayChange >= 0 ? .green : .red)
                }
            }
            
            Divider()
            
            HStack {
                StatItem(title: "Holdings", value: "\(portfolio.holdings.count)")
                Spacer()
                StatItem(title: "Gain/Loss", value: "$\(portfolio.totalGainLoss, specifier: "%.2f")")
                Spacer()
                StatItem(title: "Return", value: "\(portfolio.totalReturn, specifier: "%.2f")%")
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct StatItem: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
        }
    }
}

struct PerformanceChartView: View {
    let portfolio: Portfolio
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Performance")
                .font(.headline)
                .fontWeight(.bold)
            
            // Mock performance chart
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.blue.opacity(0.1))
                .frame(height: 200)
                .overlay(
                    Text("Performance Chart")
                        .foregroundColor(.blue)
                )
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct HoldingsListView: View {
    let holdings: [Holding]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Holdings")
                .font(.headline)
                .fontWeight(.bold)
            
            ForEach(holdings.prefix(5)) { holding in
                HoldingRowView(holding: holding)
            }
            
            if holdings.count > 5 {
                NavigationLink("View All Holdings") {
                    AllHoldingsView(holdings: holdings)
                }
                .font(.caption)
                .foregroundColor(.blue)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct HoldingRowView: View {
    let holding: Holding
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(holding.symbol)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text(holding.name)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing) {
                Text("$\(holding.value, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text("\(holding.quantity, specifier: "%.2f") shares")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            VStack(alignment: .trailing) {
                Text("\(holding.change, specifier: "%+.2f")")
                    .font(.caption)
                    .foregroundColor(holding.change >= 0 ? .green : .red)
            }
        }
        .padding(.vertical, 5)
    }
}

struct RecentTransactionsView: View {
    let transactions: [Transaction]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Recent Transactions")
                .font(.headline)
                .fontWeight(.bold)
            
            ForEach(transactions.prefix(3)) { transaction in
                TransactionRowView(transaction: transaction)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct TransactionRowView: View {
    let transaction: Transaction
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(transaction.symbol)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text(transaction.type.rawValue)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing) {
                Text("\(transaction.type == .buy ? "+" : "-")$\(transaction.amount, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(transaction.type == .buy ? .green : .red)
                Text(transaction.date, style: .date)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 5)
    }
}

// Placeholder views for other tabs
struct TradingView: View {
    var body: some View {
        NavigationView {
            Text("Trading Interface")
                .navigationTitle("Trading")
        }
    }
}

struct MarketsView: View {
    var body: some View {
        NavigationView {
            Text("Markets Overview")
                .navigationTitle("Markets")
        }
    }
}

struct ResearchView: View {
    var body: some View {
        NavigationView {
            Text("Research & Analysis")
                .navigationTitle("Research")
        }
    }
}

struct ProfileView: View {
    @EnvironmentObject var authenticationManager: AuthenticationManager
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Profile")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Button("Sign Out") {
                    authenticationManager.logout()
                }
                .buttonStyle(.bordered)
                
                Spacer()
            }
            .padding()
            .navigationTitle("Profile")
        }
    }
}

struct AllHoldingsView: View {
    let holdings: [Holding]
    
    var body: some View {
        List(holdings) { holding in
            HoldingRowView(holding: holding)
        }
        .navigationTitle("All Holdings")
    }
}

// Mock data models
struct Portfolio {
    let totalValue: Double
    let todayChange: Double
    let totalGainLoss: Double
    let totalReturn: Double
    let holdings: [Holding]
    let recentTransactions: [Transaction]
}

struct Holding: Identifiable {
    let id = UUID()
    let symbol: String
    let name: String
    let quantity: Double
    let value: Double
    let change: Double
}

struct Transaction: Identifiable {
    let id = UUID()
    let symbol: String
    let type: TransactionType
    let amount: Double
    let date: Date
}

enum TransactionType: String {
    case buy = "Buy"
    case sell = "Sell"
}

// Mock managers
class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false
    
    func login(username: String, password: String) async throws {
        // Mock authentication
        try await Task.sleep(nanoseconds: 1_000_000_000)
        isAuthenticated = true
    }
    
    func authenticateWithBiometrics() async throws {
        // Mock biometric authentication
        try await Task.sleep(nanoseconds: 500_000_000)
        isAuthenticated = true
    }
    
    func logout() {
        isAuthenticated = false
    }
}

class PortfolioManager: ObservableObject {
    func loadPortfolio() async {
        // Mock portfolio loading
    }
    
    func getPortfolio() async -> Portfolio? {
        // Mock portfolio data
        return Portfolio(
            totalValue: 125000.50,
            todayChange: 2.34,
            totalGainLoss: 15420.75,
            totalReturn: 14.08,
            holdings: [
                Holding(symbol: "AAPL", name: "Apple Inc.", quantity: 100, value: 17500.00, change: 1.23),
                Holding(symbol: "GOOGL", name: "Alphabet Inc.", quantity: 50, value: 7500.00, change: -0.45),
                Holding(symbol: "MSFT", name: "Microsoft Corp.", quantity: 75, value: 28125.00, change: 2.89)
            ],
            recentTransactions: [
                Transaction(symbol: "AAPL", type: .buy, amount: 500.00, date: Date()),
                Transaction(symbol: "GOOGL", type: .sell, amount: 250.00, date: Date().addingTimeInterval(-86400))
            ]
        )
    }
}

class TradingManager: ObservableObject {
    func initialize() async {
        // Mock initialization
    }
}

class NotificationManager: ObservableObject {
    func requestPermissions() async {
        // Mock permission request
    }
}
