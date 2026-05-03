# Financial Master Helm Chart

This Helm chart deploys Financial Master - The Open-Source Bloomberg Terminal Alternative - on Kubernetes.

## Prerequisites

- Kubernetes 1.24+
- Helm 3.12+
- Ingress Controller (nginx recommended)
- cert-manager (for TLS certificates)

## Installation

### Quick Start

```bash
# Add Bitnami repository for dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Financial Master
helm install financial-master ./helm/financial-master \
  --namespace financial-master \
  --create-namespace \
  --set global.environment=production
```

### With Custom Values

```bash
# Create custom values file
cat > my-values.yaml <<EOF
api:
  ingress:
    hosts:
      - host: api.mycompany.com
frontend:
  ingress:
    hosts:
      - host: app.mycompany.com
postgresql:
  auth:
    password: "my-secure-password"
EOF

# Install with custom values
helm install financial-master ./helm/financial-master \
  --namespace financial-master \
  --create-namespace \
  -f my-values.yaml
```

## Upgrading

```bash
# Update dependencies
helm dependency update ./helm/financial-master

# Upgrade release
helm upgrade financial-master ./helm/financial-master \
  --namespace financial-master \
  -f my-values.yaml
```

## Uninstallation

```bash
helm uninstall financial-master --namespace financial-master
kubectl delete namespace financial-master
```

## Configuration

See [values.yaml](values.yaml) for full configuration options.

### Key Parameters

| Parameter               | Description                      | Default     |
|-------------------------|----------------------------------|-------------|
| `api.replicaCount` | API server replicas | `3` |
| `api.image.tag` | API image tag | `v4.0.0` |
| `api.autoscaling.enabled` | Enable HPA | `true` |
| `api.ingress.enabled` | Enable ingress | `true` |
| `frontend.replicaCount` | Frontend replicas | `2` |
| `worker.replicaCount` | Celery worker replicas | `2` |
| `postgresql.enabled` | Deploy PostgreSQL | `true` |
| `redis.enabled` | Deploy Redis | `true` |

### Environment-Specific Values

#### Development

```yaml
# values-dev.yaml
api:
  replicaCount: 1
  autoscaling:
    enabled: false
postgresql:
  primary:
    persistence:
      enabled: false
```

#### Staging

```yaml
# values-staging.yaml
global:
  environment: staging
api:
  replicaCount: 2
  ingress:
    hosts:
      - host: api-staging.financialmaster.app
```

#### Production

```yaml
# values-prod.yaml
global:
  environment: production
api:
  replicaCount: 3
  autoscaling:
    minReplicas: 3
    maxReplicas: 10
  resources:
    limits:
      memory: 4Gi
      cpu: 2000m
```

## Secrets Management

Create a Kubernetes secret for sensitive data:

```bash
kubectl create secret generic financial-master-secrets \
  --namespace financial-master \
  --from-literal=JWT_SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=API_KEY=$(openssl rand -hex 16) \
  --from-literal=ALPACA_API_KEY=your-alpaca-key \
  --from-literal=ALPACA_SECRET_KEY=your-alpaca-secret
```

Or use external-secrets operator for cloud provider integration.

## Monitoring

The chart includes Prometheus and Grafana for monitoring:

```bash
# Access Grafana
kubectl port-forward svc/financial-master-grafana 3000:3000 -n financial-master

# Login with admin/admin (change in values.yaml)
```

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n financial-master

# View API logs
kubectl logs -n financial-master -l app.kubernetes.io/component=api

# Check events
kubectl get events -n financial-master --sort-by='.lastTimestamp'

# Debug ingress
kubectl describe ingress -n financial-master
```
