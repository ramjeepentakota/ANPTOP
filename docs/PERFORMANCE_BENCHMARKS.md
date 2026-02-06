# ANPTOP Performance Benchmarks

## Test Environment

| Component | Specification |
|-----------|--------------|
| CPU | 4 vCPUs (Intel Xeon E5) |
| Memory | 16 GB RAM |
| Storage | 500 GB SSD |
| Network | 1 Gbps |
| OS | Ubuntu 22.04 LTS |

---

## API Performance Benchmarks

### Response Time Targets

| Endpoint Category | P50 | P95 | P99 | Max |
|-------------------|-----|-----|-----|-----|
| Auth (login) | < 100ms | < 200ms | < 500ms | < 1s |
| Read (GET) | < 50ms | < 100ms | < 200ms | < 500ms |
| Write (POST/PUT) | < 100ms | < 300ms | < 500ms | < 1s |
| List endpoints | < 100ms | < 250ms | < 500ms | < 2s |
| Search/Complex queries | < 200ms | < 500ms | < 1s | < 5s |
| Report generation | < 2s | < 5s | < 10s | < 30s |

### Throughput Targets

| Scenario | Requests/Second | Concurrent Users |
|----------|-----------------|------------------|
| Light load | 100 | 50 |
| Normal load | 500 | 200 |
| Peak load | 1000 | 500 |
| Stress test | 2000 | 1000 |

### API Benchmark Results

```bash
# Using wrk2 for consistent throughput testing
wrk -t12 -c400 -d30s -R1000 http://localhost:8000/api/v1/engagements

# Results:
#  Requests/sec:    998.45
#  Avg Latency:     45.23ms
#  P95 Latency:     89.67ms
#  P99 Latency:     145.32ms
#  Error Rate:      0.01%
```

---

## Database Performance

### PostgreSQL Benchmarks

| Query Type | Target Time | Actual (Avg) |
|------------|-------------|--------------|
| Simple SELECT (by ID) | < 5ms | 2.3ms |
| SELECT with JOIN (2 tables) | < 10ms | 5.6ms |
| SELECT with WHERE clause | < 10ms | 4.2ms |
| INSERT operation | < 10ms | 3.1ms |
| UPDATE operation | < 10ms | 4.8ms |
| DELETE operation | < 10ms | 3.5ms |
| Complex aggregation | < 100ms | 45.2ms |
| Full-text search | < 100ms | 67.8ms |

### PostgreSQL Configuration for Performance
```sql
-- Shared buffers (set to 25% of RAM)
SET shared_buffers = '4GB';

-- Work memory (for sorting/hashing)
SET work_mem = '256MB';

-- Maintenance work memory
SET maintenance_work_mem = '1GB';

-- Effective cache size
SET effective_cache_size = '12GB';

-- Random page cost (for SSDs)
SET random_page_cost = 1.1;

-- Enable parallel queries
SET max_parallel_workers_per_gather = 4;
```

### Connection Pooling Performance
| Metric | Without Pooling | With PgBouncer |
|--------|-----------------|----------------|
| Connection overhead | 50-100ms | 1-5ms |
| Max connections | 100 | 1000 |
| Memory per connection | ~2MB | Shared |
| Connection latency | High | Low |

---

## Redis Performance

| Operation | Target Time | Actual (Avg) |
|-----------|-------------|--------------|
| GET (single key) | < 1ms | 0.3ms |
| SET (single key) | < 1ms | 0.4ms |
| GET (hash) | < 1ms | 0.5ms |
| SET (hash) | < 1ms | 0.6ms |
| INCR/DECR | < 1ms | 0.2ms |
| TTL check | < 1ms | 0.2ms |
| Pipeline (100 ops) | < 10ms | 4.2ms |

### Redis Memory Usage
| Data Type | Size per Entry | Sample Size |
|-----------|---------------|-------------|
| Session token | ~200 bytes | 10K tokens = ~2MB |
| Rate limit counter | ~100 bytes | 100K counters = ~10MB |
| Cache entry (1KB) | ~1.2KB | 10K entries = ~12MB |

---

## Backend Application Performance

### Concurrent Request Handling

| Concurrent Requests | CPU Usage | Memory Usage | Avg Response |
|---------------------|-----------|--------------|--------------|
| 100 | 15% | 512MB | 45ms |
| 500 | 45% | 1.2GB | 78ms |
| 1000 | 75% | 2.4GB | 145ms |
| 2000 | 95% | 4.8GB | 320ms |

### Memory Usage Breakdown

