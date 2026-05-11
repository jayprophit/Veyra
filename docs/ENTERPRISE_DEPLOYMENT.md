# Veyra - Enterprise Deployment Guide

## Overview
Veyra is now enterprise-grade with production-ready deployment configurations, monitoring, security, and scalability features.

## Prerequisites
- Kubernetes 1.25+
- Redis 7.0+
- PostgreSQL 15+
- Prometheus + Grafana
- Ingress controller (nginx/traefik)

## Quick Start

### 1. Deploy Infrastructure
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy secrets
kubectl create secret generic veyra-secrets \
  --from-literal=database-url="postgresql://user:pass@postgres:5432/finmaster" \
  --from-literal=redis-url="redis://redis:6379/0" \
  --from-literal=jwt-secret="your-production-secret"

# Deploy application
kubectl apply -f k8s/deployment-enterprise.yaml
```

### 2. Setup Monitoring
```bash
# Deploy Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Import Grafana dashboard
kubectl apply -f monitoring/grafana-dashboard.yaml
```

### 3. Configure Ingress
```bash
# Deploy ingress
kubectl apply -f k8s/ingress.yaml
```

## Features
- ✅ Auto-scaling (HPA)
- ✅ Circuit breakers
- ✅ Rate limiting
- ✅ Health checks
- ✅ Graceful shutdown
- ✅ Structured logging
- ✅ Prometheus metrics
- ✅ Security scanning
- ✅ CI/CD pipeline

## Monitoring
- Health: `/api/v1/health`
- Metrics: `/metrics`
- Logs: Structured JSON
- Dashboard: Grafana

## Support
Enterprise support available with SLA guarantees.
