import React, {useEffect} from 'react';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {appWindow} from '@tauri-apps/api/window';
import {register} from '@tauri-apps/api/globalShortcut';
import {checkUpdate, installUpdate} from '@tauri-apps/api/updater';
import {relaunch} from '@tauri-apps/api/process';
import {Toaster} from 'react-hot-toast';

// Layout
import Layout from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Tax from './pages/Tax';
import Fuel from './pages/Fuel';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

// Store
import {useAppStore} from './store';

// Services
import {initializeAutoSync} from './services/autoSync';
import {initializeSystemTray} from './services/systemTray';

function App() {
  const {theme} = useAppStore();

  useEffect(() => {
    // Initialize services
    initializeSystemTray();
    initializeAutoSync();

    // Register global shortcuts
    const registerShortcuts = async () => {
      // Ctrl/Cmd + Shift + D - Dashboard
      await register('CommandOrControl+Shift+D', () => {
        appWindow.show();
        appWindow.setFocus();
      });

      // Ctrl/Cmd + Shift + S - Sync
      await register('CommandOrControl+Shift+S', () => {
        // Trigger sync
        console.log('Manual sync triggered');
      });
    };

    registerShortcuts();

    // Check for updates
    const checkForUpdates = async () => {
      try {
        const {shouldUpdate, manifest} = await checkUpdate();
        if (shouldUpdate) {
          console.log(`Update available: ${manifest?.version}`);
          await installUpdate();
          await relaunch();
        }
      } catch (error) {
        console.error('Update check failed:', error);
      }
    };

    checkForUpdates();
  }, []);

  return (
    <div className={theme}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/tax" element={<Tax />} />
            <Route path="/fuel" element={<Fuel />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
      <Toaster position="bottom-right" />
    </div>
  );
}

export default App;
