# Deployment Documentation

## Overview

This document provides comprehensive deployment instructions for Veyra across different environments and platforms.

## Prerequisites

### Required Tools

- Docker 20.10+
- Kubernetes 1.24+ (for production)
- kubectl
- Helm 3.x
- Terraform 1.x (optional, for infrastructure provisioning)
- pnpm 10+
- Node.js 22+

### Required Accounts

- Docker Hub or container registry
- Cloud provider account (AWS/GCP/Azure)
- Domain name (optional)

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/jayprophit/Veyra.git
cd Veyra

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Staging Deployment

### Prerequisites

- Staging environment configured
- Database credentials
- API keys for external services
- SSL certificate

### Deployment Steps

```bash
# Set environment
export ENVIRONMENT=staging

# Build containers
pnpm build

# Deploy to staging
kubectl apply -f infrastructure/kubernetes/staging/
```

### Verification

```bash
# Check deployment status
kubectl get pods -n staging

# Check services
kubectl get services -n staging

# View logs
kubectl logs -f deployment/api-gateway -n staging
```

## Production Deployment

### Prerequisites

- Production environment configured
- Database backups tested
- Monitoring configured
- Alert rules configured
- SSL certificate configured
- DNS configured

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Database migrations prepared
- [ ] Backup current production
- [ ] Notify stakeholders
- [ ] Prepare rollback plan

### Deployment Steps

```bash
# Set environment
export ENVIRONMENT=production

# Build containers
pnpm build

# Tag containers
docker tag veyra/api-gateway:latest veyra/api-gateway:v1.0.0

# Push to registry
docker push veyra/api-gateway:v1.0.0

# Deploy to production
kubectl apply -f infrastructure/kubernetes/production/

# Verify deployment
kubectl rollout status deployment/api-gateway -n production
```

### Post-Deployment Verification

```bash
# Health checks
curl https://api.veyra.com/health

# Check metrics
curl https://api.veyra.com/metrics

# Verify database connections
kubectl exec -it deployment/database -n production -- psql -U veyra -d veyra -c "SELECT 1;"
```

## Kubernetes Deployment

### Namespace Configuration

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: veyra-production
  labels:
    name: veyra-production
    environment: production
```

### Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: veyra-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: veyra/api-gateway:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: veyra-production
spec:
  selector:
    app: api-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: veyra-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:22-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

EXPOSE 8000

CMD ["node", "dist/index.js"]
```

### Build and Push

```bash
# Build image
docker build -t veyra/api-gateway:v1.0.0 .

# Tag image
docker tag veyra/api-gateway:v1.0.0 registry.veyra.com/api-gateway:v1.0.0

# Login to registry
docker login registry.veyra.com

# Push image
docker push registry.veyra.com/api-gateway:v1.0.0
```

## Terraform Deployment

### Infrastructure Configuration

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_eks_cluster" "veyra" {
  name     = "veyra-cluster"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = aws_subnet.veyra[*].id
  }
}

resource "aws_eks_node_group" "veyra" {
  cluster_name    = aws_eks_cluster.veyra.name
  node_group_name = "veyra-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.veyra[*].id

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 3
  }
}
```

### Apply Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy
```

## Cloudflare Deployment

### Workers Configuration

```javascript
// cloudflare/api-gateway.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route requests to backend
    if (url.pathname.startsWith('/api/')) {
      const backendUrl = `https://api.veyra.com${url.pathname}`;
      const response = await fetch(backendUrl, request);
      return response;
    }
    
    // Serve static assets
    return new Response('Not found', { status: 404 });
  }
};
```

### Deploy Worker

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy worker
wrangler deploy cloudflare/api-gateway.js
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'veyra'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Grafana Dashboards

Import pre-configured dashboards from `infrastructure/monitoring/grafana/dashboards/`

### Log Aggregation

```yaml
# fluentd configuration
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.log.pos
  tag kubernetes.*
  read_from_head true
  <parse>
    @type json
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>
```

## Rollback Procedures

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/api-gateway -n production

# Rollback to previous version
kubectl rollout undo deployment/api-gateway -n production

# Rollback to specific revision
kubectl rollout undo deployment/api-gateway --to-revision=2 -n production
```

### Database Rollback

```bash
# List migrations
kubectl exec -it deployment/database -n production -- psql -U veyra -d veyra -c "SELECT * FROM schema_migrations;"

# Rollback specific migration
kubectl exec -it deployment/database -n production -- psql -U veyra -d veyra -c "ROLLBACK;"
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it deployment/database -n production -- pg_dump -U veyra veyra > backup.sql

# Restore from backup
kubectl exec -i deployment/database -n production -- psql -U veyra veyra < backup.sql
```

### Automated Backups

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: veyra-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - pg_dump
            - -U
            - veyra
            - veyra
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: password
          restartPolicy: OnFailure
```

## Troubleshooting

### Common Issues

**Pod Not Starting**

```bash
# Check pod status
kubectl describe pod <pod-name> -n production

# View logs
kubectl logs <pod-name> -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

**Service Not Accessible**

```bash
# Check service endpoints
kubectl get endpoints <service-name> -n production

# Check ingress
kubectl describe ingress <ingress-name> -n production

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://<service-name>
```

**Database Connection Issues**

```bash
# Check database pod
kubectl get pods -n production -l app=database

# Test database connection
kubectl run -it --rm psql --image=postgres:14 --restart=Never -- psql -h <database-host> -U veyra -d veyra
```

## Security Considerations

### Secrets Management

```bash
# Create secret
kubectl create secret generic api-secret \
  --from-literal=api-key=your-api-key \
  --from-literal=api-secret=your-api-secret \
  -n production

# Use secret in deployment
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: api-secret
        key: api-key
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: veyra-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

## Performance Optimization

### Resource Limits

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
  namespace: veyra-production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-gateway
```

## Support

For deployment issues:
- Email: ops@veyra.com
- Documentation: https://docs.veyra.com
- Status Page: https://status.veyra.com
