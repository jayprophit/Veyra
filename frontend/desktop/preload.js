/**
 * Veyra - Preload Script
 * 
 * Secure bridge between main and renderer processes.
 * Exposes safe APIs to the frontend.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),

  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),

  // Notifications
  showNotification: (title, body, data) => 
    ipcRenderer.invoke('show-notification', { title, body, data }),

  // Tray
  updateTrayBadge: (count) => ipcRenderer.invoke('update-tray-badge', count),

  // Event listeners
  onQuickAction: (callback) => ipcRenderer.on('quick-action', callback),
  onToggleNotifications: (callback) => ipcRenderer.on('toggle-notifications', callback),
  onNotificationClicked: (callback) => ipcRenderer.on('notification-clicked', callback),

  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),

  // Trading alerts (renderer to main)
  sendTradingAlert: (alert) => ipcRenderer.send('trading-alert', alert),
  sendPriceAlert: (alert) => ipcRenderer.send('price-alert', alert),
  sendAchievement: (achievement) => ipcRenderer.send('achievement-unlocked', achievement),
});

// Notify when preload has loaded
console.log('Veyra - Preload script loaded');
