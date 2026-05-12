import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import './i18n/i18n';
import { DashboardLayout } from './components/Layout/DashboardLayout';
import { AnalysisPage } from './pages/AnalysisPage';
import DividendTrackerPage from './pages/DividendTrackerPage';
import { EnhancedSettingsPage } from './pages/EnhancedSettingsPage';
import { MarketDataPage } from './pages/MarketDataPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { RiskPage } from './pages/RiskPage';
import StrategyBuilderPage from './pages/StrategyBuilderPage';
import { TaxDashboardPage } from './pages/TaxDashboardPage';
import { TradingPage } from './pages/TradingPage';
import { MarketIntelligencePage } from './pages/MarketIntelligencePage';
import ComingSoonPage from './pages/ComingSoonPage';
import NotFoundPage from './pages/NotFoundPage';
import MaintenancePage from './pages/MaintenancePage';
import RedirectPage from './pages/RedirectPage';
import PartnersPage from './pages/PartnersPage';
import AITrainingPage from './pages/AITrainingPage';
import BlockchainPage from './pages/BlockchainPage';
import AlternativeDataPage from './pages/AlternativeDataPage';
import QuantResearchPage from './pages/QuantResearchPage';

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
              <Route path="partners" element={<PartnersPage />} />
              <Route path="ai-training" element={<AITrainingPage />} />
              <Route path="blockchain" element={<BlockchainPage />} />
              <Route path="alternative-data" element={<AlternativeDataPage />} />
              <Route path="quant-research" element={<QuantResearchPage />} />
            </Route>
            {/* Standalone pages */}
            <Route path="/coming-soon" element={<ComingSoonPage />} />
            <Route path="/maintenance" element={<MaintenancePage />} />
            <Route path="/redirect" element={<RedirectPage />} />
            <Route path="/404" element={<NotFoundPage />} />
            {/* Catch all route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
