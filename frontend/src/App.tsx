import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { DashboardLayout } from './components/Layout/DashboardLayout';
import { PortfolioPage } from './pages/PortfolioPage';
import { TradingPage } from './pages/TradingPage';
import { MarketDataPage } from './pages/MarketDataPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { RiskPage } from './pages/RiskPage';
import { SettingsPage } from './pages/SettingsPage';
import './App.css';

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
        <div className="App">
          <Routes>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<PortfolioPage />} />
              <Route path="portfolio" element={<PortfolioPage />} />
              <Route path="trading" element={<TradingPage />} />
              <Route path="market" element={<MarketDataPage />} />
              <Route path="analysis" element={<AnalysisPage />} />
              <Route path="risk" element={<RiskPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Routes>
          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