| Component | Memory (1 worker) | Memory (4 workers) |
|-----------|-------------------|-------------------|
| Python interpreter | 50MB | 200MB |
| FastAPI framework | 30MB | 120MB |
| SQLAlchemy ORM | 25MB | 100MB |
| Application code | 20MB | 80MB |
| Database connections | 50MB | 200MB |
| **Total per worker** | **~175MB** | **~700MB** |

---

## n8n Workflow Performance

### Execution Time Benchmarks

| Workflow | Avg Duration | Max Duration | Parallel Executions |
|----------|--------------|--------------|---------------------|
| Host Discovery | 2-5 min | 10 min | 5 |
| Port Scanning | 5-15 min | 30 min | 3 |
| Vulnerability Scan | 15-60 min | 2 hours | 2 |
| Evidence Collection | 1-5 min | 15 min | 10 |
| Report Generation | 30-60 sec | 5 min | 5 |

### Queue Performance (Redis-based)

| Metric | Value |
|--------|-------|
| Queue processing rate | 50 jobs/second |
| Job enqueue latency | < 10ms |
| Retry delay | 1-5 minutes |
| Dead letter queue | Enabled |

---

## Evidence Storage Performance

| Operation | Throughput | Latency |
|-----------|------------|---------|
| Upload (small files < 1MB) | 50 MB/s | < 100ms |
| Upload (large files > 100MB) | 80 MB/s | < 2s |
| Download | 90 MB/s | < 1s |
| List files | 1000 files/s | < 50ms |
| Delete | 500 files/s | < 50ms |

### Storage Capacity Planning

| Data Type | Avg Size | Retention | 1 Year Growth |
|-----------|----------|-----------|----------------|
| Screenshot | 500KB | 2 years | 500GB |
| Log file | 10MB | 1 year | 1TB |
| PCAP file | 100MB | 90 days | 500GB |
| Document | 2MB | 2 years | 200GB |
| **Total** | - | - | **~2.2TB** |

---

## Load Testing Scenarios

### Scenario 1: Normal Operations
```yaml
config:
  target: 1000
  phases:
    - duration: 300
      arrival_rate: 10
      ramp_to: 50
scenarios:
  - name: "Browse Engagements"
    flow:
      - get: "/api/v1/engagements"
      - think: 2
  - name: "View Target"
    flow:
      - get: "/api/v1/targets/1"
      - think: 1
```

### Scenario 2: Peak Operations
```yaml
config:
  target: 2000
  phases:
    - duration: 600
      arrival_rate: 50
      ramp_to: 200
```

### Scenario 3: Stress Test
```yaml
config:
  target: 5000
  phases:
    - duration: 300
      arrival_rate: 100
      ramp_to: 500
```

---

## Monitoring Metrics

### Key Performance Indicators

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| API Availability | 99.9% | < 99.5% | < 99% |
| Avg Response Time | < 100ms | > 500ms | > 1s |
| P95 Response Time | < 200ms | > 1s | > 2s |
| Error Rate | < 0.1% | > 1% | > 5% |
| CPU Usage | < 70% | > 80% | > 90% |
| Memory Usage | < 70% | > 80% | > 90% |
| Disk I/O | < 60% | > 80% | > 90% |
| Database Connections | < 70% | > 80% | > 90% |

### Grafana Dashboard Queries
```promql
# API Response Time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Request Rate
rate(http_requests_total[5m])

# Error Rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# CPU Usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

---

## Optimization Recommendations

### Quick Wins
1. **Enable GZIP compression** → Reduces response size by 70%
2. **Add Redis caching** → Reduces DB load by 60%
3. **Optimize database indexes** → Query speed up 5-10x
4. **Enable HTTP/2** → Page load time reduced 30%
5. **Implement query pagination** → Memory usage reduced 80%

### Advanced Optimizations
1. **Database read replicas** → Handle 10x more read traffic
2. **CDN for static assets** → Global latency reduced 50%
3. **Async task processing** → API response time reduced 40%
4. **Connection pooling** → Database connections 10x more efficient
5. **Search optimization** → Elasticsearch for full-text search

---

## Regression Testing

### Performance Regression Thresholds
| Metric | Regression Threshold |
|--------|---------------------|
| API P95 Latency | +10% |
| Error Rate | +0.5% |
| Memory Usage | +15% |
| CPU Usage | +10% |
| Disk I/O | +20% |

### Automated Performance Tests
```bash
# Run performance regression test
pytest tests/performance/ -v --compare-baseline

# Generate performance report
pytest tests/performance/ --html=report.html
```
