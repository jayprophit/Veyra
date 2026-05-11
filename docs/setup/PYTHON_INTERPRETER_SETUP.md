# Python Interpreter Setup Guide for Windsurf

## Quick Fix for "Select Python Interpreter" Issue

### Option 1: Automatic Setup (Recommended)

**Windows PowerShell:**
```powershell
.\scripts\setup_python_env.ps1
```

**Windows Command Prompt:**
```cmd
scripts\setup_python_env.bat
```

**macOS/Linux:**
```bash
./scripts/setup_python_env.sh
```

### Option 2: Manual Setup

1. **Open Terminal in Project Root**
   ```bash
   cd "c:\Users\jpowe\Desktop\Veyra"
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate Virtual Environment**
   - **Windows:** `.venv\Scripts\activate`
   - **macOS/Linux:** `source .venv/bin/activate`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy isort
   ```

### Option 3: Windsurf-Specific Fix

1. **Press `Ctrl+Shift+P`** (or `Cmd+Shift+P` on Mac)
2. **Type:** `Python: Select Interpreter`
3. **Choose one of:**
   - `.venv\Scripts\python.exe` (Windows - if exists)
   - `Python 3.11` or higher
   - Any Python 3.9+ installation

4. **If .venv doesn't exist:**
   - Windsurf should auto-create it on first run (configured in `.windsurf/settings.json`)
   - Or run: `python -m venv .venv`

## Configuration Files

### `.windsurf/settings.json`
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src/backend",
        "${workspaceFolder}/src/backend/app"
    ]
}
```

### `.vscode/settings.json`
Same configuration for VS Code compatibility.

## Troubleshooting

### Issue: "Python interpreter not found"
**Solution:**
1. Check Python installation: `python --version`
2. If not found, install Python 3.9+ from [python.org](https://python.org)
3. Ensure Python is added to PATH during installation

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
.venv\Scripts\pip install -r requirements.txt
```

### Issue: "Cannot activate virtual environment"
**Solution (Windows PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Interpreter keeps reverting
**Solution:**
1. Delete `.windsurf/settings.json`
2. Restart Windsurf
3. Run: `Python: Select Interpreter` again
4. Choose the `.venv` Python

## Verify Setup

Run these commands to verify:

```bash
# Check Python version
python --version

# Check virtual environment
python -c "import sys; print(sys.executable)"

# Run tests
python -m pytest tests/

# Start server
python -m src.backend.app.api_server
```

## Alternative: Use Global Python

If you prefer not using virtual environments:

1. **Install dependencies globally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Select global Python in Windsurf:**
   - `Ctrl+Shift+P` → `Python: Select Interpreter`
   - Choose system Python (e.g., `Python 3.11.x`)

**Note:** Not recommended for production development.

## Docker Alternative

If local Python setup fails, use Docker:

```bash
docker-compose up --build
```

This runs the entire stack without local Python setup.

## Support

If issues persist:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Create GitHub Issue with error details
3. Verify Python 3.9+ is installed: `python --version`

