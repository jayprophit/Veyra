#!/bin/bash
# Master Setup Script - Run Everything
echo "FINANCIAL MASTER - COMPLETE ZERO-COST SETUP"
echo "============================================="

echo ""
echo "SETUP OVERVIEW"
echo "================"
echo "This script will guide you through the complete setup:"
echo "   1. Account creation (free services)"
echo "   2. Local development environment"
echo "   3. GitHub repository setup"
echo "   4. Cloud services configuration"
echo "   5. Deployment and verification"
echo "   6. Update workflow training"

echo ""
echo "ESTIMATED TIME: 30-45 minutes"
echo "TOTAL COST: $0 (free tiers)"
echo "CAPACITY: 100+ users"

read -p "Press Enter to begin setup..."

# Run each setup script
echo ""
echo "STARTING SETUP..."
echo "=================="

# Account setup
echo ""
echo "STEP 1: ACCOUNT SETUP"
echo "======================"
~/veyra/setup-scripts/account-setup.sh

# Local setup
echo ""
echo "STEP 2: LOCAL DEVELOPMENT SETUP"
echo "================================="
~/veyra/setup-scripts/local-setup.sh

# GitHub setup
echo ""
echo "STEP 3: GITHUB SETUP"
echo "======================"
~/veyra/setup-scripts/github-setup.sh

# Cloud setup
echo ""
echo "STEP 4: CLOUD SERVICES SETUP"
echo "=============================="
~/veyra/setup-scripts/cloud-setup.sh

# Deployment
echo ""
echo "STEP 5: DEPLOYMENT"
echo "=================="
~/veyra/setup-scripts/deployment.sh

# Verification
echo ""
echo "STEP 6: VERIFICATION"
echo "===================="
~/veyra/setup-scripts/verification.sh

# Update workflow
echo ""
echo "STEP 7: UPDATE WORKFLOW"
echo "========================"
~/veyra/setup-scripts/update-workflow.sh

echo ""
echo "SETUP COMPLETE!"
echo "================="
echo ""
echo "Your Veyra is fully deployed:"
echo "   Frontend: https://veyra.pages.dev"
echo "   Backend: https://veyra-api.onrender.com"
echo "   API Gateway: https://veyra-api.workers.dev"
echo ""
echo "Project directory: ~/veyra"
echo "Setup scripts: ~/veyra/setup-scripts/"
echo ""
echo "Development workflow:"
echo "   1. Edit code in WindSurf"
echo "   2. Push to GitHub: git push origin main"
echo "   3. Auto-deploy to cloud services"
echo "   4. Test on all devices"
echo ""
echo "Congratulations! Your zero-cost multi-cloud financial platform is ready!"
