package com.veyra.ui.trading

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.veyra.R
import com.veyra.databinding.FragmentTradingBinding
import com.veyra.ui.adapters.OrderAdapter
import com.veyra.ui.adapters.PriceDataAdapter
import com.veyra.ui.models.Order
import com.veyra.ui.models.OrderSide
import com.veyra.ui.models.OrderType
import com.veyra.ui.models.OrderStatus
import com.veyra.ui.models.PriceDataPoint
import com.veyra.ui.trading.viewmodel.TradingViewModel
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class TradingFragment : Fragment() {

    private var _binding: FragmentTradingBinding? = null
    private val binding get() = _binding!!
    
    private val tradingViewModel: TradingViewModel by viewModels()
    private lateinit var orderAdapter: OrderAdapter
    private lateinit var priceDataAdapter: PriceDataAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentTradingBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupUI()
        setupObservers()
        setupChart()
        
        // Load initial data
        tradingViewModel.loadMarketData("AAPL")
    }
    
    private fun setupUI() {
        // Setup symbol spinner
        val symbols = listOf("AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "BTC", "ETH")
        val symbolAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, symbols)
        symbolAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.symbolSpinner.adapter = symbolAdapter
        
        // Setup order type spinner
        val orderTypes = OrderType.values().map { it.displayName }
        val orderTypeAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, orderTypes)
        orderTypeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.orderTypeSpinner.adapter = orderTypeAdapter
        
        // Setup order side buttons
        binding.buyButton.setOnClickListener {
            tradingViewModel.setOrderSide(OrderSide.BUY)
            updateOrderSideUI()
        }
        
        binding.sellButton.setOnClickListener {
            tradingViewModel.setOrderSide(OrderSide.SELL)
            updateOrderSideUI()
        }
        
        // Setup place order button
        binding.placeOrderButton.setOnClickListener {
            placeOrder()
        }
        
        // Setup advanced order button
        binding.advancedOrderButton.setOnClickListener {
            // Navigate to advanced orders
        }
        
        // Setup refresh button
        binding.refreshButton.setOnClickListener {
            tradingViewModel.refreshData()
        }
        
        // Setup recycler views
        setupRecyclerViews()
        
        // Initialize UI state
        updateOrderSideUI()
    }
    
    private fun setupRecyclerViews() {
        // Setup orders recycler view
        orderAdapter = OrderAdapter()
        binding.ordersRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = orderAdapter
        }
        
        // Setup price data recycler view (if needed for additional info)
        priceDataAdapter = PriceDataAdapter()
    }
    
    private fun setupChart() {
        binding.priceChart.apply {
            description.isEnabled = false
            setTouchEnabled(true)
            isDragEnabled = true
            setScaleEnabled(true)
            setDrawGridBackground(false)
            setDrawBorders(false)
            
            xAxis.apply {
                setDrawGridLines(false)
                setDrawAxisLine(false)
                granularity = 1f
                setLabelCount(6)
            }
            
            axisLeft.apply {
                setDrawGridLines(true)
                setDrawAxisLine(false)
                granularity = 1f
                setLabelCount(8)
            }
            
            axisRight.isEnabled = false
            
            legend.isEnabled = false
        }
    }
    
    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.currentPrice.collect { price ->
                binding.currentPriceTextView.text = String.format("%.2f", price)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.priceChange.collect { change ->
                binding.priceChangeTextView.text = String.format(
                    "%s%.2f (%.2f%%)",
                    if (change >= 0) "+" else "",
                    change,
                    tradingViewModel.priceChangePercent.value
                )
                binding.priceChangeTextView.setTextColor(
                    resources.getColor(
                        if (change >= 0) R.color.positive_green else R.color.negative_red
                    )
                )
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.marketStats.collect { stats ->
                binding.openPriceTextView.text = String.format("%.2f", stats.openPrice)
                binding.highPriceTextView.text = String.format("%.2f", stats.highPrice)
                binding.lowPriceTextView.text = String.format("%.2f", stats.lowPrice)
                binding.volumeTextView.text = formatVolume(stats.volume)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.priceData.collect { data ->
                updateChart(data)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.recentOrders.collect { orders ->
                orderAdapter.submitList(orders)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.isLoading.collect { isLoading ->
                binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
                binding.refreshButton.isEnabled = !isLoading
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            tradingViewModel.errorMessage.collect { error ->
                if (error.isNotEmpty()) {
                    // Show error message
                    showErrorMessage(error)
                }
            }
        }
    }
    
    private fun updateChart(data: List<PriceDataPoint>) {
        if (data.isEmpty()) return
        
        val entries = data.mapIndexed { index, point ->
            Entry(index.toFloat(), point.price.toFloat())
        }
        
        val dataSet = LineDataSet(entries, "Price").apply {
            color = if (tradingViewModel.priceChange.value >= 0) {
                resources.getColor(R.color.positive_green)
            } else {
                resources.getColor(R.color.negative_red)
            }
            setDrawValues(false)
            setDrawCircles(true)
            setCircleColor(resources.getColor(R.color.primary_blue))
            setCircleRadius(3f)
            setDrawFilled(false)
            lineWidth = 2f
        }
        
        val lineData = LineData(dataSet as ILineDataSet)
        binding.priceChart.data = lineData
        binding.priceChart.invalidate()
    }
    
    private fun updateOrderSideUI() {
        val isBuy = tradingViewModel.orderSide.value == OrderSide.BUY
        
        binding.buyButton.setBackgroundColor(
            resources.getColor(if (isBuy) R.color.positive_green else R.color.gray_light)
        )
        binding.sellButton.setBackgroundColor(
            resources.getColor(if (!isBuy) R.color.negative_red else R.color.gray_light)
        )
        
        binding.buyButton.setTextColor(
            resources.getColor(if (isBuy) R.color.white else R.color.text_primary)
        )
        binding.sellButton.setTextColor(
            resources.getColor(if (!isBuy) R.color.white else R.color.text_primary)
        )
        
        binding.placeOrderButton.setBackgroundColor(
            resources.getColor(if (isBuy) R.color.positive_green else R.color.negative_red)
        )
    }
    
    private fun placeOrder() {
        val symbol = binding.symbolSpinner.selectedItem?.toString() ?: return
        val orderType = OrderType.values()[binding.orderTypeSpinner.selectedItemPosition]
        val quantityText = binding.quantityEditText.text.toString()
        val priceText = binding.priceEditText.text.toString()
        
        if (quantityText.isEmpty()) {
            showErrorMessage("Please enter quantity")
            return
        }
        
        val quantity = quantityText.toDoubleOrNull()
        if (quantity == null || quantity <= 0) {
            showErrorMessage("Please enter a valid quantity")
            return
        }
        
        val price = if (orderType == OrderType.MARKET) {
            tradingViewModel.currentPrice.value
        } else {
            if (priceText.isEmpty()) {
                showErrorMessage("Please enter price for limit orders")
                return
            }
            priceText.toDoubleOrNull() ?: return
        }
        
        tradingViewModel.placeOrder(
            symbol = symbol,
            type = orderType,
            side = tradingViewModel.orderSide.value,
            quantity = quantity,
            price = price
        )
    }
    
    private fun formatVolume(volume: Double): String {
        return when {
            volume >= 1_000_000 -> String.format("%.1fM", volume / 1_000_000)
            volume >= 1_000 -> String.format("%.1fK", volume / 1_000)
            else -> String.format("%.0f", volume)
        }
    }
    
    private fun showErrorMessage(message: String) {
        // Implement error message display (e.g., Toast or Snackbar)
        android.widget.Toast.makeText(requireContext(), message, android.widget.Toast.LENGTH_SHORT).show()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
