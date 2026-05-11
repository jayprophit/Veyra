#!/bin/bash
# GitHub Repository Setup Script
echo "FINANCIAL MASTER - GITHUB SETUP"
echo "=================================="

# Navigate to project directory
cd ~/veyra

echo ""
echo "CONFIGURING GIT"
echo "=================="

# Check if git is configured
if [ -z "$(git config --global user.name)" ]; then
    echo "Please enter your Git user name:"
    read -r GIT_NAME
    git config --global user.name "$GIT_NAME"
fi

if [ -z "$(git config --global user.email)" ]; then
    echo "Please enter your Git email:"
    read -r GIT_EMAIL
    git config --global user.email "$GIT_EMAIL"
fi

echo "Git configured:"
echo "   Name: $(git config --global user.name)"
echo "   Email: $(git config --global user.email)"

echo ""
echo "SETTING UP SSH KEYS"
echo "======================"

# Check if SSH key exists
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -C "$(git config --global user.email)" -f ~/.ssh/id_ed25519 -N ""
    
    # Add to SSH agent
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    
    echo "SSH key generated!"
    echo "Public key:"
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "Copy the public key above and add it to GitHub:"
    echo "   1. Go to GitHub -> Settings -> SSH and GPG keys"
    echo "   2. Click 'New SSH key'"
    echo "   3. Paste the key and save"
    read -p "Press Enter after adding SSH key to GitHub..."
else
    echo "SSH key already exists"
fi

echo ""
echo "CREATING GITHUB REPOSITORY"
echo "=============================="

echo "Opening GitHub to create repository..."
echo "Repository details:"
echo "   Name: veyra"
echo "   Description: Veyra - Zero-Cost Multi-Cloud Platform"
echo "   Visibility: Public (free)"
echo "   Include: README.md, .gitignore (Node.js)"

read -p "Press Enter after creating repository on GitHub..."

echo ""
echo "CONNECTING TO GITHUB"
echo "========================"

# Initialize git repository
if [ ! -d .git ]; then
    git init
    echo "Git repository initialized"
else
    echo "Git repository already exists"
fi

# Add remote origin
echo "Please enter your GitHub username:"
read -r GITHUB_USERNAME

git remote add origin "git@github.com:$GITHUB_USERNAME/veyra.git"
echo "Remote origin added"

echo ""
echo "PUSHING TO GITHUB"
echo "===================="

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Veyra zero-cost setup

- Complete zero-cost multi-cloud platform
- Frontend: Responsive web application
- Backend: Express.js API server
- Database: PostgreSQL with Docker
- Cache: Redis with Docker
- AI/ML: Ollama integration
- Monitoring: Health checks and status endpoints
- Security: Helmet.js, CORS, environment variables
- Development: Hot reload with nodemon
- Deployment: Ready for Cloudflare + Render + Neon"

# Push to GitHub
git push -u origin main

echo ""
echo "GITHUB SETUP COMPLETE!"
echo "========================"
echo ""
echo "Repository: https://github.com/$GITHUB_USERNAME/veyra"
echo "Repository will be available at: https://$GITHUB_USERNAME.github.io/veyra"
echo "Next step: Run cloud-setup.sh"
