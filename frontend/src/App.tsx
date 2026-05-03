import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import { DashboardLayout } from './components/Layout/DashboardLayout';
import { AnalysisPage } from './pages/AnalysisPage';
import { DividendTrackerPage } from './pages/DividendTrackerPage';
import { EnhancedSettingsPage } from './pages/EnhancedSettingsPage';
import { MarketDataPage } from './pages/MarketDataPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { RiskPage } from './pages/RiskPage';
import { StrategyBuilderPage } from './pages/StrategyBuilderPage';
import { TaxDashboardPage } from './pages/TaxDashboardPage';
import { TradingPage } from './pages/TradingPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 30000,
      staleTime: 10000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App ds-theme">
          <Routes>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<PortfolioPage />} />
              <Route path="portfolio" element={<PortfolioPage />} />
              <Route path="trading" element={<TradingPage />} />
              <Route path="market" element={<MarketDataPage />} />
              <Route path="market-intelligence" element={<MarketIntelligencePage />} />
              <Route path="analysis" element={<AnalysisPage />} />
              <Route path="risk" element={<RiskPage />} />
              <Route path="settings" element={<EnhancedSettingsPage />} />
              <Route path="strategy-builder" element={<StrategyBuilderPage />} />
              <Route path="dividends" element={<DividendTrackerPage />} />
              <Route path="tax" element={<TaxDashboardPage />} />
            </Route>
          </Routes>
          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
