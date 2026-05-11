/**
 * Veyra - Electron Desktop Application
 * 
 * Features:
 * - Cross-platform desktop app (Windows/Mac/Linux)
 * - Native system tray integration
 * - Desktop notifications
 * - Auto-updater
 * - Hardware-accelerated charts
 */

const { app, BrowserWindow, Tray, Menu, ipcMain, Notification, nativeImage } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

// App configuration
const APP_NAME = 'Veyra';
const APP_ICON = path.join(__dirname, 'assets', 'icon.png');
const TRAY_ICON = path.join(__dirname, 'assets', 'tray-icon.png');

// Window management
let mainWindow = null;
let tray = null;
let isQuitting = false;

// Create main application window
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: APP_NAME,
    icon: APP_ICON,
    show: false, // Show when ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      // Enable hardware acceleration for charts
      offscreen: false,
      webSecurity: true
    },
    titleBarStyle: 'default',
    backgroundColor: '#1a1a2e'
  });

  // Load the app
  if (isDev) {
    // Development: Connect to local dev server
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // Production: Load built app
    mainWindow.loadFile(path.join(__dirname, '../frontend/build/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Check for updates
    checkForUpdates();
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!isQuitting && process.platform === 'darwin') {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle new window requests
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Open external links in system browser
    if (url.startsWith('http')) {
      require('electron').shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });
}

// Create system tray
function createTray() {
  const icon = nativeImage.createFromPath(TRAY_ICON);
  tray = new Tray(icon.resize({ width: 16, height: 16 }));

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open Veyra',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createMainWindow();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quick Actions',
      submenu: [
        {
          label: 'New Trade',
          click: () => sendToRenderer('quick-action', 'new-trade')
        },
        {
          label: 'Start Bot',
          click: () => sendToRenderer('quick-action', 'start-bot')
        },
        {
          label: 'Check Portfolio',
          click: () => sendToRenderer('quick-action', 'portfolio')
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Notifications',
      type: 'checkbox',
      checked: true,
      click: (menuItem) => {
        sendToRenderer('toggle-notifications', menuItem.checked);
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip(APP_NAME);
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    } else {
      createMainWindow();
    }
  });

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// Send message to renderer process
function sendToRenderer(channel, data) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, data);
  }
}

// Show desktop notification
function showNotification(title, body, data = {}) {
  if (Notification.isSupported()) {
    const notification = new Notification({
      title: title,
      body: body,
      icon: APP_ICON,
      silent: false,
      urgency: data.urgency || 'normal'
    });

    notification.on('click', () => {
      if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
        // Send data to renderer
        sendToRenderer('notification-clicked', data);
      }
    });

    notification.show();
  }
}

// Check for updates
function checkForUpdates() {
  // Implement auto-updater logic here
  // For now, just log
  console.log('Checking for updates...');
}

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});

ipcMain.handle('minimize-window', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.handle('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.handle('close-window', () => {
  if (mainWindow) {
    if (process.platform === 'darwin') {
      mainWindow.hide();
    } else {
      mainWindow.close();
    }
  }
});

ipcMain.handle('show-notification', (event, { title, body, data }) => {
  showNotification(title, body, data);
});

ipcMain.handle('update-tray-badge', (event, count) => {
  if (tray) {
    // Update tray icon with badge (requires custom implementation)
    tray.setToolTip(`${APP_NAME} - ${count} notifications`);
  }
});

// App event handlers
app.whenReady().then(() => {
  createMainWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    require('electron').shell.openExternal(navigationUrl);
  });
});

// Handle notifications from renderer
ipcMain.on('trading-alert', (event, alert) => {
  showNotification(
    `Trading Alert: ${alert.symbol}`,
    alert.message,
    { type: 'trading', symbol: alert.symbol }
  );
});

ipcMain.on('price-alert', (event, alert) => {
  showNotification(
    `Price Alert: ${alert.symbol}`,
    `${alert.symbol} is now ${alert.condition} ${alert.targetPrice}`,
    { type: 'price', symbol: alert.symbol }
  );
});

ipcMain.on('achievement-unlocked', (event, achievement) => {
  showNotification(
    'Achievement Unlocked! 🎉',
    `${achievement.name}: ${achievement.description}`,
    { type: 'achievement', achievementId: achievement.id }
  );
});

console.log(`${APP_NAME} Desktop App starting...`);
