//
//  PortfolioView.swift
//  Veyra
//
//  Created by Veyra Team on 2024.
//  Copyright © 2024 Veyra. All rights reserved.
//

import SwiftUI
import Charts
import Combine

struct PortfolioView: View {
    @StateObject private var portfolioViewModel = PortfolioViewModel()
    @State private var selectedTimeframe: Timeframe = .day
    @State private var showingAllocationDetails = false
    @State private var showingTransactionHistory = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Portfolio Summary
                    portfolioSummarySection
                    
                    // Performance Chart
                    performanceChartSection
                    
                    // Asset Allocation
                    assetAllocationSection
                    
                    // Top Holdings
                    topHoldingsSection
                    
                    // Recent Activity
                    recentActivitySection
                }
                .padding()
            }
            .navigationTitle("Portfolio")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button(action: { showingAllocationDetails = true }) {
                            Label("Allocation Details", systemImage: "piechart")
                        }
                        Button(action: { showingTransactionHistory = true }) {
                            Label("Transaction History", systemImage: "list.bullet")
                        }
                        Button(action: { portfolioViewModel.refreshPortfolio() }) {
                            Label("Refresh", systemImage: "arrow.clockwise")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(isPresented: $showingAllocationDetails) {
                AllocationDetailView(portfolioData: portfolioViewModel.portfolioData)
            }
            .sheet(isPresented: $showingTransactionHistory) {
                TransactionHistoryView(transactions: portfolioViewModel.recentTransactions)
            }
        }
    }
    
    private var portfolioSummarySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Portfolio Summary")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 12) {
                // Total Value
                HStack {
                    Text("Total Value")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("$\(portfolioViewModel.totalValue, specifier: "%.2f")")
                        .font(.title2)
                        .fontWeight(.bold)
                }
                
                // Today's Change
                HStack {
                    Text("Today's Change")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Spacer()
                    HStack {
                        Image(systemName: portfolioViewModel.dailyChange >= 0 ? "arrow.up" : "arrow.down")
                            .foregroundColor(portfolioViewModel.dailyChange >= 0 ? .green : .red)
                        Text("\(portfolioViewModel.dailyChange >= 0 ? "+" : "")$\(portfolioViewModel.dailyChange, specifier: "%.2f")")
                            .foregroundColor(portfolioViewModel.dailyChange >= 0 ? .green : .red)
                        Text("(\(portfolioViewModel.dailyChangePercent, specifier: "%.2f")%)")
                            .foregroundColor(portfolioViewModel.dailyChange >= 0 ? .green : .red)
                    }
                    .font(.subheadline)
                    .fontWeight(.medium)
                }
                
                // Total Return
                HStack {
                    Text("Total Return")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Spacer()
                    HStack {
                        Image(systemName: portfolioViewModel.totalReturn >= 0 ? "arrow.up" : "arrow.down")
                            .foregroundColor(portfolioViewModel.totalReturn >= 0 ? .green : .red)
                        Text("\(portfolioViewModel.totalReturn >= 0 ? "+" : "")$\(portfolioViewModel.totalReturn, specifier: "%.2f")")
                            .foregroundColor(portfolioViewModel.totalReturn >= 0 ? .green : .red)
                        Text("(\(portfolioViewModel.totalReturnPercent, specifier: "%.2f")%)")
                            .foregroundColor(portfolioViewModel.totalReturn >= 0 ? .green : .red)
                    }
                    .font(.subheadline)
                    .fontWeight(.medium)
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var performanceChartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Performance")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                // Timeframe Selector
                HStack(spacing: 0) {
                    ForEach(Timeframe.allCases, id: \.self) { timeframe in
                        Button(action: { selectedTimeframe = timeframe }) {
                            Text(timeframe.shortName)
                                .font(.caption)
                                .fontWeight(.medium)
                                .foregroundColor(selectedTimeframe == timeframe ? .white : .blue)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                        }
                        .background(selectedTimeframe == timeframe ? .blue : Color(.systemGray5))
                        .cornerRadius(6)
                    }
                }
            }
            
            if !portfolioViewModel.performanceData.isEmpty {
                Chart(portfolioViewModel.performanceData) { dataPoint in
                    LineMark(
                        x: .value("Date", dataPoint.date),
                        y: .value("Value", dataPoint.value)
                    )
                    .foregroundStyle(portfolioViewModel.totalReturn >= 0 ? .green : .red)
                    .symbol(Circle().strokeBorder(lineWidth: 2))
                    
                    AreaMark(
                        x: .value("Date", dataPoint.date),
                        y: .value("Value", dataPoint.value)
                    )
                    .foregroundStyle(
                        LinearGradient(
                            colors: [
                                (portfolioViewModel.totalReturn >= 0 ? .green : .red).opacity(0.3),
                                (portfolioViewModel.totalReturn >= 0 ? .green : .red).opacity(0.1)
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                }
                .frame(height: 200)
                .chartXAxis {
                    AxisMarks(values: .stride(by: .day, count: selectedTimeframe.axisCount)) { value in
                        AxisGridLine()
                        AxisValueLabel {
                            Text(value.as(Date.self)?.formatted(.dateTime.weekday(.abbreviated)) ?? "")
                        }
                    }
                }
                .chartYAxis {
                    AxisMarks { value in
                        AxisGridLine()
                        AxisValueLabel {
                            Text("$\(value.as(Double.self) ?? 0, specifier: "%.0f")")
                        }
                    }
                }
            } else {
                Rectangle()
                    .fill(Color(.systemGray5))
                    .frame(height: 200)
                    .overlay(
                        Text("Loading performance data...")
                            .foregroundColor(.secondary)
                    )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var assetAllocationSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Asset Allocation")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button(action: { showingAllocationDetails = true }) {
                    Text("Details")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            
            if !portfolioViewModel.assetAllocation.isEmpty {
                // Pie Chart
                Chart(portfolioViewModel.assetAllocation) { allocation in
                    SectorMark(
                        angle: .value("Value", allocation.value),
                        innerRadius: .ratio(0.5),
                        angularInset: 2
                    )
                    .foregroundStyle(allocation.color)
                    .opacity(0.8)
                }
                .frame(height: 200)
                
                // Legend
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 8) {
                    ForEach(portfolioViewModel.assetAllocation, id: \.name) { allocation in
                        HStack(spacing: 8) {
                            Circle()
                                .fill(allocation.color)
                                .frame(width: 12, height: 12)
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text(allocation.name)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                
                                Text("\(allocation.percentage, specifier: "%.1f")%")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            Text("$\(allocation.value, specifier: "%.0f")")
                                .font(.caption)
                                .fontWeight(.medium)
                        }
                    }
                }
            } else {
                Rectangle()
                    .fill(Color(.systemGray5))
                    .frame(height: 200)
                    .overlay(
                        Text("Loading allocation data...")
                            .foregroundColor(.secondary)
                    )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var topHoldingsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Top Holdings")
                .font(.headline)
                .fontWeight(.semibold)
            
            ForEach(portfolioViewModel.topHoldings.prefix(5), id: \.symbol) { holding in
                HoldingRow(holding: holding)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Recent Activity")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button(action: { showingTransactionHistory = true }) {
                    Text("View All")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            
            ForEach(portfolioViewModel.recentTransactions.prefix(3), id: \.id) { transaction in
                TransactionRow(transaction: transaction)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct HoldingRow: View {
    let holding: Holding
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(holding.symbol)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(holding.name)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("\(holding.quantity, specifier: "%.2f") shares")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("$\(holding.value, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                HStack {
                    Image(systemName: holding.change >= 0 ? "arrow.up" : "arrow.down")
                        .font(.caption2)
                        .foregroundColor(holding.change >= 0 ? .green : .red)
                    Text("\(holding.changePercent, specifier: "%.2f")%")
                        .font(.caption)
                        .foregroundColor(holding.change >= 0 ? .green : .red)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct TransactionRow: View {
    let transaction: Transaction
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.type.rawValue)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(transaction.symbol)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("\(transaction.quantity, specifier: "%.2f") @ $\(transaction.price, specifier: "%.2f")")
                    .font(.caption)
                
                Text(transaction.date.formatted(.dateTime.month().day().year()))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(transaction.total, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(transaction.type == .buy ? .green : .red)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Supporting Types

enum Timeframe: String, CaseIterable {
    case day = "1D"
    case week = "1W"
    case month = "1M"
    case year = "1Y"
    case all = "ALL"
    
    var shortName: String {
        switch self {
        case .day: return "1D"
        case .week: return "1W"
        case .month: return "1M"
        case .year: return "1Y"
        case .all: return "ALL"
        }
    }
    
    var axisCount: Int {
        switch self {
        case .day: return 8
        case .week: return 7
        case .month: return 4
        case .year: return 12
        case .all: return 6
        }
    }
}

struct AssetAllocation: Identifiable {
    let id = UUID()
    let name: String
    let value: Double
    let percentage: Double
    let color: Color
}

struct Holding: Identifiable {
    let id = UUID()
    let symbol: String
    let name: String
    let quantity: Double
    let value: Double
    let change: Double
    let changePercent: Double
}

struct Transaction: Identifiable {
    let id = UUID()
    let type: TransactionType
    let symbol: String
    let quantity: Double
    let price: Double
    let total: Double
    let date: Date
}

enum TransactionType: String {
    case buy = "Buy"
    case sell = "Sell"
    case dividend = "Dividend"
    case deposit = "Deposit"
    case withdrawal = "Withdrawal"
}

struct PerformanceDataPoint: Identifiable {
    let id = UUID()
    let date: Date
    let value: Double
}

// MARK: - ViewModel

@MainActor
class PortfolioViewModel: ObservableObject {
    @Published var totalValue: Double = 125_750.00
    @Published var dailyChange: Double = 1_250.00
    @Published var dailyChangePercent: Double = 1.00
    @Published var totalReturn: Double = 15_750.00
    @Published var totalReturnPercent: Double = 14.33
    @Published var performanceData: [PerformanceDataPoint] = []
    @Published var assetAllocation: [AssetAllocation] = []
    @Published var topHoldings: [Holding] = []
    @Published var recentTransactions: [Transaction] = []
    @Published var portfolioData: PortfolioData = PortfolioData()
    
    init() {
        generateMockData()
    }
    
    func refreshPortfolio() {
        // Simulate refresh
        totalValue += Double.random(in: -1000...1000)
        dailyChange = Double.random(in: -500...500)
        dailyChangePercent = (dailyChange / totalValue) * 100
        
        generateMockData()
    }
    
    private func generateMockData() {
        generatePerformanceData()
        generateAssetAllocation()
        generateTopHoldings()
        generateRecentTransactions()
        generatePortfolioData()
    }
    
    private func generatePerformanceData() {
        let now = Date()
        performanceData = (0..<365).map { i in
            let date = now.addingTimeInterval(TimeInterval(-365 + i) * 86400)
            let baseValue = 110_000
            let growth = Double(i) * 15.0
            let variation = Double.random(in: -2000...2000)
            return PerformanceDataPoint(date: date, value: baseValue + growth + variation)
        }
    }
    
    private func generateAssetAllocation() {
        assetAllocation = [
            AssetAllocation(name: "Stocks", value: 75_000, percentage: 59.6, color: .blue),
            AssetAllocation(name: "Bonds", value: 25_000, percentage: 19.9, color: .green),
            AssetAllocation(name: "Real Estate", value: 15_000, percentage: 11.9, color: .orange),
            AssetAllocation(name: "Commodities", value: 7_500, percentage: 6.0, color: .purple),
            AssetAllocation(name: "Cash", value: 3_250, percentage: 2.6, color: .gray)
        ]
    }
    
    private func generateTopHoldings() {
        topHoldings = [
            Holding(symbol: "AAPL", name: "Apple Inc.", quantity: 150, value: 22_500, change: 125.00, changePercent: 0.56),
            Holding(symbol: "GOOGL", name: "Alphabet Inc.", quantity: 50, value: 12_500, change: -250.00, changePercent: -1.96),
            Holding(symbol: "MSFT", name: "Microsoft Corp.", quantity: 80, value: 24_000, change: 400.00, changePercent: 1.67),
            Holding(symbol: "AMZN", name: "Amazon.com Inc.", quantity: 100, value: 14_000, change: 200.00, changePercent: 1.43),
            Holding(symbol: "TSLA", name: "Tesla Inc.", quantity: 75, value: 18_750, change: -375.00, changePercent: -1.96)
        ]
    }
    
    private func generateRecentTransactions() {
        recentTransactions = [
            Transaction(type: .buy, symbol: "AAPL", quantity: 10, price: 150.00, total: 1500.00, date: Date().addingTimeInterval(-86400)),
            Transaction(type: .sell, symbol: "GOOGL", quantity: 5, price: 2500.00, total: 12500.00, date: Date().addingTimeInterval(-172800)),
            Transaction(type: .dividend, symbol: "MSFT", quantity: 0, price: 0.68, total: 54.40, date: Date().addingTimeInterval(-259200)),
            Transaction(type: .buy, symbol: "AMZN", quantity: 20, price: 140.00, total: 2800.00, date: Date().addingTimeInterval(-345600)),
            Transaction(type: .deposit, symbol: "CASH", quantity: 0, price: 0.00, total: 5000.00, date: Date().addingTimeInterval(-432000))
        ]
    }
    
    private func generatePortfolioData() {
        portfolioData = PortfolioData(
            totalValue: totalValue,
            cashBalance: 3_250,
            investedAmount: 110_000,
            totalReturn: totalReturn,
            totalReturnPercent: totalReturnPercent,
            dailyChange: dailyChange,
            dailyChangePercent: dailyChangePercent,
            assetAllocation: assetAllocation,
            holdings: topHoldings,
            transactions: recentTransactions
        )
    }
}

struct PortfolioData {
    let totalValue: Double
    let cashBalance: Double
    let investedAmount: Double
    let totalReturn: Double
    let totalReturnPercent: Double
    let dailyChange: Double
    let dailyChangePercent: Double
    let assetAllocation: [AssetAllocation]
    let holdings: [Holding]
    let transactions: [Transaction]
}

// MARK: - Supporting Views

struct AllocationDetailView: View {
    let portfolioData: PortfolioData
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    ForEach(portfolioData.assetAllocation, id: \.name) { allocation in
                        AllocationDetailRow(allocation: allocation)
                    }
                }
                .padding()
            }
            .navigationTitle("Asset Allocation")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
        }
    }
}

struct AllocationDetailRow: View {
    let allocation: AssetAllocation
    
    var body: some View {
        HStack {
            Circle()
                .fill(allocation.color)
                .frame(width: 16, height: 16)
            
            Text(allocation.name)
                .font(.subheadline)
                .fontWeight(.medium)
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(allocation.value, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text("\(allocation.percentage, specifier: "%.1f")%")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
}

struct TransactionHistoryView: View {
    let transactions: [Transaction]
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            List(transactions, id: \.id) { transaction in
                TransactionRow(transaction: transaction)
            }
            .navigationTitle("Transaction History")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    PortfolioView()
}
