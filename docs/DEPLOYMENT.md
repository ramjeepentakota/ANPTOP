# ANPTOP Deployment Guide

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 vCPUs | 4+ vCPUs |
| RAM | 4 GB | 16 GB |
| Storage | 50 GB | 200+ GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Required Software

- Docker Engine 20.10+
- Docker Compose v2.0+
- kubectl (for Kubernetes)
- Helm 3.0+ (optional)

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Development)

#### 1. Clone Repository
```bash
git clone https://github.com/anptop/anptop.git
cd anptop
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Start Services
```bash
docker-compose up -d
```

#### 4. Verify Installation
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
```

#### 5. Access Application
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000/api/v1
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

---

### Option 2: Kubernetes Deployment

#### 1. Create Namespace
```bash
kubectl create namespace anptop
```

#### 2. Create Secrets
```bash
kubectl apply -f k8s/secrets.yaml
```

#### 3. Deploy Components
```bash
# Deploy namespace and base resources
kubectl apply -f k8s/namespace.yaml

# Deploy database and cache
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Deploy application
kubectl apply -f k8s/backend-deployment.yaml

# Deploy workflow engine
kubectl apply -f k8s/n8n-deployment.yaml

# Deploy monitoring
kubectl apply -f k8s/monitoring-deployment.yaml
```

#### 4. Configure Ingress
```bash
# Edit ingress.yaml with your domain
kubectl apply -f k8s/ingress.yaml
```

#### 5. Verify Deployment
```bash
kubectl get pods -n anptop
kubectl get svc -n anptop
```

---

## Environment Variables

### Core Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Application secret key | Auto-generated |
| `DEBUG` | Debug mode | `false` |
| `ENVIRONMENT` | Deployment environment | `production` |
| `ALLOWED_HOSTS` | CORS allowed hosts | `*` |

### Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL user | `anptop` |
| `POSTGRES_PASSWORD` | PostgreSQL password | Required |
| `POSTGRES_DB` | Database name | `anptop` |

### Redis Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | Required |

### JWT Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS512` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |

### n8n Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `N8N_BASIC_AUTH_ACTIVE` | Enable auth | `true` |
| `N8N_WEBHOOK_URL` | Webhook URL | Required |
| `N8N_ENCRYPTION_KEY` | Encryption key | Required |

---

## Initial Setup

### 1. Create Admin User
```bash
# First login via API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Import Initial Data
```bash
# Initialize database
docker-compose exec backend python -m app.db.init_db

# Import n8n workflows
docker-compose exec backend python -m scripts.import_workflows
```

### 3. Configure n8n
1. Access n8n at http://localhost:5678
2. Login with credentials from secrets
3. Import workflows from `n8n/workflows/`
4. Activate workflows

### 4. Setup Monitoring
1. Access Grafana at http://localhost:3001
2. Login with admin credentials
3. Import dashboard from `docker/grafana/dashboards/`
4. Configure alerts in Prometheus

---

## Backup & Recovery

### Automated Backups
```bash
# Schedule daily backups
0 2 * * * docker-compose -f /path/to/anptop/docker-compose.yml exec -T backend python /app/scripts/backup.py backup --type full
```

### Manual Backup
```bash
# Full backup
docker-compose exec backend python /app/scripts/backup.py backup --type full

# PostgreSQL only
docker-compose exec -T postgres pg_dump -U anptop anptop > backup.sql

# Redis
docker-compose exec redis redis-cli BGSAVE
docker-compose cp redis:/data/appendonly.aof ./redis_backup.aof
```

### Restore from Backup
```bash
# Full restore
docker-compose exec backend python /app/scripts/backup.py restore /backups/anptop_manifest_20240115.json

# PostgreSQL restore
docker-compose exec -T postgres psql -U anptop -d anptop < backup.sql
```

---

## Scaling

### Horizontal Scaling (Kubernetes)
```bash
# Scale backend
kubectl scale deployment anptop-backend --replicas=3 -n anptop

# Scale with autoscaling
kubectl autoscale deployment anptop-backend -n anptop --min=2 --max=10 --cpu-percent=70
```

### Database Scaling
```bash
# Increase PostgreSQL resources
kubectl patch deployment anptop-postgres -n anptop -p '{"spec":{"resources":{"limits":{"memory":"2Gi","cpu":"2000m"}}}}'
```

---

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec backend python -c "from app.db.session import engine; engine.execute('SELECT 1')"

# Redis health
docker-compose exec redis redis-cli ping
```

### Metrics
```bash
# API metrics
curl http://localhost:8000/metrics

# Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

#### 2. Database Connection Failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://anptop:pass@localhost:5432/anptop'); engine.connect()"
```

#### 3. n8n Webhooks Not Working
```bash
# Check n8n logs
docker-compose logs n8n

# Verify webhook URL configuration
# Must match the external URL
```

#### 4. High Memory Usage
```bash
# Check container stats
docker stats

# Solutions:
# - Increase memory limits
# - Enable Redis caching
# - Scale horizontally
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
docker-compose up -d backend
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up audit logging
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up backup rotation
- [ ] Enable intrusion detection
- [ ] Regular security updates

---

## Upgrades

### Minor Updates
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d
```

### Major Updates
```bash
# Backup first
docker-compose exec backend python /app/scripts/backup.py backup --type full

# Pull new images
docker-compose pull

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Restart
docker-compose up -d
```
