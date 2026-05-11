//
//  TradingView.swift
//  Veyra
//
//  Created by Veyra Team on 2024.
//  Copyright © 2024 Veyra. All rights reserved.
//

import SwiftUI
import Charts
import Combine

struct TradingView: View {
    @StateObject private var tradingViewModel = TradingViewModel()
    @State private var selectedSymbol: String = "AAPL"
    @State private var orderType: OrderType = .market
    @State private var orderSide: OrderSide = .buy
    @State private var quantity: String = ""
    @State private var price: String = ""
    @State private var showingOrderConfirmation = false
    @State private var showingAdvancedOrders = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Symbol Selector and Market Data
                    marketDataSection
                    
                    // Chart Section
                    chartSection
                    
                    // Order Entry Section
                    orderEntrySection
                    
                    // Advanced Orders
                    advancedOrdersSection
                    
                    // Recent Orders
                    recentOrdersSection
                }
                .padding()
            }
            .navigationTitle("Trading")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        tradingViewModel.refreshData()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                tradingViewModel.loadMarketData(symbol: selectedSymbol)
            }
            .sheet(isPresented: $showingOrderConfirmation) {
                OrderConfirmationView(
                    order: tradingViewModel.pendingOrder,
                    onConfirm: {
                        tradingViewModel.executeOrder()
                        showingOrderConfirmation = false
                    },
                    onCancel: {
                        showingOrderConfirmation = false
                    }
                )
            }
            .sheet(isPresented: $showingAdvancedOrders) {
                AdvancedOrdersView(
                    symbol: selectedSymbol,
                    onOrderCreated: { order in
                        tradingViewModel.executeAdvancedOrder(order)
                        showingAdvancedOrders = false
                    }
                )
            }
        }
    }
    
    private var marketDataSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Symbol Selector
            HStack {
                Menu {
                    ForEach(tradingViewModel.availableSymbols, id: \.self) { symbol in
                        Button(symbol) {
                            selectedSymbol = symbol
                            tradingViewModel.loadMarketData(symbol: symbol)
                        }
                    }
                } label: {
                    HStack {
                        Text(selectedSymbol)
                            .font(.title2)
                            .fontWeight(.bold)
                        Image(systemName: "chevron.down")
                            .font(.caption)
                    }
                    .foregroundColor(.primary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("\(tradingViewModel.currentPrice, specifier: "%.2f")")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(tradingViewModel.priceChange >= 0 ? .green : .red)
                    
                    Text("\(tradingViewModel.priceChange >= 0 ? "+" : "")\(tradingViewModel.priceChange, specifier: "%.2f") (\(tradingViewModel.priceChangePercent, specifier: "%.2f")%)")
                        .font(.caption)
                        .foregroundColor(tradingViewModel.priceChange >= 0 ? .green : .red)
                }
            }
            
            // Market Stats
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 8) {
                MarketStatCard(title: "Open", value: "\(tradingViewModel.openPrice, specifier: "%.2f")")
                MarketStatCard(title: "High", value: "\(tradingViewModel.highPrice, specifier: "%.2f")")
                MarketStatCard(title: "Low", value: "\(tradingViewModel.lowPrice, specifier: "%.2f")")
                MarketStatCard(title: "Volume", value: formatVolume(tradingViewModel.volume))
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var chartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Price Chart")
                .font(.headline)
                .fontWeight(.semibold)
            
            if !tradingViewModel.priceData.isEmpty {
                Chart(tradingViewModel.priceData) { dataPoint in
                    LineMark(
                        x: .value("Time", dataPoint.timestamp),
                        y: .value("Price", dataPoint.price)
                    )
                    .foregroundStyle(tradingViewModel.priceChange >= 0 ? .green : .blue)
                    .symbol(Circle().strokeBorder(lineWidth: 2))
                }
                .frame(height: 200)
                .chartXAxis {
                    AxisMarks(values: .stride(by: .hour, count: 6)) { value in
                        AxisGridLine()
                        AxisValueLabel {
                            Text(value.hour, format: .dateTime.hour(.defaultDigits()))
                        }
                    }
                }
                .chartYAxis {
                    AxisMarks { value in
                        AxisGridLine()
                        AxisValueLabel {
                            Text(value.as(Double.self ?? 0, specifier: "%.2f"))
                        }
                    }
                }
            } else {
                Rectangle()
                    .fill(Color(.systemGray5))
                    .frame(height: 200)
                    .overlay(
                        Text("Loading chart data...")
                            .foregroundColor(.secondary)
                    )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var orderEntrySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Place Order")
                .font(.headline)
                .fontWeight(.semibold)
            
            // Order Type and Side
            HStack {
                // Order Type
                Menu {
                    ForEach(OrderType.allCases, id: \.self) { type in
                        Button(type.rawValue) {
                            orderType = type
                        }
                    }
                } label: {
                    HStack {
                        Text(orderType.rawValue)
                        Image(systemName: "chevron.down")
                    }
                    .padding()
                    .background(Color(.systemGray5))
                    .cornerRadius(8)
                }
                
                Spacer()
                
                // Order Side
                HStack(spacing: 0) {
                    Button(action: { orderSide = .buy }) {
                        Text("BUY")
                            .fontWeight(.medium)
                            .foregroundColor(orderSide == .buy ? .white : .green)
                            .frame(maxWidth: .infinity)
                    }
                    .background(orderSide == .buy ? .green : Color(.systemGray5))
                    .cornerRadius(8, corners: [.topLeft, .bottomLeft])
                    
                    Button(action: { orderSide = .sell }) {
                        Text("SELL")
                            .fontWeight(.medium)
                            .foregroundColor(orderSide == .sell ? .white : .red)
                            .frame(maxWidth: .infinity)
                    }
                    .background(orderSide == .sell ? .red : Color(.systemGray5))
                    .cornerRadius(8, corners: [.topRight, .bottomRight])
                }
            }
            
            // Quantity and Price
            VStack(spacing: 12) {
                HStack {
                    Text("Quantity")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Spacer()
                    TextField("0", text: $quantity)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .frame(width: 120)
                }
                
                if orderType == .limit {
                    HStack {
                        Text("Price")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Spacer()
                        TextField("0.00", text: $price)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .frame(width: 120)
                    }
                }
            }
            
            // Order Summary
            if !quantity.isEmpty {
                let qty = Double(quantity) ?? 0
                let orderPrice = orderType == .market ? tradingViewModel.currentPrice : (Double(price) ?? 0)
                let totalValue = qty * orderPrice
                
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Estimated Total")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Spacer()
                        Text("$\(totalValue, specifier: "%.2f")")
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                    
                    if orderType == .limit {
                        HStack {
                            Text("Order Type")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            Spacer()
                            Text(orderType.rawValue.uppercased())
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                    }
                }
                .padding()
                .background(Color(.systemGray5))
                .cornerRadius(8)
            }
            
            // Action Buttons
            HStack(spacing: 12) {
                Button(action: {
                    createOrder()
                }) {
                    Text("Place Order")
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                }
                .background(orderSide == .buy ? .green : .red)
                .cornerRadius(8)
                .disabled(quantity.isEmpty || (orderType == .limit && price.isEmpty))
                
                Button(action: {
                    showingAdvancedOrders = true
                }) {
                    Text("Advanced")
                        .fontWeight(.medium)
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity)
                }
                .background(Color(.systemGray5))
                .cornerRadius(8)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var advancedOrdersSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Advanced Orders")
                .font(.headline)
                .fontWeight(.semibold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                AdvancedOrderCard(
                    title: "Iceberg",
                    description: "Hidden large orders",
                    icon: "icloud"
                )
                AdvancedOrderCard(
                    title: "TWAP",
                    description: "Time-weighted avg price",
                    icon: "clock"
                )
                AdvancedOrderCard(
                    title: "VWAP",
                    description: "Volume-weighted avg price",
                    icon: "chart.bar"
                )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var recentOrdersSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Orders")
                .font(.headline)
                .fontWeight(.semibold)
            
            ForEach(tradingViewModel.recentOrders.prefix(5), id: \.id) { order in
                OrderRow(order: order)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private func createOrder() {
        guard let qty = Double(quantity), qty > 0 else { return }
        
        let orderPrice: Double
        if orderType == .market {
            orderPrice = tradingViewModel.currentPrice
        } else {
            guard let priceValue = Double(price), priceValue > 0 else { return }
            orderPrice = priceValue
        }
        
        let order = Order(
            symbol: selectedSymbol,
            side: orderSide,
            type: orderType,
            quantity: qty,
            price: orderPrice,
            timestamp: Date()
        )
        
        tradingViewModel.pendingOrder = order
        showingOrderConfirmation = true
    }
    
    private func formatVolume(_ volume: Double) -> String {
        if volume >= 1_000_000 {
            return String(format: "%.1fM", volume / 1_000_000)
        } else if volume >= 1_000 {
            return String(format: "%.1fK", volume / 1_000)
        } else {
            return String(format: "%.0f", volume)
        }
    }
}

struct MarketStatCard: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(8)
        .background(Color(.systemBackground))
        .cornerRadius(6)
    }
}

struct AdvancedOrderCard: View {
    let title: String
    let description: String
    let icon: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
            
            Text(title)
                .font(.subheadline)
                .fontWeight(.medium)
            
            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
    }
}

