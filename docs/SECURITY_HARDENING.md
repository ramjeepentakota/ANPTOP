# ANPTOP Security Hardening Checklist

## 1. Operating System Hardening

### Linux Servers

- [ ] **Kernel Parameters**
  - [ ] Disable IP forwarding (`net.ipv4.ip_forward = 0`)
  - [ ] Disable ICMP redirects (`net.ipv4.conf.all.accept_redirects = 0`)
  - [ ] Enable SYN flood protection (`net.ipv4.tcp_syncookies = 1`)
  - [ ] Disable source routing (`net.ipv4.conf.all.accept_source_route = 0`)
  - [ ] Enable reverse path filtering (`net.ipv4.conf.all.rp_filter = 1`)

- [ ] **System Security**
  - [ ] Enable automatic security updates
  - [ ] Remove unnecessary packages and services
  - [ ] Configure `/etc/login.defs` for password policies
  - [ ] Set umask to 027 or stricter
  - [ ] Disable root SSH login
  - [ ] Configure SSH to use only strong ciphers

- [ ] **User Management**
  - [ ] Enforce strong password policy (min 12 chars, complexity)
  - [ ] Set password expiration (90 days max)
  - [ ] Enable account lockout after 5 failed attempts
  - [ ] Remove orphaned accounts and groups
  - [ ] Implement sudo for privileged access

### Configuration Example (sysctl.conf)
```bash
# Network hardening
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Memory protection
kernel.randomize_va_space = 2
kernel.exec-shield = 1
```

---

## 2. Docker Container Hardening

### Image Security

- [ ] **Base Image**
  - [ ] Use official, verified images only
  - [ ] Pin base image version (not `latest`)
  - [ ] Use minimal base images (alpine, slim)
  - [ ] Regularly scan images for vulnerabilities

- [ ] **Image Build**
  - [ ] Use multi-stage builds to reduce size
  - [ ] Don't include unnecessary packages
  - [ ] Use specific package versions
  - [ ] Remove temporary files in build
  - [ ] Don't run as root user

### Dockerfile Best Practices
```dockerfile
# Use non-root user
FROM python:3.11-slim

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /app
COPY --chown=appuser:appgroup . .

USER appuser

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

CMD ["python", "app.py"]
```

### Docker Runtime Security

- [ ] **Container Configuration**
  - [ ] Enable Docker Content Trust
  - [ ] Use `--read-only` flag for root filesystem
  - [ ] Disable privileged mode
  - [ ] Set resource limits (memory, CPU)
  - [ ] Use `--cap-drop=ALL` and add only required capabilities
  - [ ] Enable seccomp profile
  - [ ] Enable AppArmor profile

### Docker Daemon Configuration (daemon.json)
```json
{
  "icc": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userns-remap": "default",
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp-profile.json"
}
```

---

## 3. Database Security

### PostgreSQL

- [ ] **Authentication**
  - [ ] Use scram-sha-256 authentication
  - [ ] Enforce password complexity
  - [ ] Set password encryption
  - [ ] Configure connection limits per user
  - [ ] Use SSL/TLS for all connections

- [ ] **Access Control**
  - [ ] Restrict listen_addresses
  - [ ] Configure pg_hba.conf properly
  - [ ] Remove public schema privileges
  - [ ] Grant least privilege to users
  - [ ] Enable audit logging

### PostgreSQL Configuration (postgresql.conf)
```conf
# Connection
listen_addresses = 'localhost'
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'

# Authentication
password_encryption = scram-sha-256
scram_auth_enabled = on

# Resource Limits
max_connections = 100
shared_buffers = 256MB
work_mem = 4MB

# Logging
log_connections = on
log_disconnections = on
log_statement = 'ddl'
log_duration = on
log_hostname = on
```

### pg_hba.conf Example
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
host    anptop          anptop_app       10.0.0.0/8              scram-sha-256
```

---

## 4. Redis Security

- [ ] **Authentication**
  - [ ] Set strong password (>= 32 characters)
  - [ ] Disable dangerous commands (FLUSHDB, FLUSHALL, CONFIG, KEYS)
  - [ ] Rename dangerous commands

- [ ] **Network**
  - [ ] Bind to localhost only
  - [ ] Enable TLS encryption
  - [ ] Configure firewall rules

### Redis Configuration
```
# Security
requirepass <strong_random_password>
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command KEYS "ANPTOP_KEYS"

# Network
bind 127.0.0.1
port 6379
protected-mode yes

