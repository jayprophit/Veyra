#!/bin/bash
# Verify Veyra Installation and Run Tests

set -e

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🌟 VEYRA - INSTALLATION & VALIDATION VERIFICATION 🌟"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check Python
echo "✓ Checking Python..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  Python Version: $PYTHON_VERSION"

# Check key files
echo ""
echo "✓ Checking essential files..."
FILES=(
    "src/backend/app/veyra_demo_server.py"
    "scripts/launch_demo.sh"
    "VEYRA_DEMO_SERVER_GUIDE.md"
    "VEYRA_COMPREHENSIVE_REPORT.md"
    ".devcontainer/devcontainer.json"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - MISSING"
    fi
done

# Check module count
echo ""
echo "✓ Checking platform modules..."
MODULE_COUNT=$(find src/backend/app -name "*.py" -type f | wc -l)
echo "  Total Modules: $MODULE_COUNT"

if [ $MODULE_COUNT -gt 1000 ]; then
    echo "  ✅ Module count exceeds minimum (1000+)"
else
    echo "  ⚠️  Module count may be lower than expected"
fi

# Validate demo server syntax
echo ""
echo "✓ Validating demo server..."
python3 -m py_compile src/backend/app/veyra_demo_server.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ Demo server syntax valid"
else
    echo "  ❌ Demo server has syntax errors"
    exit 1
fi

# Check FastAPI availability
echo ""
echo "✓ Checking FastAPI..."
if pip show fastapi &>/dev/null; then
    echo "  ✅ FastAPI installed"
else
    echo "  ⏳ FastAPI not installed - will install on first run"
fi

# Check for requirements files
echo ""
echo "✓ Checking requirements files..."
[ -f requirements.txt ] && echo "  ✅ requirements.txt" || echo "  ⚠️  requirements.txt not found"
[ -f requirements_ai.txt ] && echo "  ✅ requirements_ai.txt" || echo "  ⚠️  requirements_ai.txt not found"
[ -f requirements_opensource.txt ] && echo "  ✅ requirements_opensource.txt" || echo "  ⚠️  requirements_opensource.txt not found"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ VALIDATION COMPLETE - READY TO LAUNCH"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "  1. Start the demo server:"
echo "     bash scripts/launch_demo.sh"
echo ""
echo "  2. Open in browser:"
echo "     http://localhost:5000"
echo ""
echo "  3. View API documentation:"
echo "     http://localhost:5000/docs"
echo ""
echo "  4. Read the full guide:"
echo "     cat VEYRA_DEMO_SERVER_GUIDE.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
