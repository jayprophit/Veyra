# CI/CD Pipeline Failures - Resolution Guide

## Current Issues Detected

### 1. PowerShell Script Path Error
**Error:** `The term '.\scripts\setup_python_env.ps1' is not recognized`

**Cause:** You ran the command from `C:\Windows\System32` instead of the project directory.

**Fix:**
```powershell
# Navigate to project root FIRST
cd "c:\Users\jpowe\Desktop\Financial Master"

# Then run the script
.\scripts\setup_python_env.ps1
```

### 2. GitHub CI Test Failures (Python 3.9-3.12)
**Likely Causes:**
- Missing `__init__.py` files in modules
- Import errors
- Missing test files
- Requirements.txt issues

## Immediate Fixes Required

### Fix 1: Ensure All Modules Have __init__.py
```bash
# Check for missing __init__.py files
find src/backend/app -type d -not -path "*/\.*" -not -path "*/__pycache__*" | while read dir; do
    if [ ! -f "$dir/__init__.py" ]; then
        echo "Missing: $dir/__init__.py"
    fi
done
```

### Fix 2: Create Missing Test Files
```bash
mkdir -p tests/unit
touch tests/__init__.py
touch tests/unit/__init__.py
```

### Fix 3: Update CI Configuration
See `.github/workflows/ci.yml` fixes below.

## Step-by-Step Resolution

### Step 1: Navigate to Correct Directory
```powershell
cd "c:\Users\jpowe\Desktop\Financial Master"
pwd  # Verify you're in the right place
```

### Step 2: Run Setup Script
```powershell
# Option A: PowerShell
.\scripts\setup_python_env.ps1

# Option B: Command Prompt
scripts\setup_python_env.bat
```

### Step 3: Verify Python Environment
```powershell
python --version
.venv\Scripts\python --version
.venv\Scripts\pip list
```

### Step 4: Run Tests Locally
```powershell
# Activate environment
.venv\Scripts\activate

# Run tests
pytest tests/ -v

# Run linting
flake8 src/backend/app
black --check src/backend/app
```

## Common CI Failure Fixes

### Issue: Module Import Errors
**Fix:** Add missing `__init__.py` files:
```bash
touch src/backend/app/{new_module}/__init__.py
```

### Issue: Requirements Not Found
**Fix:** Ensure `requirements.txt` exists in root:
```
numpy>=1.24.0
pandas>=2.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Issue: Lint Failures
**Fix:** Run auto-formatters:
```bash
black src/backend/app
isort src/backend/app
flake8 src/backend/app --max-line-length=100
```

### Issue: Security Scan Failures
**Fix:** Address bandit warnings:
```bash
bandit -r src/backend/app -f json
```

## Quick Fix Commands

```powershell
# Complete reset and setup
cd "c:\Users\jpowe\Desktop\Financial Master"

# Remove old venv (if corrupted)
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue

# Create fresh venv
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install deps
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install pytest pytest-cov black flake8 mypy isort

# Test
pytest tests/ -x -v
```

## GitHub CI Status Check

After local fixes pass, push and check:
```bash
git add .
git commit -m "Fix: Resolve CI/CD pipeline failures"
git push origin main
```

Then monitor at: `https://github.com/jpowell/financial-master/actions`

## Emergency: Skip CI if Blocked

If CI is blocking urgent work:
```bash
git commit -m "Your message [skip ci]"
```

Then fix CI issues in a follow-up PR.

## Support

If issues persist after these fixes:
1. Check GitHub Actions logs for specific error messages
2. Run tests locally with: `pytest tests/ -v --tb=short`
3. Verify Python version: Should be 3.9+
4. Check for syntax errors: `python -m py_compile src/backend/app/**/*.py`