struct OrderRow: View {
    let order: Order
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(order.symbol)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(order.side.rawValue.uppercased())
                    .font(.caption)
                    .foregroundColor(order.side == .buy ? .green : .red)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("\(order.quantity, specifier: "%.2f") @ $\(order.price, specifier: "%.2f")")
                    .font(.subheadline)
                
                Text(order.type.rawValue.uppercased())
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(order.quantity * order.price, specifier: "%.2f")")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(order.status.rawValue.uppercased())
                    .font(.caption)
                    .foregroundColor(statusColor)
            }
        }
        .padding(.vertical, 8)
    }
    
    private var statusColor: Color {
        switch order.status {
        case .filled:
            return .green
        case .pending:
            return .orange
        case .cancelled:
            return .red
        case .rejected:
            return .red
        }
    }
}

// MARK: - Supporting Types

enum OrderType: String, CaseIterable {
    case market = "Market"
    case limit = "Limit"
    case stop = "Stop"
    case stopLimit = "Stop Limit"
}

enum OrderSide: String {
    case buy = "Buy"
    case sell = "Sell"
}

enum OrderStatus: String {
    case pending = "Pending"
    case filled = "Filled"
    case cancelled = "Cancelled"
    case rejected = "Rejected"
}

struct Order: Identifiable {
    let id = UUID()
    let symbol: String
    let side: OrderSide
    let type: OrderType
    let quantity: Double
    let price: Double
    let timestamp: Date
    var status: OrderStatus = .pending
}

