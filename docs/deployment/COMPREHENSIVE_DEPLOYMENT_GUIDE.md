# Comprehensive Deployment Guide

## Overview

This guide provides complete deployment instructions for Financial Master with all FactSet and enhanced financial repository integrations across multiple deployment strategies.

## Deployment Strategies

### 1. Zero-Cost Multi-Cloud Deployment

**Perfect for:** Startups, Testing, First Customers  
**Cost:** $0/month (free tiers only)  
**Setup Time:** 30-45 minutes with automated scripts  
**Capacity:** 100+ users  

### 2. Comprehensive Multi-Cloud Deployment

**Perfect for:** Enterprise Scale, Global Deployment  
**Cost:** $380-$15,000/month  
**Setup Time:** 3-6 months with full infrastructure  
**Capacity:** Unlimited users  

## Zero-Cost Deployment

### Architecture Overview

```
Zero-Cost Architecture
├── Frontend (Cloudflare Pages)
│   ├── Static site hosting
│   ├── CDN distribution
│   └── SSL certificates
├── Backend API (Render)
│   ├── FastAPI application
│   ├── PostgreSQL database
│   └── Redis caching
├── External APIs
│   ├── FactSet APIs
│   ├── Alpha Vantage
│   ├── Yahoo Finance
│   └── Polygon.io
└── Monitoring (Uptime Robot)
    ├── Service monitoring
    ├── Performance tracking
    └── Alert notifications
```

### Prerequisites

#### Required Accounts

