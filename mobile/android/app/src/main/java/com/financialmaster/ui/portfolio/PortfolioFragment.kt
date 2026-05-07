package com.financialmaster.ui.portfolio

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.financialmaster.R
import com.financialmaster.databinding.FragmentPortfolioBinding
import com.financialmaster.ui.adapters.HoldingAdapter
import com.financialmaster.ui.adapters.TransactionAdapter
import com.financialmaster.ui.models.Holding
import com.financialmaster.ui.models.Transaction
import com.financialmaster.ui.models.TransactionType
import com.financialmaster.ui.portfolio.viewmodel.PortfolioViewModel
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.data.PieData
import com.github.mikephil.charting.data.PieDataSet
import com.github.mikephil.charting.data.PieEntry
import com.github.mikephil.charting.formatter.PercentFormatter
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.*

@AndroidEntryPoint
class PortfolioFragment : Fragment() {

    private var _binding: FragmentPortfolioBinding? = null
    private val binding get() = _binding!!
    
    private val portfolioViewModel: PortfolioViewModel by viewModels()
    private lateinit var holdingAdapter: HoldingAdapter
    private lateinit var transactionAdapter: TransactionAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPortfolioBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupUI()
        setupObservers()
        setupCharts()
        
        // Load initial data
        portfolioViewModel.loadPortfolioData()
    }
    
    private fun setupUI() {
        // Setup recycler views
        setupRecyclerViews()
        
        // Setup click listeners
        binding.allocationDetailsButton.setOnClickListener {
            // Navigate to allocation details
        }
        
        binding.transactionHistoryButton.setOnClickListener {
            // Navigate to transaction history
        }
        
        binding.refreshButton.setOnClickListener {
            portfolioViewModel.refreshPortfolio()
        }
        
        // Setup timeframe selector
        setupTimeframeSelector()
    }
    
    private fun setupRecyclerViews() {
        // Setup holdings recycler view
        holdingAdapter = HoldingAdapter()
        binding.holdingsRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = holdingAdapter
        }
        
        // Setup transactions recycler view
        transactionAdapter = TransactionAdapter()
        binding.transactionsRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = transactionAdapter
        }
    }
    
    private fun setupTimeframeSelector() {
        binding.timeframeChipGroup.setOnCheckedChangeListener { group, checkedId ->
            val timeframe = when (checkedId) {
                R.id.chip_1d -> PortfolioViewModel.Timeframe.DAY
                R.id.chip_1w -> PortfolioViewModel.Timeframe.WEEK
                R.id.chip_1m -> PortfolioViewModel.Timeframe.MONTH
                R.id.chip_1y -> PortfolioViewModel.Timeframe.YEAR
                R.id.chip_all -> PortfolioViewModel.Timeframe.ALL
                else -> PortfolioViewModel.Timeframe.DAY
            }
            portfolioViewModel.setTimeframe(timeframe)
        }
    }
    
    private fun setupCharts() {
        setupPieChart()
        setupPerformanceChart()
    }
    
    private fun setupPieChart() {
        binding.allocationPieChart.apply {
            description.isEnabled = false
            setUsePercentValues(true)
            setDrawHoleEnabled(true)
            setHoleColor(resources.getColor(R.color.background))
            setTransparentCircleColor(resources.getColor(R.color.background))
            setTransparentCircleRadius(55f)
            setHoleRadius(45f)
            setDrawCenterText(true)
            centerText = "Asset Allocation"
            centerTextSize = 16f
            legend.isEnabled = false
        }
    }
    
    private fun setupPerformanceChart() {
        binding.performanceLineChart.apply {
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
            portfolioViewModel.totalValue.collect { value ->
                binding.totalValueTextView.text = formatCurrency(value)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.dailyChange.collect { change ->
                binding.dailyChangeTextView.text = String.format(
                    "%s%s (%.2f%%)",
                    if (change >= 0) "+" else "",
                    formatCurrency(change),
                    portfolioViewModel.dailyChangePercent.value
                )
                binding.dailyChangeTextView.setTextColor(
                    resources.getColor(
                        if (change >= 0) R.color.positive_green else R.color.negative_red
                    )
                )
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.totalReturn.collect { return_ ->
                binding.totalReturnTextView.text = String.format(
                    "%s%s (%.2f%%)",
                    if (return_ >= 0) "+" else "",
                    formatCurrency(return_),
                    portfolioViewModel.totalReturnPercent.value
                )
                binding.totalReturnTextView.setTextColor(
                    resources.getColor(
                        if (return_ >= 0) R.color.positive_green else R.color.negative_red
                    )
                )
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.assetAllocation.collect { allocation ->
                updatePieChart(allocation)
                updateAllocationLegend(allocation)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.performanceData.collect { data ->
                updatePerformanceChart(data)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.topHoldings.collect { holdings ->
                holdingAdapter.submitList(holdings)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.recentTransactions.collect { transactions ->
                transactionAdapter.submitList(transactions)
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.isLoading.collect { isLoading ->
                binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
                binding.refreshButton.isEnabled = !isLoading
            }
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            portfolioViewModel.errorMessage.collect { error ->
                if (error.isNotEmpty()) {
                    showErrorMessage(error)
                }
            }
        }
    }
    
    private fun updatePieChart(allocation: List<com.financialmaster.ui.models.AssetAllocation>) {
        if (allocation.isEmpty()) return
        
        val entries = allocation.map { asset ->
            PieEntry(asset.percentage.toFloat(), asset.name)
        }
        
        val colors = allocation.map { asset ->
            resources.getColor(getColorForAsset(asset.name))
        }
        
        val dataSet = PieDataSet(entries, "Asset Allocation").apply {
            setColors(colors)
            setDrawValues(false)
            setSliceSpace(3f)
        }
        
        val pieData = PieData(dataSet)
        binding.allocationPieChart.data = pieData
        binding.allocationPieChart.invalidate()
    }
    
    private fun updateAllocationLegend(allocation: List<com.financialmaster.ui.models.AssetAllocation>) {
        // Clear existing legend items
        binding.allocationLegendLinearLayout.removeAllViews()
        
        val inflater = LayoutInflater.from(context)
        
        for (asset in allocation) {
            val legendItem = inflater.inflate(R.layout.item_allocation_legend, binding.allocationLegendLinearLayout, false)
            
            // Set color indicator
            legendItem.findViewById<android.view.View>(R.id.colorIndicator)?.setBackgroundColor(
                resources.getColor(getColorForAsset(asset.name))
            )
            
            // Set asset name
            legendItem.findViewById<android.widget.TextView>(R.id.assetNameTextView)?.text = asset.name
            
            // Set percentage
            legendItem.findViewById<android.widget.TextView>(R.id.percentageTextView)?.text = 
                String.format("%.1f%%", asset.percentage)
            
            // Set value
            legendItem.findViewById<android.widget.TextView>(R.id.valueTextView)?.text = 
                formatCurrency(asset.value)
            
            binding.allocationLegendLinearLayout.addView(legendItem)
        }
    }
    
    private fun updatePerformanceChart(data: List<com.financialmaster.ui.models.PerformanceDataPoint>) {
        if (data.isEmpty()) return
        
        val entries = data.mapIndexed { index, point ->
            com.github.mikephil.charting.data.Entry(index.toFloat(), point.value.toFloat())
        }
        
        val dataSet = com.github.mikephil.charting.data.LineDataSet(entries, "Performance").apply {
            color = if (portfolioViewModel.totalReturn.value >= 0) {
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
        
        val lineData = com.github.mikephil.charting.data.LineData(dataSet)
        binding.performanceLineChart.data = lineData
        binding.performanceLineChart.invalidate()
    }
    
    private fun getColorForAsset(assetName: String): Int {
        return when (assetName.lowercase()) {
            "stocks" -> R.color.blue
            "bonds" -> R.color.green
            "real estate" -> R.color.orange
            "commodities" -> R.color.purple
            "cash" -> R.color.gray
            else -> R.color.primary_blue
        }
    }
    
    private fun formatCurrency(amount: Double): String {
        return NumberFormat.getCurrencyInstance(Locale.US).format(amount)
    }
    
    private fun showErrorMessage(message: String) {
        android.widget.Toast.makeText(requireContext(), message, android.widget.Toast.LENGTH_SHORT).show()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