struct PriceDataPoint: Identifiable {
    let id = UUID()
    let timestamp: Date
    let price: Double
}

// MARK: - ViewModel

@MainActor
class TradingViewModel: ObservableObject {
    @Published var currentPrice: Double = 150.00
    @Published var priceChange: Double = 2.50
    @Published var priceChangePercent: Double = 1.67
    @Published var openPrice: Double = 147.50
    @Published var highPrice: Double = 152.00
    @Published var lowPrice: Double = 146.00
    @Published var volume: Double = 45_678_900
    @Published var priceData: [PriceDataPoint] = []
    @Published var recentOrders: [Order] = []
    @Published var pendingOrder: Order?
    
    let availableSymbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "BTC", "ETH"]
    
    func loadMarketData(symbol: String) {
        // Simulate loading market data
        generateMockPriceData()
        generateMockOrders()
    }
    
    func refreshData() {
        // Simulate refresh
        priceChange = Double.random(in: -5...5)
        currentPrice += priceChange
        priceChangePercent = (priceChange / currentPrice) * 100
        
        generateMockPriceData()
    }
    
    func executeOrder() {
        guard let order = pendingOrder else { return }
        
        // Simulate order execution
        var executedOrder = order
        executedOrder.status = .filled
        
        recentOrders.insert(executedOrder, at: 0)
        pendingOrder = nil
    }
    
    func executeAdvancedOrder(_ order: Order) {
        // Simulate advanced order execution
        var executedOrder = order
        executedOrder.status = .filled
        
        recentOrders.insert(executedOrder, at: 0)
    }
    
    private func generateMockPriceData() {
        let now = Date()
        priceData = (0..<100).map { i in
            let timestamp = now.addingTimeInterval(TimeInterval(-100 + i) * 300) // 5-minute intervals
            let basePrice = currentPrice
            let variation = Double.random(in: -2...2)
            return PriceDataPoint(timestamp: timestamp, price: basePrice + variation)
        }
    }
    
    private func generateMockOrders() {
        recentOrders = [
            Order(symbol: "AAPL", side: .buy, type: .market, quantity: 100, price: 149.50, timestamp: Date().addingTimeInterval(-3600)),
            Order(symbol: "GOOGL", side: .sell, type: .limit, quantity: 50, price: 2800.00, timestamp: Date().addingTimeInterval(-7200)),
            Order(symbol: "MSFT", side: .buy, type: .market, quantity: 75, price: 380.25, timestamp: Date().addingTimeInterval(-10800))
        ]
    }
}