1. **Cloudflare Account** (Free tier)
   - Sign up at [cloudflare.com](https://cloudflare.com)
   - Create Pages project
   - Get custom domain (optional)

2. **Render Account** (Free tier)
   - Sign up at [render.com](https://render.com)
   - Connect GitHub repository
   - Configure web service

3. **GitHub Account** (Free tier)
   - Sign up at [github.com](https://github.com)
   - Fork or clone repository
   - Configure Actions

4. **API Keys** (Free tiers)
   - FactSet Developer Account
   - Alpha Vantage API Key
   - Polygon.io API Key
   - Yahoo Finance (no key required)

### Automated Setup

#### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/jpowell/financial-master.git
cd financial-master

# Create your fork (optional)
git remote add fork https://github.com/YOUR_USERNAME/financial-master.git
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

#### Step 3: Run Setup Script

```bash
# Make setup script executable
chmod +x setup-scripts/setup-zero-cost.sh

# Run automated setup
./setup-scripts/setup-zero-cost.sh
```

#### Setup Script Details

```bash
#!/bin/bash
# setup-scripts/setup-zero-cost.sh

echo "🚀 Starting Zero-Cost Deployment Setup..."

# Check prerequisites
command -v git >/dev/null 2>&1 || { echo "❌ Git is required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ Node.js is required"; exit 1; }
command -v python >/dev/null 2>&1 || { echo "❌ Python is required"; exit 1; }

# Configure environment
echo "📝 Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "🔧 Please edit .env with your API keys"
    read -p "Press Enter after editing .env: "
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install
pip install -r requirements.txt

# Build frontend
echo "🏗️ Building frontend..."
cd src/frontend
npm run build
cd ../..

# Deploy to Cloudflare Pages
echo "☁️ Deploying to Cloudflare Pages..."
npx wrangler pages deploy src/frontend/dist --project-name financial-master

# Deploy backend to Render
echo "🚀 Deploying backend to Render..."
# This would typically be done through Render dashboard
echo "📊 Visit https://dashboard.render.com to deploy backend service"

# Setup monitoring
echo "📈 Setting up monitoring..."
echo "📊 Visit https://uptimerobot.com to set up monitoring"

echo "✅ Zero-Cost Deployment Setup Complete!"
echo "🌐 Frontend: https://financial-master.pages.dev"
echo "🔧 Backend: Configure at https://dashboard.render.com"
echo "📈 Monitoring: Configure at https://uptimerobot.com"
```

### Manual Deployment

#### Frontend Deployment (Cloudflare Pages)

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy frontend
cd src/frontend
npm run build
wrangler pages deploy dist --project-name financial-master
```

#### Backend Deployment (Render)

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New Web Service"
   - Connect GitHub repository
   - Select `financial-master` repository

2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt && uvicorn src.backend.main:app --host 0.0.0.0`
   - Start Command: `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT`
   - Runtime: `Python 3.11`

3. **Environment Variables**
   - Add all variables from `.env` file
   - Use Render's secret management for sensitive data

4. **Database Setup**
   - Render provides PostgreSQL automatically
   - Get connection string from dashboard
   - Update `DATABASE_URL` in environment

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Monitoring Setup

#### Uptime Robot Configuration

```yaml
# Uptime Robot monitoring
services:
  - name: Financial Master Frontend
    url: https://financial-master.pages.dev
    interval: 5
    alert_contacts:
      - email: admin@financialmaster.com
      - slack: https://hooks.slack.com/your-webhook
  
  - name: Financial Master Backend
    url: https://your-service.onrender.com/health
    interval: 5
    alert_contacts:
      - email: admin@financialmaster.com
      - slack: https://hooks.slack.com/your-webhook
```

## Comprehensive Multi-Cloud Deployment

### Architecture Overview

```
Comprehensive Architecture
├── Frontend (AWS CloudFront + S3)
│   ├── React application
│   ├── CDN distribution
│   ├── SSL certificates
│   └── Static asset optimization
├── Backend API (AWS ECS + Fargate)
│   ├── FastAPI application
│   ├── Auto-scaling
│   ├── Load balancing
│   └── Health monitoring
├── Database (AWS RDS + Redis)
│   ├── PostgreSQL cluster
│   ├── Redis cluster
│   ├── Read replicas
│   └── Backup automation
├── External APIs (Multiple Providers)
│   ├── FactSet APIs
│   ├── Alpha Vantage
│   ├── Yahoo Finance
│   ├── Polygon.io
│   └── QuantConnect
├── Monitoring (AWS CloudWatch + Grafana)
│   ├── Application metrics
│   ├── Infrastructure monitoring
│   ├── Log aggregation
│   └── Alert management
└── Security (AWS WAF + Shield)
    ├── DDoS protection
    ├── API rate limiting
    ├── SSL/TLS encryption
    └── Access control
```

### Infrastructure Setup

#### AWS Infrastructure

```yaml
# aws-infrastructure.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: Financial Master Comprehensive Infrastructure

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
  
  DatabasePassword:
    Type: String
    NoEcho: true
    MinLength: 8

Resources:
  # VPC Configuration
  FinancialMasterVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: financial-master-vpc

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref FinancialMasterVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !Ref 'AWS::Region']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: financial-master-public-1

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref FinancialMasterVPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !Ref 'AWS::Region']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: financial-master-public-2

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref FinancialMasterVPC
      CidrBlock: 10.0.3.0/24
      AvailabilityZone: !Select [0, !Ref 'AWS::Region']
      Tags:
        - Key: Name
          Value: financial-master-private-1

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref FinancialMasterVPC
      CidrBlock: 10.0.4.0/24
      AvailabilityZone: !Select [1, !Ref 'AWS::Region']
      Tags:
        - Key: Name
          Value: financial-master-private-2

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: financial-master-igw

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref FinancialMasterVPC
      InternetGatewayId: !Ref InternetGateway

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref FinancialMasterVPC
      Tags:
        - Key: Name
          Value: financial-master-public-routes

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  # RDS Database
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for Financial Master database
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: financial-master-db-subnets

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: financial-master-db
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: '15.4'
      AllocatedStorage: 100
      StorageType: gp2
      DBName: financial_master
      MasterUsername: postgres
      MasterUserPassword: !Ref DatabasePassword
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      BackupRetentionPeriod: 7
      MultiAZ: true
      StorageEncrypted: true
      Tags:
        - Key: Name
          Value: financial-master-db

  # ElastiCache Redis
  RedisSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Financial Master Redis
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: financial-master-redis-subnets

  RedisCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupId: financial-master-redis
      Description: Redis cluster for Financial Master
      CacheNodeType: cache.t3.micro
      NumCacheClusters: 2
      Engine: redis
      EngineVersion: 7.0
      CacheSubnetGroupName: !Ref RedisSubnetGroup
      SecurityGroupIds:
        - !Ref RedisSecurityGroup
      Tags:
        - Key: Name
          Value: financial-master-redis

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: financial-master
      CapacityProviders:
        - Name: FARGATE
          DefaultCapacityProviderStrategy: SPREAD_CAPACITY_PROVIDER_STRATEGY
      Tags:
        - Key: Name
          Value: financial-master-ecs

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: financial-master-task
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: 1024
      Memory: 2048
      ExecutionRoleArn: !Ref TaskExecutionRole
      TaskRoleArn: !Ref TaskRole
      ContainerDefinitions:
        - Name: financial-master-container
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/financial-master:latest'
          PortMappings:
            - ContainerPort: 8000
              Protocol: tcp
          Environment:
            - Name: DATABASE_URL
              Value: !Sub 'postgresql://postgres:${DatabasePassword}@${Database.Endpoint}:${Database.Port}/financial_master'
            - Name: REDIS_URL
              Value: !Sub 'redis://${RedisCluster.PrimaryEndPoint.Address}:${RedisCluster.PrimaryEndPoint.Port}/0'
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: /ecs/financial-master
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # Service
  Service:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: financial-master-service
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      PlatformVersion: LATEST
      NetworkConfiguration:
        AwsvpcConfiguration:
          SecurityGroups:
            - !Ref ServiceSecurityGroup
          Subnets:
            - !Ref PrivateSubnet1
            - !Ref PrivateSubnet2
          AssignPublicIp: DISABLED
      LoadBalancers:
        - ContainerName: financial-master-container
          ContainerPort: 8000
          TargetGroupArn: !Ref TargetGroup

  # Application Load Balancer
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: financial-master-alb
      IpAddressType: ipv4
      Scheme: internet-facing
      Type: application
      SecurityGroups:
        - !Ref LoadBalancerSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      Tags:
        - Key: Name
          Value: financial-master-alb

  # Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: financial-master-targets
      Port: 80
      Protocol: HTTP
      VpcId: !Ref FinancialMasterVPC
      TargetType: ip
      HealthCheckProtocol: HTTP
      HealthCheckPort: 8000
      HealthCheckPath: /health
      Matcher:
        HttpCode: 200
      Tags:
        - Key: Name
          Value: financial-master-targets

Outputs:
  LoadBalancerDNS:
    Description: DNS name of the load balancer
    Value: !GetAtt LoadBalancer.DNSName
    Export:
      Name: LoadBalancerDNS
```

#### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-master
  labels:
    app: financial-master
spec:
  replicas: 3
  selector:
    matchLabels:
      app: financial-master
  template:
    metadata:
      labels:
        app: financial-master
    spec:
      containers:
      - name: financial-master
        image: financial-master:latest
        ports:
        - containerPort: 8000
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: financial-master-secrets
                key: database-url
          - name: REDIS_URL
            valueFrom:
              secretKeyRef:
                name: financial-master-secrets
                key: redis-url
          - name: FACTSET_API_KEY
            valueFrom:
              secretKeyRef:
                name: financial-master-secrets
                key: factset-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: financial-master-service
spec:
  selector:
    app: financial-master
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: financial-master-secrets
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  redis-url: <base64-encoded-redis-url>
  factset-api-key: <base64-encoded-factset-key>
```

### Monitoring and Logging

#### CloudWatch Configuration

```python
# CloudWatch logging setup
import boto3
import logging
from pythonjsonlogger import jsonlogger

class CloudWatchHandler(logging.Handler):
    def __init__(self, log_group, log_stream):
        super().__init__()
        self.log_group = log_group
        self.log_stream = log_stream
        self.client = boto3.client('logs')
    
    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[
                    {
                        'timestamp': int(record.created * 1000),
                        'message': log_entry,
                        'level': record.levelname
                    }
                ]
            )
        except Exception as e:
            print(f"Error sending to CloudWatch: {e}")

# Configure logging
logger = logging.getLogger('financial_master')
logger.addHandler(CloudWatchHandler('financial-master', 'application'))
logger.setLevel(logging.INFO)
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Financial Master Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(rate(api_request_duration_seconds_sum[5m]))",
            "legendFormat": "Response Time"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_errors_total[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      }
    ]
  }
}
```

## Performance Optimization

### Database Optimization

#### PostgreSQL Configuration

```sql
-- PostgreSQL optimization settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_holdings_symbol ON holdings(symbol);
CREATE INDEX CONCURRENTLY idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX CONCURRENTLY idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX CONCURRENTLY idx_technical_indicators_symbol ON technical_indicators(symbol);

