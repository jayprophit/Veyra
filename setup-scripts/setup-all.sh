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
~/financial-master/setup-scripts/account-setup.sh

# Local setup
echo ""
echo "STEP 2: LOCAL DEVELOPMENT SETUP"
echo "================================="
~/financial-master/setup-scripts/local-setup.sh

# GitHub setup
echo ""
echo "STEP 3: GITHUB SETUP"
echo "======================"
~/financial-master/setup-scripts/github-setup.sh

# Cloud setup
echo ""
echo "STEP 4: CLOUD SERVICES SETUP"
echo "=============================="
~/financial-master/setup-scripts/cloud-setup.sh

# Deployment
echo ""
echo "STEP 5: DEPLOYMENT"
echo "=================="
~/financial-master/setup-scripts/deployment.sh

# Verification
echo ""
echo "STEP 6: VERIFICATION"
echo "===================="
~/financial-master/setup-scripts/verification.sh

# Update workflow
echo ""
echo "STEP 7: UPDATE WORKFLOW"
echo "========================"
~/financial-master/setup-scripts/update-workflow.sh

echo ""
echo "SETUP COMPLETE!"
echo "================="
echo ""
echo "Your Financial Master is fully deployed:"
echo "   Frontend: https://financial-master.pages.dev"
echo "   Backend: https://financial-master-api.onrender.com"
echo "   API Gateway: https://financial-master-api.workers.dev"
echo ""
echo "Project directory: ~/financial-master"
echo "Setup scripts: ~/financial-master/setup-scripts/"
echo ""
echo "Development workflow:"
echo "   1. Edit code in WindSurf"
echo "   2. Push to GitHub: git push origin main"
echo "   3. Auto-deploy to cloud services"
echo "   4. Test on all devices"
echo ""
echo "Congratulations! Your zero-cost multi-cloud financial platform is ready!"
