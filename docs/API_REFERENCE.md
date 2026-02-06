# ANPTOP API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require JWT authentication except for `/auth/login` and `/health`.

Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### POST /auth/login
Authenticate user and get JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/register
Register new user (admin only).

**Request:**
```json
{
  "username": "new_user",
  "email": "new_user@example.com",
  "password": "secure_password",
  "role": "analyst"
}
```

**Response:**
```json
{
  "id": 3,
  "username": "new_user",
  "email": "new_user@example.com",
  "role": "analyst",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### POST /auth/refresh
Refresh access token.

**Headers:** Authorization: Bearer <expired_token>

**Response:**
```json
{
  "access_token": "new_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Engagements Endpoints

### GET /engagements
List all engagements with filtering.

**Query Parameters:**
- `status` (optional): Filter by status
- `target_id` (optional): Filter by target
- `page` (optional): Page number
- `per_page` (optional): Items per page

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Q1 2024 Network Assessment",
      "description": "Quarterly network security assessment",
      "target_id": 1,
      "status": "active",
      "workflow_stage": "reconnaissance",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "created_by": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### POST /engagements
Create new engagement.

**Request:**
```json
{
  "name": "New Penetration Test",
  "description": "Description of the engagement",
  "target_id": 1,
  "scope": "192.168.1.0/24",
  "rules_of_engagement": "Allow scope defined in project",
  "start_date": "2024-02-01",
  "end_date": "2024-02-15"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Penetration Test",
  "status": "pending",
  "workflow_stage": "planning",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### GET /engagements/{id}
Get engagement details.

**Response:**
```json
{
  "id": 1,
  "name": "Q1 2024 Network Assessment",
  "targets": [
    {
      "id": 1,
      "ip_address": "192.168.1.100",
      "hostname": "server01.corp.local",
      "os": "Linux Ubuntu 22.04",
      "services": [
        {"port": 22, "name": "ssh", "version": "OpenSSH 8.9"}
      ]
    }
  ],
  "vulnerabilities": [
    {
      "id": 5,
      "name": "SSH Weak Cipher",
      "severity": "medium",
      "cvss_score": 5.3,
      "status": "open"
    }
  ],
  "evidence_count": 12,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /engagements/{id}
Update engagement.

### DELETE /engagements/{id}
Delete engagement (soft delete).

---

## Targets Endpoints

### GET /targets
List all targets.

**Query Parameters:**
- `type` (optional): Filter by type (host, domain, network, container)
- `os_family` (optional): Filter by OS family
- `page`, `per_page`

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "type": "host",
      "ip_address": "192.168.1.100",
      "hostname": "server01.corp.local",
      "os": "Linux Ubuntu 22.04",
      "os_family": "linux",
      "mac_address": "00:1A:2B:3C:4D:5E",
      "is_active": true,
      "last_scanned": "2024-01-15T10:00:00Z",
      "tags": ["production", "webserver"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /targets
Add new target.

**Request:**
```json
{
  "type": "host",
  "ip_address": "192.168.1.101",
  "hostname": "db01.corp.local",
  "os": "Windows Server 2022",
  "os_family": "windows",
  "mac_address": "00:1A:2B:3C:4D:6F",
  "description": "Database Server",
  "tags": ["production", "database"]
}
```

### GET /targets/{id}/services
Get services discovered on target.

**Response:**
```json
{
  "target_id": 1,
  "services": [
    {
      "id": 10,
      "port": 22,
      "protocol": "tcp",
      "name": "ssh",
      "version": "OpenSSH 8.9",
      "banner": "SSH-2.0-OpenSSH_8.9",
      "product": "OpenSSH",
      "cves": [
        {
          "cve_id": "CVE-2023-48788",
          "cvss_score": 5.3,
          "severity": "medium"
        }
      ]
    },
    {
      "id": 11,
      "port": 443,
      "protocol": "tcp",
      "name": "https",
      "product": "nginx",
      "version": "1.24.0"
    }
  ]
}
```

---

## Vulnerabilities Endpoints

### GET /vulnerabilities
List vulnerabilities.

**Query Parameters:**
- `severity` (optional): critical, high, medium, low, info
- `status` (optional): open, confirmed, false_positive, remediated
- `engagement_id` (optional): Filter by engagement
- `page`, `per_page`

**Response:**
```json
{
  "items": [
    {
      "id": 5,
      "name": "SSH Weak Cipher Enabled",
      "description": "SSH server accepts weak ciphers",
      "severity": "medium",
      "cvss_score": 5.3,
      "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
      "cve_id": null,
      "cwe_id": "CWE-326",
      "status": "open",
      "target_id": 1,
      "engagement_id": 1,
      "tool_source": "nmap",
      "remediation": "Disable weak ciphers in sshd_config",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /vulnerabilities
Create vulnerability finding.

**Request:**
```json
{
  "name": "SQL Injection in Login",
  "description": "Application is vulnerable to SQL injection",
  "severity": "high",
  "cvss_score": 8.6,
  "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L",
  "target_id": 2,
  "engagement_id": 1,
  "remediation": "Use parameterized queries",
  "evidence_refs": ["evidence_001", "evidence_002"]
}
```

### PUT /vulnerabilities/{id}
Update vulnerability status/remediation.

**Request:**
```json
{
  "status": "confirmed",
  "remediation": "Implemented input validation",
  "assigned_to": 2
}
```

### GET /vulnerabilities/stats
Get vulnerability statistics.

**Response:**
```json
{
  "total": 45,
  "by_severity": {
    "critical": 2,
    "high": 8,
    "medium": 20,
    "low": 12,
    "info": 3
  },
  "by_status": {
    "open": 25,
    "confirmed": 10,
    "false_positive": 5,
    "remediated": 5
  },
  "trend": {
    "last_week_new": 12,
    "last_week_closed": 5
  }
}
```

---

## Evidence Endpoints

### POST /evidence/upload
Upload evidence file.

**Content-Type:** multipart/form-data

**Body:**
- `file`: File to upload
- `engagement_id`: int
- `target_id`: int (optional)
- `vulnerability_id`: int (optional)
- `description`: str
- `evidence_type`: screenshot, log, pcap, document, other

**Response:**
```json
{
  "id": 100,
  "filename": "screenshot_001.png",
  "original_name": "vuln_screenshot.png",
  "mime_type": "image/png",
  "size_bytes": 245678,
  "storage_path": "/evidence/engagement_1/vuln_5/screenshot_001.png",
  "sha256_hash": "a1b2c3d4...",
  "uploaded_by": 1,
  "engagement_id": 1,
  "vulnerability_id": 5,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### GET /evidence/{id}
Get evidence metadata.

**Response:**
```json
{
  "id": 100,
  "filename": "screenshot_001.png",
  "original_name": "vuln_screenshot.png",
  "mime_type": "image/png",
  "size_bytes": 245678,
  "description": "Screenshot showing SQL error message",
  "evidence_type": "screenshot",
  "sha256_hash": "a1b2c3d4...",
  "uploaded_by": 1,
  "engagement_id": 1,
  "vulnerability_id": 5,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### GET /evidence/{id}/download
Download evidence file.

### DELETE /evidence/{id}
Delete evidence.

---

## Workflows Endpoints

### GET /workflows
List workflows.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Network Reconnaissance",
      "description": "Automated network discovery workflow",
      "category": "reconnaissance",
      "trigger_type": "manual",
      "is_active": true,
      "n8n_workflow_id": "abc123",
      "engagement_types": ["network_assessment"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /workflows/{id}/execute
Execute workflow.

**Request:**
```json
{
  "engagement_id": 1,
  "target_scope": ["192.168.1.0/24"],
  "options": {
    "timeout": 3600,
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "execution_id": "exec_abc123",
  "status": "started",
  "n8n_execution_id": "n8n_xyz789",
  "started_at": "2024-01-15T10:00:00Z"
}
```

### GET /workflows/executions/{id}
Get execution status.

**Response:**
```json
{
  "execution_id": "exec_abc123",
  "status": "completed",
  "workflow_id": 1,
  "result_summary": {
    "hosts_discovered": 50,
    "ports_scanned": 1000,
    "vulnerabilities_found": 15
  },
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T11:30:00Z",
  "duration_seconds": 5400
}
```

---

## Approvals Endpoints

### GET /approvals
List pending approvals.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "request_type": "high_risk_tool",
      "tool_name": "Nessus",
      "target_scope": ["192.168.1.0/24"],
      "requested_by": 2,
      "requested_at": "2024-01-15T10:00:00Z",
      "status": "pending",
      "justification": "Full network vulnerability scan authorized by client",
      "expires_at": "2024-01-16T10:00:00Z"
    }
  ]
}
```

### POST /approvals
Request approval for high-risk activity.

**Request:**
```json
{
  "request_type": "high_risk_tool",
  "tool_name": "Nmap",
  "target_scope": ["10.0.0.0/8"],
  "justification": "Network discovery required for engagement",
  "estimated_duration": 3600
}
```

### PUT /approvals/{id}
Approve or reject request.

**Request:**
```json
{
  "status": "approved",
  "approver_notes": "Approved per engagement scope",
  "approval_duration_hours": 24
}
```

---

## Reports Endpoints

### GET /reports/templates
List report templates.

### POST /reports/generate
Generate engagement report.

**Request:**
```json
{
  "engagement_id": 1,
  "template": "executive_summary",
  "include_vulnerabilities": true,
  "include_evidence": true,
  "include_remediation": true,
  "format": "pdf"
}
```

**Response:**
```json
{
  "report_id": 1,
  "status": "generating",
  "download_url": null
}
```

### GET /reports/{id}/download
Download generated report.

---

## Users Endpoints

### GET /users/me
Get current user profile.

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@anptop.local",
  "role": "admin",
  "permissions": ["read", "write", "approve", "admin"],
  "engagements": [],
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:00:00Z"
}
```

### PUT /users/me
Update current user profile.

### PUT /users/{id}
Update user (admin only).

---

## Audit Endpoints

### GET /audit/logs
Get audit logs.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `action_type` (optional): Filter by action
- `resource_type` (optional): Filter by resource
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date
- `page`, `per_page`

**Response:**
```json
{
  "items": [
    {
      "id": 1000,
      "user_id": 1,
      "username": "admin",
      "action": "vulnerability_update",
      "resource_type": "vulnerability",
      "resource_id": 5,
      "old_value": {"status": "open"},
      "new_value": {"status": "confirmed"},
      "ip_address": "192.168.1.10",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 100
}
```

---

## Health Endpoints

### GET /health
System health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "n8n": "healthy"
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