-- Partition large tables
CREATE TABLE market_data_partitioned (
    LIKE market_data INCLUDING ALL
) PARTITION BY RANGE (timestamp);

CREATE TABLE market_data_2024 PARTITION OF market_data_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

#### Redis Configuration

```conf
# redis.conf optimization
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### Application Optimization

#### Connection Pooling

```python
# Database connection pooling
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Redis connection pooling
import redis
from redis.connection import ConnectionPool

redis_pool = ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    retry_on_timeout=True
)
redis_client = redis.Redis(connection_pool=redis_pool)
```

## Security Configuration

### SSL/TLS Setup

#### Let's Encrypt Certificate

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot --nginx -d api.financialmaster.com -d www.financialmaster.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

#### WAF Configuration

```yaml
# AWS WAF rules
Resources:
  FinancialMasterWAF:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: financial-master-waf
      Scope: CLOUDFRONT
      DefaultAction:
        Allow: {}
      Rules:
        - Name: RateLimitRule
          Priority: 1
          Statement:
            RateBasedStatement:
              Limit: 1000
              AggregateKeyType: IP
        - Name: SQLInjectionRule
          Priority: 2
          Statement:
            SqliMatchStatement:
              FieldToMatch: BODY
              TextTransformations:
                - URL_DECODE
                - HTML_ENTITY_DECODE
        - Name: XSSRule
          Priority: 3
          Statement:
            XssMatchStatement:
              FieldToMatch: BODY
              TextTransformations:
                - URL_DECODE
                - HTML_ENTITY_DECODE
