# 💻 Financial Master Desktop

Cross-platform desktop application for Windows, macOS, and Linux.

## Features

- 🖥️ Native desktop experience
- 📊 Advanced charting and analytics
- 🔔 System tray integration
- ⌨️ Global keyboard shortcuts
- 📁 Drag-and-drop file import
- 🖨️ Report generation & printing
- 🌙 Native OS theme support
- 🔐 Secure credential storage

## Tech Stack

- **Framework:** Tauri (Rust + Web frontend)
- **Frontend:** React + TypeScript
- **Size:** ~5MB (vs 150MB+ Electron)
- **Performance:** Native speed
- **Security:** Rust backend

## Supported Platforms

- Windows 10/11
- macOS 11+ (Intel & Apple Silicon)
- Linux (Ubuntu, Fedora, etc.)

## Why Tauri?

| Feature | Electron | Tauri |
|---------|----------|-------|
| Size | ~150MB | ~5MB |
| Memory | High | Low |
| Security | JS backend | Rust backend |
| Speed | Slower | Native |
| Updates | Complex | Simple |

## Quick Start

```bash
cd desktop
npm install
cargo tauri dev      # Development
cargo tauri build    # Production build
```