// MARK: - Supporting Views

struct OrderConfirmationView: View {
    let order: Order?
    let onConfirm: () -> Void
    let onCancel: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                if let order = order {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Order Confirmation")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Symbol:")
                                Spacer()
                                Text(order.symbol)
                                    .fontWeight(.medium)
                            }
                            
                            HStack {
                                Text("Side:")
                                Spacer()
                                Text(order.side.rawValue.uppercased())
                                    .fontWeight(.medium)
                                    .foregroundColor(order.side == .buy ? .green : .red)
                            }
                            
                            HStack {
                                Text("Type:")
                                Spacer()
                                Text(order.type.rawValue.uppercased())
                                    .fontWeight(.medium)
                            }
                            
                            HStack {
                                Text("Quantity:")
                                Spacer()
                                Text("\(order.quantity, specifier: "%.2f")")
                                    .fontWeight(.medium)
                            }
                            
                            HStack {
                                Text("Price:")
                                Spacer()
                                Text("$\(order.price, specifier: "%.2f")")
                                    .fontWeight(.medium)
                            }
                            
                            HStack {
                                Text("Total:")
                                Spacer()
                                Text("$\(order.quantity * order.price, specifier: "%.2f")")
                                    .fontWeight(.bold)
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                    }
                    
                    Spacer()
                    
                    HStack(spacing: 12) {
                        Button("Cancel", action: onCancel)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color(.systemGray5))
                            .cornerRadius(8)
                        
                        Button("Confirm", action: onConfirm)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(order.side == .buy ? .green : .red)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel", action: onCancel)
                }
            }
        }
    }
}

struct AdvancedOrdersView: View {
    let symbol: String
    let onOrderCreated: (Order) -> Void
    
    var body: some View {
        NavigationView {
            Text("Advanced Orders for \(symbol)")
                .navigationTitle("Advanced Orders")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button("Done") {
                            // Dismiss view
                        }
                    }
                }
        }
    }
}

// MARK: - Extensions

extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}

#Preview {
    TradingView()
}