```

### Access Control

#### API Authentication

```python
# JWT authentication
from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

## Backup and Disaster Recovery

### Database Backup Strategy

```bash
# Automated backup script
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="financial_master"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U postgres -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://financial-master-backups/database/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: backup_$DATE.sql.gz"
```

### Application Backup

```bash
# Application backup script
#!/bin/bash
# backup-application.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/application"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Backup source code
git archive --format=tar.gz --prefix=source_$DATE/ HEAD > $BACKUP_DIR/source_$DATE.tar.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/config_$DATE.tar.gz s3://financial-master-backups/config/
aws s3 cp $BACKUP_DIR/source_$DATE.tar.gz s3://financial-master-backups/source/

echo "Application backup completed"
```

### Disaster Recovery Plan

```yaml
# disaster-recovery.yml
disaster_recovery:
  rto: 4  # Recovery Time Objective: 4 hours
  rpo: 1  # Recovery Point Objective: 1 hour
  
  procedures:
    - name: "Database Recovery"
      steps:
        - "Stop application services"
        - "Restore database from latest backup"
        - "Verify data integrity"
        - "Start application services"
        - "Run health checks"
    
    - name: "Application Recovery"
      steps:
        - "Deploy latest stable version"
        - "Restore configuration files"
        - "Update DNS records"
        - "Verify all services"
        - "Monitor performance"
  
  communication:
    - "Notify stakeholders via email"
    - "Update status page"
    - "Send Slack notifications"
    - "Post incident report"
```

## Troubleshooting

### Common Deployment Issues

#### 1. Database Connection Failures

**Problem**: Cannot connect to database  
**Solutions**:
1. Check database service status
2. Verify connection string format
3. Check firewall rules
4. Validate credentials
5. Test network connectivity

#### 2. API Rate Limiting

**Problem**: API requests being rate limited  
**Solutions**:
1. Implement exponential backoff
2. Use multiple API keys
3. Implement proper caching
4. Optimize request frequency
5. Monitor usage metrics

#### 3. Performance Issues

**Problem**: Slow application response  
**Solutions**:
1. Check database query performance
2. Monitor resource utilization
3. Optimize caching strategy
4. Scale infrastructure
5. Profile application code

#### 4. SSL/TLS Issues

**Problem**: Certificate errors  
**Solutions**:
1. Verify certificate validity
2. Check certificate chain
3. Update certificate if expired
4. Verify DNS configuration
5. Test with SSL tools

### Debugging Tools

#### Application Logs

```bash
# View application logs
docker logs financial-master-container

# View database logs
docker logs postgres-container

# View nginx logs
docker logs nginx-container
```

#### Performance Monitoring

```bash
# Check system resources
docker stats financial-master-container

# Monitor database performance
docker exec postgres-container pg_stat_activity

# Check Redis performance
docker exec redis-container redis-cli info
```

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**License:** MIT
