# Veyra Platform - Comprehensive Troubleshooting Guide

**Last Updated:** May 12, 2026  
**Version:** 1.0  
**Audience:** Developers, DevOps Engineers, System Administrators  

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [System Health Monitoring](#system-health-monitoring)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Backend Troubleshooting](#backend-troubleshooting)
5. [Frontend Issues](#frontend-issues)
6. [Mobile App Problems](#mobile-app-problems)
7. [Database Issues](#database-issues)
8. [API Problems](#api-problems)
9. [Infrastructure Issues](#infrastructure-issues)
10. [Performance Issues](#performance-issues)
11. [Security Issues](#security-issues)
12. [Integration Issues](#integration-issues)
13. [Emergency Procedures](#emergency-procedures)
14. [Debugging Tools](#debugging-tools)
15. [Contact Support](#contact-support)

---

## 🚀 Quick Reference

### Critical Commands
```bash
# Check system status
kubectl get pods -n veyra
kubectl get services -n veyra
kubectl describe pod <pod-name> -n veyra

# Check logs
kubectl logs -f deployment/veyra-api -n veyra
kubectl logs -f deployment/veyra-frontend -n veyra

# Restart services
kubectl rollout restart deployment/veyra-api -n veyra
kubectl rollout restart deployment/veyra-frontend -n veyra

# Scale services
kubectl scale deployment veyra-api --replicas=5 -n veyra
```

### Health Check Endpoints
- **Backend Health:** `https://api.veyra.com/health`
- **Frontend Health:** `https://app.veyra.com/health`
- **Database Health:** `https://api.veyra.com/health/db`
- **Redis Health:** `https://api.veyra.com/health/redis`

### Key Configuration Files
- **Kubernetes:** `deploy/k8s/`
- **Docker:** `config/docker/`
- **Environment:** `config/environments/`
- **Monitoring:** `monitoring/prometheus.yml`

---

## 🏥 System Health Monitoring

### Health Check Scripts

#### System Overview Check
```bash
#!/bin/bash
# check_system_health.sh

echo "=== Veyra System Health Check ==="
echo "Timestamp: $(date)"
echo ""

# Check Kubernetes cluster
echo "📊 Kubernetes Cluster Status:"
kubectl cluster-info
echo ""

# Check pod status
echo "📦 Pod Status:"
kubectl get pods -n veyra -o wide
echo ""

# Check service status
echo "🌐 Service Status:"
kubectl get services -n veyra
echo ""

# Check resource usage
echo "💾 Resource Usage:"
kubectl top pods -n veyra
echo ""

# Check PVC status
echo "📁 Storage Status:"
kubectl get pvc -n veyra
echo ""

# Check events
echo "⚠️ Recent Events:"
kubectl get events -n veyra --sort-by='.lastTimestamp' | tail -10
```

#### Application Health Check
```bash
#!/bin/bash
# check_app_health.sh

echo "=== Application Health Check ==="

# Backend health
echo "🔧 Backend Health:"
curl -s https://api.veyra.com/health | jq '.'
echo ""

# Frontend health
echo "🎨 Frontend Health:"
curl -s https://app.veyra.com/health | jq '.'
echo ""

# Database connectivity
echo "🗄️ Database Health:"
curl -s https://api.veyra.com/health/db | jq '.'
echo ""

# Redis connectivity
echo "🔴 Redis Health:"
curl -s https://api.veyra.com/health/redis | jq '.'
echo ""

# External APIs
echo "🌍 External API Status:"
curl -s https://api.veyra.com/health/external | jq '.'
```

### Monitoring Dashboard Access
- **Grafana:** `https://monitoring.veyra.com`
- **Prometheus:** `https://prometheus.veyra.com`
- **Jaeger Tracing:** `https://tracing.veyra.com`
- **Kiali Service Mesh:** `https://mesh.veyra.com`

---

## 🔧 Common Issues & Solutions

### Issue 1: High CPU Usage
**Symptoms:**
- API response times > 2 seconds
- CPU usage > 80% on pods
- Auto-scaling triggered frequently

**Solutions:**
```bash
# Check high CPU pods
kubectl top pods -n veyra --sort-by=cpu

# Check pod logs for issues
kubectl logs -f deployment/veyra-api -n veyra

# Scale up temporarily
kubectl scale deployment veyra-api --replicas=10 -n veyra

# Check for memory leaks
kubectl exec -it <pod-name> -n veyra -- top

# Restart problematic pods
kubectl delete pod <pod-name> -n veyra
```

### Issue 2: Database Connection Problems
**Symptoms:**
- Database timeout errors
- Connection refused messages
- Slow query performance

**Solutions:**
```bash
# Check database pod status
kubectl get pods -n veyra | grep database

# Check database logs
kubectl logs -f statefulset/veyra-database -n veyra

# Test database connectivity
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "SELECT 1;"

# Restart database
kubectl rollout restart statefulset/veyra-database -n veyra

# Check database metrics
curl -s https://api.veyra.com/health/db | jq '.'
```

### Issue 3: Memory Issues
**Symptoms:**
- Out of memory errors
- Pod crashes with OOMKilled
- High memory usage > 90%

**Solutions:**
```bash
# Check memory usage
kubectl top pods -n veyra --sort-by=memory

# Check for memory leaks
kubectl exec -it <pod-name> -n veyra -- free -h

# Increase memory limits
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","resources":{"limits":{"memory":"2Gi"}}}]}}}}'

# Restart services
kubectl rollout restart deployment/veyra-api -n veyra
```

---

## 🔧 Backend Troubleshooting

### API Service Issues

#### Problem: API Not Responding
**Diagnosis:**
```bash
# Check API pod status
kubectl get pods -n veyra | grep veyra-api

# Check API service
kubectl get svc veyra-api -n veyra

# Check API logs
kubectl logs -f deployment/veyra-api -n veyra

# Test API endpoint
curl -v https://api.veyra.com/health
```

**Solutions:**
```bash
# Restart API service
kubectl rollout restart deployment/veyra-api -n veyra

# Check ingress configuration
kubectl get ingress veyra-ingress -n veyra -o yaml

# Verify load balancer
kubectl get svc veyra-api-loadbalancer -n veyra

# Check network policies
kubectl get networkpolicy -n veyra
```

#### Problem: Authentication Failures
**Diagnosis:**
```bash
# Check auth service logs
kubectl logs -f deployment/veyra-auth -n veyra

# Test authentication
curl -X POST https://api.veyra.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Check JWT configuration
kubectl get secret veyra-secrets -n veyra -o yaml
```

**Solutions:**
```bash
# Restart auth service
kubectl rollout restart deployment/veyra-auth -n veyra

# Update JWT secret
kubectl create secret generic veyra-secrets \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  --dry-run=client -o yaml | kubectl apply -f -

# Check database user permissions
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "\du"
```

### Background Job Issues

#### Problem: Jobs Not Processing
**Diagnosis:**
```bash
# Check worker pods
kubectl get pods -n veyra | grep worker

# Check job queue
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli llen veyra:queue

# Check worker logs
kubectl logs -f deployment/veyra-worker -n veyra
```

**Solutions:**
```bash
# Scale workers
kubectl scale deployment veyra-worker --replicas=5 -n veyra

# Clear stuck jobs
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli del veyra:queue

# Restart workers
kubectl rollout restart deployment/veyra-worker -n veyra
```

---

## 🎨 Frontend Issues

### Build and Deployment Problems

#### Problem: Frontend Not Loading
**Diagnosis:**
```bash
# Check frontend pods
kubectl get pods -n veyra | grep veyra-frontend

# Check frontend service
kubectl get svc veyra-frontend -n veyra

# Check frontend logs
kubectl logs -f deployment/veyra-frontend -n veyra

# Test frontend endpoint
curl -v https://app.veyra.com
```

**Solutions:**
```bash
# Rebuild frontend
docker build -t veyra/frontend:latest frontend/
docker push veyra/frontend:latest

# Redeploy frontend
kubectl rollout restart deployment/veyra-frontend -n veyra

# Check static assets
kubectl exec -it deployment/veyra-frontend -n veyra -- ls -la /app/build
```

#### Problem: CSS/JS Not Loading
**Diagnosis:**
```bash
# Check asset paths
kubectl exec -it deployment/veyra-frontend -n veyra -- find /app/build -name "*.css" -o -name "*.js"

# Check CDN configuration
curl -I https://app.veyra.com/static/main.css

# Check browser console for errors
# (Manual check in browser)
```

**Solutions:**
```bash
# Clear CDN cache
# (CloudFlare dashboard or API)

# Rebuild with correct paths
cd frontend/
npm run build
docker build -t veyra/frontend:latest .
docker push veyra/frontend:latest

# Update ingress for static assets
kubectl patch ingress veyra-ingress -n veyra -p '{"spec":{"rules":[{"host":"app.veyra.com","http":{"paths":[{"path":"/static","pathType":"Prefix","backend":{"service":{"name":"veyra-frontend","port":{"number":3000}}}}]}}]}}'
```

### Performance Issues

#### Problem: Slow Page Load
**Diagnosis:**
```bash
# Check frontend pod resources
kubectl top pods -n veyra | grep veyra-frontend

# Check network latency
ping app.veyra.com

# Analyze bundle size
kubectl exec -it deployment/veyra-frontend -n veyra -- du -sh /app/build/static/
```

**Solutions:**
```bash
# Enable gzip compression
kubectl patch deployment veyra-frontend -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-frontend","env":[{"name":"ENABLE_GZIP","value":"true"}]}]}}}}'

# Add CDN for static assets
# (Update DNS and CDN configuration)

# Optimize images
# (Run image optimization pipeline)
```

---

## 📱 Mobile App Problems

### Build Issues

#### Problem: Flutter Build Fails
**Diagnosis:**
```bash
# Check Flutter environment
flutter doctor -v

# Check dependencies
cd mobile/veyra_app/
flutter pub deps

# Check build logs
flutter build apk --verbose
```

**Solutions:**
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter build apk

# Update dependencies
flutter pub upgrade

# Check platform-specific issues
flutter build apk --debug
flutter build ios --debug
```

#### Problem: Native Build Errors
**Diagnosis:**
```bash
# Check Android build
cd mobile/veyra_app/android/
./gradlew build

# Check iOS build
cd mobile/veyra_app/ios/
xcodebuild -project Veyra.xcodeproj -scheme Veyra build
```

**Solutions:**
```bash
# Update Gradle
cd mobile/veyra_app/android/
./gradlew wrapper --gradle-version=7.4.2

# Clean Xcode build
cd mobile/veyra_app/ios/
xcodebuild clean -project Veyra.xcodeproj -scheme Veyra

# Check certificates
# (Manual check in Xcode)
```

### Runtime Issues

#### Problem: App Crashes on Startup
**Diagnosis:**
```bash
# Check device logs
adb logcat | grep Veyra

# Check iOS logs
idevicesyslog | grep Veyra

# Check crash reports
# (Manual check in device settings)
```

**Solutions:**
```bash
# Debug with Flutter
flutter run --debug

# Check for memory issues
flutter run --profile
# Monitor memory usage in Android Studio

# Update dependencies
flutter pub upgrade
```

---

## 🗄️ Database Issues

### Connection Problems

#### Problem: Database Unreachable
**Diagnosis:**
```bash
# Check database pod
kubectl get pods -n veyra | grep database

# Check database service
kubectl get svc veyra-database -n veyra

# Test connection
kubectl exec -it veyra-api-<pod> -n veyra -- nc -zv veyra-database 5432
```

**Solutions:**
```bash
# Restart database
kubectl rollout restart statefulset/veyra-database -n veyra

# Check PVC status
kubectl get pvc -n veyra

# Verify network policies
kubectl get networkpolicy -n veyra | grep database
```

#### Problem: Slow Queries
**Diagnosis:**
```bash
# Check slow query log
kubectl exec -it veyra-database-0 -n veyra -- tail -f /var/log/postgresql/postgresql.log

# Check active connections
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "SELECT * FROM pg_stat_activity;"

# Check query performance
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**Solutions:**
```bash
# Restart database
kubectl rollout restart statefulset/veyra-database -n veyra

# Optimize queries
# (Review and optimize slow queries)

# Add indexes
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "CREATE INDEX CONCURRENTLY idx_table_column ON table(column);"

# Increase resources
kubectl patch statefulset veyra-database -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"postgres","resources":{"limits":{"memory":"8Gi","cpu":"4000m"}}}]}}}}'
```

### Backup and Recovery

#### Problem: Backup Failed
**Diagnosis:**
```bash
# Check backup job
kubectl get jobs -n veyra | grep backup

# Check backup logs
kubectl logs job/veyra-backup -n veyra

# Check backup storage
kubectl get pvc -n veyra | grep backup
```

**Solutions:**
```bash
# Manually trigger backup
kubectl create job --from=cronjob/veyra-backup manual-backup-$(date +%s) -n veyra

# Check backup script
kubectl exec -it veyra-database-0 -n veyra -- pg_dump --help

# Verify backup storage
kubectl exec -it veyra-backup-<pod> -n veyra -- ls -la /backup/
```

---

## 🌐 API Problems

### Rate Limiting Issues

#### Problem: API Rate Limited
**Diagnosis:**
```bash
# Check rate limiting headers
curl -I https://api.veyra.com/api/v1/portfolio

# Check Redis rate limiting
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli get rate_limit:user123

# Check HPA status
kubectl get hpa -n veyra
```

**Solutions:**
```bash
# Clear rate limit cache
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli del rate_limit:user123

# Scale up API
kubectl scale deployment veyra-api --replicas=10 -n veyra

# Adjust rate limits
kubectl patch configmap api-config -n veyra -p '{"data":{"rate_limit":"1000"}}'
```

### CORS Issues

#### Problem: CORS Errors
**Diagnosis:**
```bash
# Check CORS headers
curl -H "Origin: https://app.veyra.com" -H "Access-Control-Request-Method: GET" -X OPTIONS https://api.veyra.com/api/v1/portfolio -v

# Check ingress configuration
kubectl get ingress veyra-ingress -n veyra -o yaml | grep cors
```

**Solutions:**
```bash
# Update CORS configuration
kubectl patch ingress veyra-ingress -n veyra -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/cors-allow-origin":"*"}}}'

# Restart ingress controller
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
```

---

## 🏗️ Infrastructure Issues

### Kubernetes Cluster Issues

#### Problem: Cluster Not Responding
**Diagnosis:**
```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system
```

**Solutions:**
```bash
# Restart cluster components
# (Varies by cloud provider)

# Check cloud provider console
# (AWS, GCP, Azure console)

# Contact cloud support
# (If cluster-level issue)
```

#### Problem: Pod Scheduling Issues
**Diagnosis:**
```bash
# Check pending pods
kubectl get pods -n veyra | grep Pending

# Check node resources
kubectl describe nodes

# Check resource quotas
kubectl get resourcequota -n veyra
```

**Solutions:**
```bash
# Add more nodes
# (Cloud provider console or kubectl)

# Increase resource limits
kubectl patch resourcequota veyra-resource-quota -n veyra -p '{"spec":{"hard":{"requests.cpu":"20","requests.memory":"40Gi"}}}'

# Delete stuck pods
kubectl delete pod <pod-name> -n veyra --force --grace-period=0
```

### Storage Issues

#### Problem: PVC Not Binding
**Diagnosis:**
```bash
# Check PVC status
kubectl get pvc -n veyra

# Check storage classes
kubectl get storageclass

# Check PV status
kubectl get pv
```

**Solutions:**
```bash
# Create new storage class
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp2-encrypted
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  encrypted: "true"
EOF

# Delete and recreate PVC
kubectl delete pvc <pvc-name> -n veyra
# Apply PVC manifest again
```

---

## ⚡ Performance Issues

### High Latency

#### Problem: Slow API Response
**Diagnosis:**
```bash
# Measure response time
time curl https://api.veyra.com/health

# Check pod resource usage
kubectl top pods -n veyra

# Check network latency
kubectl exec -it veyra-api-<pod> -n veyra -- ping veyra-database
```

**Solutions:**
```bash
# Scale up services
kubectl scale deployment veyra-api --replicas=10 -n veyra

# Add caching
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","env":[{"name":"ENABLE_CACHE","value":"true"}]}]}}}}'

# Optimize database queries
# (Review and optimize slow queries)
```

### Memory Leaks

#### Problem: Memory Usage Increasing
**Diagnosis:**
```bash
# Monitor memory usage
watch -n 5 'kubectl top pods -n veyra | grep veyra-api'

# Check for memory leaks in logs
kubectl logs -f deployment/veyra-api -n veyra | grep -i memory

# Check garbage collection
kubectl exec -it veyra-api-<pod> -n veyra -- jstat -gc 1
```

**Solutions:**
```bash
# Restart services
kubectl rollout restart deployment/veyra-api -n veyra

# Increase memory limits
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","resources":{"limits":{"memory":"2Gi"}}}]}}}}'

# Enable heap profiling
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","env":[{"name":"JAVA_OPTS","value":"-XX:+HeapDumpOnOutOfMemoryError"}]}]}}}}'
```

---

## 🔒 Security Issues

### Authentication Problems

#### Problem: Invalid JWT Tokens
**Diagnosis:**
```bash
# Check JWT secret
kubectl get secret veyra-secrets -n veyra -o yaml

# Test token validation
curl -H "Authorization: Bearer <token>" https://api.veyra.com/api/v1/portfolio

# Check token expiration
echo "<token>" | cut -d. -f2 | base64 -d | jq '.exp'
```

**Solutions:**
```bash
# Rotate JWT secret
kubectl create secret generic veyra-secrets \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart auth service
kubectl rollout restart deployment/veyra-auth -n veyra
```

### SSL/TLS Issues

#### Problem: Certificate Expired
**Diagnosis:**
```bash
# Check certificate expiration
openssl s_client -connect api.veyra.com:443 -servername api.veyra.com 2>/dev/null | openssl x509 -noout -dates

# Check cert-manager
kubectl get certificates -n veyra

# Check ingress TLS
kubectl describe ingress veyra-ingress -n veyra
```

**Solutions:**
```bash
# Renew certificate
kubectl certificate renew veyra-tls -n veyra

# Restart ingress
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx

# Force certificate renewal
kubectl delete certificate veyra-tls -n veyra
kubectl apply -f deploy/k8s/ingress.yaml
```

---

## 🔗 Integration Issues

### External API Problems

#### Problem: Third-party API Down
**Diagnosis:**
```bash
# Test external API
curl -v https://api.thirdparty.com/health

# Check API configuration
kubectl get configmap external-apis -n veyra -o yaml

# Check API logs
kubectl logs -f deployment/veyra-api -n veyra | grep thirdparty
```

**Solutions:**
```bash
# Update API endpoints
kubectl patch configmap external-apis -n veyra -p '{"data":{"thirdparty_url":"https://backup-api.com"}}'

# Implement circuit breaker
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","env":[{"name":"CIRCUIT_BREAKER_ENABLED","value":"true"}]}]}}}}'

# Monitor external API status
# (Set up external monitoring)
```

### Message Queue Issues

#### Problem: Messages Not Processing
**Diagnosis:**
```bash
# Check queue length
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli llen veyra:queue

# Check consumer groups
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli xinfo groups veyra:queue

# Check worker logs
kubectl logs -f deployment/veyra-worker -n veyra
```

**Solutions:**
```bash
# Scale workers
kubectl scale deployment veyra-worker --replicas=5 -n veyra

# Clear stuck messages
kubectl exec -it veyra-redis-0 -n veyra -- redis-cli del veyra:queue

# Restart workers
kubectl rollout restart deployment/veyra-worker -n veyra
```

---

## 🚨 Emergency Procedures

### Complete System Outage

#### Step 1: Assess Impact
```bash
# Check cluster status
kubectl cluster-info

# Check all pods
kubectl get pods --all-namespaces

# Check external connectivity
ping 8.8.8.8
```

#### Step 2: Restore Critical Services
```bash
# Restart core services
kubectl rollout restart deployment/veyra-api -n veyra
kubectl rollout restart deployment/veyra-frontend -n veyra
kubectl rollout restart statefulset/veyra-database -n veyra

# Check health endpoints
curl https://api.veyra.com/health
curl https://app.veyra.com/health
```

#### Step 3: Scale Up Resources
```bash
# Scale up all services
kubectl scale deployment veyra-api --replicas=10 -n veyra
kubectl scale deployment veyra-frontend --replicas=5 -n veyra
kubectl scale deployment veyra-worker --replicas=10 -n veyra
```

#### Step 4: Monitor Recovery
```bash
# Watch pod status
watch -n 5 'kubectl get pods -n veyra'

# Monitor logs
kubectl logs -f deployment/veyra-api -n veyra

# Check health status
watch -n 10 'curl -s https://api.veyra.com/health | jq .status'
```

### Database Corruption

#### Step 1: Stop Application
```bash
# Scale down API to prevent writes
kubectl scale deployment veyra-api --replicas=0 -n veyra
```

#### Step 2: Restore from Backup
```bash
# Create restore job
kubectl create job --from=cronjob/veyra-restore restore-$(date +%s) -n veyra

# Monitor restore progress
kubectl logs -f job/restore-<id> -n veyra
```

#### Step 3: Verify Data Integrity
```bash
# Check database
kubectl exec -it veyra-database-0 -n veyra -- psql -U veyra -d veyra -c "SELECT COUNT(*) FROM users;"

# Run data validation
kubectl exec -it veyra-api-<pod> -n veyra -- python validate_data.py
```

#### Step 4: Restore Application
```bash
# Scale up API
kubectl scale deployment veyra-api --replicas=3 -n veyra

# Monitor health
curl https://api.veyra.com/health
```

---

## 🛠️ Debugging Tools

### Kubernetes Debugging

#### Port Forwarding
```bash
# Forward API port
kubectl port-forward svc/veyra-api 8000:8000 -n veyra

# Forward database port
kubectl port-forward svc/veyra-database 5432:5432 -n veyra

# Forward Redis port
kubectl port-forward svc/veyra-redis 6379:6379 -n veyra
```

#### Exec into Containers
```bash
# Debug API container
kubectl exec -it deployment/veyra-api -n veyra -- /bin/bash

# Debug database container
kubectl exec -it veyra-database-0 -n veyra -- /bin/bash

# Debug Redis container
kubectl exec -it veyra-redis-0 -n veyra -- /bin/sh
```

### Application Debugging

#### Enable Debug Mode
```bash
# Set debug environment variables
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","env":[{"name":"DEBUG","value":"true"},{"name":"LOG_LEVEL","value":"DEBUG"}]}]}}}}'

# Restart to apply
kubectl rollout restart deployment/veyra-api -n veyra
```

#### Profiling
```bash
# Enable profiling
kubectl patch deployment veyra-api -n veyra -p '{"spec":{"template":{"spec":{"containers":[{"name":"veyra-api","env":[{"name":"ENABLE_PROFILING","value":"true"}]}]}}}}'

# Access profiling endpoint
kubectl port-forward svc/veyra-api 8000:8000 -n veyra
curl http://localhost:8000/debug/pprof/
```

### Network Debugging

#### Test Connectivity
```bash
# Test pod-to-pod connectivity
kubectl exec -it veyra-api-<pod> -n veyra -- ping veyra-database.veyra.svc.cluster.local

# Test external connectivity
kubectl exec -it veyra-api-<pod> -n veyra -- curl -I https://api.thirdparty.com

# Test DNS resolution
kubectl exec -it veyra-api-<pod> -n veyra -- nslookup veyra-database.veyra.svc.cluster.local
```

#### Network Policies Debug
```bash
# Check current policies
kubectl get networkpolicy -n veyra -o yaml

# Test policy effects
kubectl run test-pod --image=alpine --rm -it --restart=Never -- ping veyra-database.veyra.svc.cluster.local
```

---

## 📞 Contact Support

### Internal Support

#### Development Team
- **Slack:** #veyra-dev
- **Email:** dev@veyra.com
- **On-call:** +1-555-DEV-HELP

#### DevOps Team
- **Slack:** #veyra-ops
- **Email:** ops@veyra.com
- **On-call:** +1-555-OPS-HELP

### External Support

#### Cloud Providers
- **AWS:** +1-800-AWS-HELP
- **GCP:** +1-855-833-3977
- **Azure:** +1-800-642-7676

#### Third-party Services
- **Database Support:** db-support@veyra.com
- **CDN Support:** cdn-support@veyra.com
- **Monitoring Support:** monitoring@veyra.com

### Escalation Procedures

#### Level 1: Basic Issues
- Response time: 1 hour
- Resolution time: 4 hours
- Contact: Development team

#### Level 2: System Issues
- Response time: 30 minutes
- Resolution time: 2 hours
- Contact: DevOps team

#### Level 3: Critical Outages
- Response time: 15 minutes
- Resolution time: 1 hour
- Contact: On-call engineer + management

### Documentation Updates

This troubleshooting guide should be updated when:
- New services are added
- Common issues are identified
- Procedures change
- New debugging tools are added

To update this guide:
1. Edit the source file in `docs/troubleshooting/`
2. Submit a pull request
3. Tag relevant team members for review
4. Update version number
5. Notify team of changes

---

## 📚 Additional Resources

### Useful Links
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/)

### Training Materials
- [Kubernetes Troubleshooting Course](https://kubernetes.io/docs/tasks/debug-application-cluster/)
- [Docker Debugging Guide](https://docs.docker.com/config/daemon/)
- [Monitoring Best Practices](https://prometheus.io/docs/practices/)

### Tools and Utilities
- **kubectl-debug**: Debug running pods
- **stern**: Multi-pod log tailing
- **kubectx/kubens**: Context switching
- **helm**: Package management
- **istioctl**: Service mesh debugging

---

**Remember:** This guide is a living document. Always verify procedures in a non-production environment before applying to production systems.

**Last reviewed:** May 12, 2026  
**Next review:** June 12, 2026
