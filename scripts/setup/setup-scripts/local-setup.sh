#!/bin/bash
# Local Development Setup Script
echo "FINANCIAL MASTER - LOCAL DEVELOPMENT SETUP"
echo "=============================================="

# Check if required tools are installed
echo ""
echo "CHECKING REQUIRED TOOLS"
echo "=========================="

# Check Node.js
if command -v node &> /dev/null; then
    echo "Node.js: $(node --version)"
else
    echo "Node.js not installed"
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "Docker: $(docker --version)"
else
    echo "Docker not installed"
    echo "Download from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    echo "Git: $(git --version)"
else
    echo "Git not installed"
    echo "Download from: https://git-scm.com/"
    exit 1
fi

echo ""
echo "CREATING PROJECT STRUCTURE"
echo "============================"

# Create project directory
PROJECT_DIR="$HOME/veyra"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create directory structure
mkdir -p src/{frontend,backend,shared}
mkdir -p config
mkdir -p scripts
mkdir -p docs
mkdir -p tests
mkdir -p monitoring

echo "Project structure created"

echo ""
echo "INITIALIZING NODE PROJECT"
echo "============================"

# Create package.json
cat > package.json << 'EOF'
{
  "name": "veyra",
  "version": "1.0.0",
  "description": "Veyra - Zero-Cost Multi-Cloud Platform",
  "main": "src/backend/index.js",
  "scripts": {
    "start": "node src/backend/index.js",
    "dev": "nodemon src/backend/index.js",
    "build": "npm run build:frontend && npm run build:backend",
    "build:frontend": "cd src/frontend && npm run build",
    "build:backend": "cd src/backend && npm run build",
    "test": "jest",
    "lint": "eslint src/",
    "deploy": "npm run build && npm run deploy:frontend && npm run deploy:backend",
    "deploy:frontend": "npm run build:frontend && wrangler pages publish dist",
    "deploy:backend": "npm run build:backend && wrangler deploy"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "dotenv": "^16.3.1",
    "pg": "^8.11.3",
    "redis": "^4.6.8",
    "axios": "^1.5.0",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "joi": "^17.9.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.6.2",
    "eslint": "^8.46.0",
    "@types/node": "^20.5.0"
  }
}
EOF

echo "package.json created"

echo ""
echo "CREATING BACKEND FILES"
echo "========================"

# Create backend index.js
cat > src/backend/index.js << 'EOF'
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

app.get('/api/test', (req, res) => {
  res.json({ 
    message: 'Veyra API is working!',
    environment: process.env.NODE_ENV || 'development'
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
  console.log('Veyra API running on port ' + PORT);
  console.log('Health check: http://localhost:' + PORT + '/health');
  console.log('API test: http://localhost:' + PORT + '/api/test');
});
EOF

echo "Backend files created"

echo ""
echo "CREATING FRONTEND FILES"
echo "=========================="

# Create frontend index.html
cat > src/frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyra</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            color: white;
        }
        .card { 
            background: white; 
            padding: 30px; 
            border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .button { 
            background: #007bff; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .button:hover { background: #0056b3; }
        .status-indicator { 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px;
            font-weight: bold;
        }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .feature-list { list-style: none; }
        .feature-list li { 
            padding: 8px 0; 
            border-bottom: 1px solid #eee;
        }
        .feature-list li:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Veyra</h1>
            <p>Zero-Cost Multi-Cloud Financial Platform</p>
        </div>
        
        <div class="card">
            <h2>System Status</h2>
            <div id="status">Checking system status...</div>
        </div>
        
        <div class="card">
            <h2>Platform Features</h2>
            <ul class="feature-list">
                <li>Multi-cloud deployment (Cloudflare + Render + Neon)</li>
                <li>Real-time financial data (Alpha Vantage API)</li>
                <li>AI-powered analytics (Ollama + Hugging Face)</li>
                <li>Mobile responsive design</li>
                <li>Progressive Web App (PWA)</li>
                <li>Zero-cost infrastructure</li>
                <li>Enterprise-grade security</li>
                <li>Real-time monitoring</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Development Workflow</h2>
            <p><strong>Local Development:</strong> WindSurf + Docker + Node.js</p>
            <p><strong>Version Control:</strong> Git + GitHub</p>
            <p><strong>CI/CD:</strong> GitHub Actions</p>
            <p><strong>Deployment:</strong> Automatic on push to main</p>
            <p><strong>Monitoring:</strong> Grafana + Prometheus + Uptime Robot</p>
        </div>
    </div>

    <script>
        // Check API status
        async function checkStatus() {
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                
                document.getElementById('status').innerHTML = `
                    <div class="status-indicator status-healthy">ONLINE</div>
                    <p><strong>API Status:</strong> ${data.message}</p>
                    <p><strong>Environment:</strong> ${data.environment}</p>
                    <p><strong>Last Checked:</strong> ${new Date().toLocaleString()}</p>
                `;
            } catch (error) {
                document.getElementById('status').innerHTML = `
                    <div class="status-indicator status-error">OFFLINE</div>
                    <p><strong>API Error:</strong> ${error.message}</p>
                    <p><strong>Last Checked:</strong> ${new Date().toLocaleString()}</p>
                `;
            }
        }

        // Check status on load
        checkStatus();
        
        // Check status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
EOF

echo "Frontend files created"

echo ""
echo "CREATING DOCKER CONFIGURATION"
echo "================================"

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: veyra
      POSTGRES_USER: veyra
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U veyra"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  ollama_data:
EOF

echo "Docker configuration created"

echo ""
echo "CREATING ENVIRONMENT FILES"
echo "=============================="

# Create .env.example
cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://veyra:password@localhost:5432/veyra
REDIS_URL=redis://localhost:6379

# Authentication
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-identifier

# API Keys
ALPHA_VANTAGE_KEY=your-alpha-vantage-key
HUGGINGFACE_API_KEY=your-huggingface-key
OPENAI_API_KEY=your-openai-key

# Cloud Services
CLOUDFLARE_API_TOKEN=your-cloudflare-token
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
RENDER_API_KEY=your-render-api-key

# Local Development
OLLAMA_URL=http://localhost:11434
NODE_ENV=development
PORT=8000
EOF

# Copy to .env
cp .env.example .env

echo "Environment files created"

echo ""
echo "INSTALLING DEPENDENCIES"
echo "=========================="

# Install Node.js dependencies
npm install

echo "Dependencies installed"

echo ""
echo "STARTING LOCAL SERVICES"
echo "=========================="

# Start Docker services
echo "Starting PostgreSQL, Redis, and Ollama..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

# Pull Ollama model
echo "Pulling Ollama model..."
docker-compose exec ollama ollama pull llama2

echo ""
echo "LOCAL SETUP COMPLETE!"
echo "========================"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Start development: npm run dev"
echo "Access application: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "Docker services: docker-compose ps"
echo "Stop services: docker-compose down"
echo ""
echo "Next step: Run github-setup.sh"