# TLS
tls-port 6380
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru
```

---

## 5. API Security

### Authentication & Authorization

- [ ] **JWT Configuration**
  - [ ] Use strong JWT secret (>= 64 characters)
  - [ ] Set appropriate token expiration (15-60 min)
  - [ ] Implement token refresh mechanism
  - [ ] Store tokens securely (HttpOnly cookies)
  - [ ] Implement token blacklisting

- [ ] **Access Control**
  - [ ] Implement role-based access control (RBAC)
  - [ ] Enforce least privilege
  - [ ] Validate all input data
  - [ ] Implement rate limiting

### JWT Configuration (backend/app/core/security.py)
```python
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', generate_strong_key(64))
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Token claims
TOKEN_TYPE_CLAIMS = {
    "sub": "user_id",
    "type": "access",
    "role": "user_role",
    "permissions": ["list", "of", "permissions"]
}
```

### Rate Limiting Configuration
```python
# In-memory rate limiter (use Redis for distributed)
RATE_LIMIT = {
    "requests": 100,
    "window": 60,  # seconds
    "burst": 20
}
```

---

## 6. Network Security

### Firewall Configuration

- [ ] **UFW (Ubuntu)**
  ```bash
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow ssh
  ufw allow http
  ufw allow https
  ufw enable
  ```

- [ ] **iptables Rules**
  ```bash
  # Drop invalid packets
  -A INPUT -m state --state INVALID -j DROP
  
  # Allow established connections
  -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
  
  # Allow SSH (rate limited)
  -A INPUT -p tcp --dport 22 -m limit --limit 25/min --limit-burst 100 -j ACCEPT
  
  # Drop port scans
  -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
  -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
  ```

### Nginx Security Headers
```nginx
server {
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## 7. Monitoring & Alerting

### Audit Logging

- [ ] **Application Audit**
  - [ ] Log all authentication events (success/failure)
  - [ ] Log authorization decisions
  - [ ] Log sensitive data access
  - [ ] Log configuration changes
  - [ ] Log data exports

### Audit Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "authentication",
  "user_id": 1,
  "username": "admin",
  "ip_address": "192.168.1.10",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "failure_reason": null,
  "details": {
    "method": "password",
    "mfa_used": true
  }
}
```

### Log Retention
- [ ] Retain audit logs for minimum 1 year
- [ ] Store logs in immutable storage
- [ ] Implement log forwarding to SIEM
- [ ] Set up real-time alerting on suspicious activity

---

## 8. Data Protection

### Encryption

- [ ] **Data at Rest**
  - [ ] Encrypt PostgreSQL data directory
  - [ ] Encrypt Redis data with password
  - [ ] Encrypt backup files
  - [ ] Use LUKS for disk encryption

- [ ] **Data in Transit**
  - [ ] Use TLS 1.2+ for all connections
  - [ ] Enforce HTTPS everywhere
  - [ ] Use TLS certificates from trusted CA
  - [ ] Implement certificate rotation

### Backup Encryption
```bash
# Encrypt backup with GPG
gpg --symmetric --cipher-algo AES256 backup.sql
```

---

## 9. Vulnerability Management

### Regular Security Tasks

- [ ] **Daily**
  - [ ] Review audit logs
  - [ ] Check failed authentication attempts
  - [ ] Monitor alert notifications

- [ ] **Weekly**
  - [ ] Scan Docker images for vulnerabilities
  - [ ] Review user access and permissions
  - [ ] Check certificate expiration

- [ ] **Monthly**
  - [ ] Penetration testing
  - [ ] Security awareness training
  - [ ] Review and update security policies

- [ ] **Quarterly**
  - [ ] Full security audit
  - [ ] Incident response drill
  - [ ] Third-party security assessment

---

## 10. Incident Response

### Preparation

- [ ] **Documentation**
  - [ ] Document incident response procedures
  - [ ] Create runbooks for common incidents
  - [ ] Maintain contact list for stakeholders

- [ ] **Tools**
  - [ ] Preserve evidence collection tools
  - [ ] Set up forensic analysis environment
  - [ ] Prepare communication templates

### Response Procedures
1. **Detection** → 2. **Analysis** → 3. **Containment** → 4. **Eradication** → 5. **Recovery** → 6. **Lessons Learned**

---

## Compliance Checklist

| Standard | Control | Status |
|----------|---------|--------|
| CIS Benchmarks | Docker/Linux | [ ] |
| OWASP Top 10 | Application | [ ] |
| NIST 800-53 | Security Controls | [ ] |
| ISO 27001 | ISMS | [ ] |
| SOC 2 | Trust Criteria | [ ] |

---

## References

- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
