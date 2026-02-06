# ANPTOP - Architecture & Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [High-Level Architecture](#high-level-architecture)
3. [Component-Level Architecture](#component-level-architecture)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Security Guardrails](#security-guardrails)
6. [Approval Workflow Design](#approval-workflow-design)
7. [User Roles & RBAC Model](#user-roles--rbac-model)
8. [MVP vs Enterprise Feature Separation](#mvp-vs-enterprise-feature-separation)

---

## 1. Executive Summary

ANPTOP (Automated Network Penetration Testing Orchestration Platform) is an enterprise-grade, semi-automated network penetration testing orchestration platform designed for security teams, red teams, and compliance auditors.

### Key Objectives
- **Semi-automated network pentesting** with human-in-the-loop approvals
- **Dynamic port-based scanning** and intelligent enumeration
- **OpenVAS-based vulnerability assessment** with CVE correlation
- **Approval-gated exploitation** with full audit trail
- **Post-exploitation and lateral movement** capabilities
- **Automated reporting** (Executive & Technical)
- **MITRE ATT&CK & NIST SP 800-115 compliance**

### Core Philosophy
- **Security First**: Every action requires approval; no autonomous exploitation
- **Audit Ready**: Complete traceability for compliance and legal requirements
- **Scalable**: Docker-first design supporting MVP to Enterprise deployments
- **Modular**: Loose coupling between components for easy updates

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANPTOP - High-Level Architecture                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        PRESENTATION LAYER                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │   │
│  │  │   React Admin    │  │   React Analyst  │  │   React Manager  │    │   │
│  │  │   Dashboard      │  │   Console        │  │   Portal         │    │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      API GATEWAY / LOAD BALANCER                      │   │
│  │                    Nginx / Traefik (TLS Termination)                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      APPLICATION LAYER                                 │   │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐ │   │
│  │  │  FastAPI Backend   │  │   n8n Orchestrator  │  │   React Frontend │ │   │
│  │  │  (Port 8000)       │  │   (Port 5678)      │  │   (Port 3000)    │ │   │
│  │  └────────────────────┘  └────────────────────┘  └──────────────────┘ │   │
│  │                                                                              │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐ │   │
│  │  │  PostgreSQL        │  │   Redis            │  │   Object Storage │ │   │
│  │  │  (Port 5432)       │  │   (Port 6379)      │  │   (MinIO/S3)     │ │   │
│  │  └────────────────────┘  └────────────────────┘  └──────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     SECURITY TOOLS LAYER                              │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │   │
│  │  │   OpenVAS   │ │  Metasploit │ │  BloodHound │ │   Custom Tools  │  │   │
│  │  │   Scanner   │ │    RPC      │ │   Ingestor  │ │   (RustScan,   │  │   │
│  │  │             │ │             │ │             │ │   Nmap, etc.)   │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     EXTERNAL SERVICES                                 │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐   │   │
│  │  │   NVD API      │ │   VirusTotal   │ │   Email/SMS Alerts     │   │   │
│  │  │   (CVE Data)   │ │   (IOCs)       │ │   (Notifications)      │   │   │
│  │  └────────────────┘ └────────────────┘ └────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Each layer is independent and replaceable
2. **Defense in Depth**: Multiple security controls at each layer
3. **Zero Trust**: All internal and external communications authenticated
4. **Immutable Evidence**: All evidence cryptographically hashed and timestamped
5. **Approval Gates**: Human-in-the-loop for all offensive operations

---

## 3. Component-Level Architecture

### 3.1 Frontend Components

```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Layout/          # Main layout (Sidebar, Header)
│   │   ├── Forms/           # Form components with validation
│   │   ├── Tables/          # Data tables with sorting/filtering
│   │   ├── Charts/          # Visualization components
│   │   ├── Modals/          # Approval dialogs
│   │   └── Alerts/          # Notifications and warnings
│   ├── pages/               # Page components
│   │   ├── Login/           # Authentication
│   │   ├── Dashboard/       # Overview and metrics
│   │   ├── Engagements/     # Engagement management
│   │   ├── Scans/           # Scan progress and results
│   │   ├── Vulnerabilities/ # Vulnerability dashboard
│   │   ├── Approvals/       # Exploitation approval screens
│   │   ├── Evidence/        # Evidence browser
│   │   ├── Reports/         # Report generation/download
│   │   └── Audit/           # Audit log viewer
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client services
│   ├── store/               # State management (Zustand/Redux)
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Utility functions
└── public/                  # Static assets
```

### 3.2 Backend Components

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── v1/
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── engagements.py
│   │   │   ├── scans.py
│   │   │   ├── vulnerabilities.py
│   │   │   ├── approvals.py
│   │   │   ├── evidence.py
│   │   │   ├── reports.py
│   │   │   └── audit.py
│   │   └── deps.py         # Dependencies (auth, DB, etc.)
│   ├── core/                # Core configuration
│   │   ├── config.py       # Settings management
│   │   ├── security.py     # Security utilities
│   │   └── logging.py      # Logging configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── engagement.py
│   │   ├── host.py
│   │   ├── port.py
│   │   ├── service.py
│   │   ├── vulnerability.py
│   │   ├── exploit.py
│   │   ├── evidence.py
│   │   └── audit.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── engagement.py
│   │   ├── scan.py
│   │   └── ...
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── engagement_service.py
│   │   ├── scan_service.py
│   │   ├── n8n_service.py
│   │   ├── approval_service.py
│   │   └── report_service.py
│   ├── db/                  # Database
│   │   ├── session.py      # DB sessions
│   │   └── init_db.py      # DB initialization
│   └── main.py             # FastAPI application
├── migrations/             # Alembic migrations
└── tests/                  # Test suite
```

### 3.3 n8n Workflow Components

```
n8n/
├── workflows/
│   ├── 01_target_intake.yml
│   ├── 02_host_discovery.yml
│   ├── 03_port_scanning.yml
│   ├── 04_service_detection.yml
│   ├── 05_enumeration.yml
│   ├── 06_vulnerability_assessment.yml
│   ├── 07_cve_correlation.yml
│   ├── 08_exploitation_approval.yml
│   ├── 09_exploitation_execution.yml
│   ├── 10_post_exploitation.yml
│   ├── 11_lateral_movement.yml
│   ├── 12_evidence_collection.yml
│   └── 13_reporting.yml
├── credentials/
│   ├── openvas_creds.json
│   ├── metasploit_creds.json
│   └── smb_creds.json
└── n8n.conf
```

### 3.4 Docker Architecture

```
docker/
├── Dockerfile.frontend
├── Dockerfile.backend
├── Dockerfile.n8n
├── Dockerfile.openvas
├── Dockerfile.redis
├── Dockerfile.worker
├── docker-compose.yml
├── docker-compose.enterprise.yml
└── nginx/
    ├── Dockerfile
    ├── nginx.conf
    └── templates/
```

---

## 4. Data Flow Diagrams

### 4.1 Target Intake Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │  FastAPI │     │  n8n     │     │  Redis   │     │PostgreSQL│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │ POST /engagement│               │                │                │
     │───────────────>│                │                │                │
     │                │ Trigger        │                │                │
     │                │ Workflow       │                │                │
     │                │───────────────>│                │                │
     │                │                │                │                │
     │                │                │ Store Job      │                │
     │                │                │───────────────>│                │
     │                │                │                │                │
     │                │                │ Save           │                │
     │                │                │ Engagement     │                │
     │                │                │────────────────│────────────────│
     │                │                │                │                │
     │  Response      │                │                │                │
     │<───────────────│                │                │                │
     │  (Engagement ID)               │                │                │
```

### 4.2 Scanning Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  n8n     │     │  Masscan │     │  Nmap    │     │  Redis   │     │PostgreSQL│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │ Execute        │                │                │                │
     │ Masscan        │                │                │                │
     │─────────────────────────────────>│                │                │
     │                │                │                │                │
     │                │ Port Results   │                │                │
     │<─────────────────────────────────│                │                │
     │                │                │                │                │
     │ Dynamic NSE    │                │                │                │
     │ Script Select  │                │                │                │
     │                │                │                │                │
     │─────────────────────────────────>│                │                │
     │                │                │ Service/Version│                │
     │                │                │ Detection      │                │
     │<─────────────────────────────────│                │                │
     │                │                │                │                │
     │ Update         │                │                │                │
     │ Database       │                │                │────────────────│
     │───────────────────────────────────────────────────────────────────────>
     │                │                │                │                │
     │ Notify         │                │                │                │
     │ Frontend       │                │                │                │
     │───────────────────────────────────────────────────────────────────────>
```

### 4.3 Exploitation Approval Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  n8n     │     │  FastAPI │     │ Frontend │     │  User    │     │PostgreSQL│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │ Detect         │                │                │                │
     │ Exploit        │                │                │                │
     │ Opportunity    │                │                │                │
     │                │                │                │                │
     │ Pause &        │ Create         │                │                │
     │ Create         │ Approval       │                │                │
     │ Approval       │ Request        │                │                │
     │────────────────├───────────────>│                │                │
     │                │                │                │                │
     │                │                │ Notify User    │                │
     │                │                │───────────────>│                │
     │                │                │                │                │
     │                │                │  User Reviews  │                │
     │                │                │  & Approves    │                │
     │                │                │                │                │
     │                │                │ POST /approve  │                │
     │                │                │───────────────>│                │
     │                │                │                │                │
     │                │ Update         │                │                │
     │                │ Approval       │                │                │
     │                │ Status         │                │                │
     │                │<───────────────│                │                │
     │                │                │                │                │
     │ Trigger        │ Notify         │                │                │
     │ Exploit        │ n8n            │                │                │
     │<───────────────│<───────────────│                │                │
     │                │                │                │                │
     │ Execute        │                │                │                │
     │ Exploit        │                │                │                │
     │───────────────────────────────────────────────────────────────────────>
     │                │                │                │                │
     │ Log            │                │                │                │
     │ Execution      │                │                │                │
     │───────────────────────────────────────────────────────────────────────>
```

---

## 5. Security Guardrails

### 5.1 Network Security

```yaml
network_security:
  segmentation:
    - Management network isolated from tool networks
    - Tool networks isolated from production
    - All traffic encrypted (TLS 1.3)
    
  firewalls:
    - Inbound: Only 443 (frontend), 8443 (API)
    - Outbound: Required egress to NVD API, email
    - Internal: All components communicate via internal network
    
  monitoring:
    - All network traffic logged
    - Intrusion detection on tool networks
    - Anomaly detection for scan patterns
```

### 5.2 Authentication & Authorization

```yaml
auth_security:
  mfa:
    required: true
    methods:
      - TOTP
      - Hardware keys (YubiKey)
      - SMS (fallback)
      
  jwt:
    algorithm: RS256
    expiry: 15 minutes
    refresh_token: 8 hours
    
  password_policy:
    min_length: 16
    complexity: required
    rotation: 90 days
    history: 12
```

### 5.3 Secrets Management

```yaml
secrets_management:
  vault: HashiCorp Vault / AWS Secrets Manager
  
  rotation:
    api_keys: 30 days
    database: 90 days
    tool_credentials: 30 days
    
  encryption:
    at_rest: AES-256-GCM
    in_transit: TLS 1.3
```

### 5.4 Exploitation Safeguards

```yaml
exploitation_safeguards:
  approval_required:
    - All exploitation attempts
    - All post-exploitation actions
    - All lateral movement
    - All credential harvesting
    
  scope_enforcement:
    - Target whitelist validation
    - Target blacklist validation
    - Network boundary checks
    - DNS resolution validation
    
  kill_switches:
    - Global emergency stop
    - Engagement-level pause
    - Individual action cancel
    - Automatic timeout (24 hours)
    
  evidence_protection:
    - All commands logged
    - All outputs captured
    - All files hashed (SHA-256, SHA-512)
    - Chain of custody maintained
```

---

## 6. Approval Workflow Design

### 6.1 Approval States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Approval State Machine                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│      ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐          │
│      │ PENDING │────>│ APPROVED│────>│ EXECUTING│────>│ COMPLETED│         │
│      └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘          │
│           │               │               │               │               │
│           │               │               │               │               │
│           ▼               ▼               ▼               ▼               │
│      ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐          │
│      │ REJECTED│     │ EXPIRED │     │ FAILED  │     │ CANCELLED│         │
│      └─────────┘     └─────────┘     └─────────┘     └─────────┘          │
│                                                                              │
│                                                                              │
│  State Transitions:                                                           │
│  ─────────────────                                                            │
│  PENDING → APPROVED: Manual approval by authorized user                       │
│  PENDING → REJECTED: Manual rejection by authorized user                       │
│  PENDING → EXPIRED: Timeout (default 24 hours)                                │
│  APPROVED → EXECUTING: n8n starts execution                                    │
│  EXECUTING → COMPLETED: Action finished successfully                          │
│  EXECUTING → FAILED: Action encountered error                                  │
│  EXECUTING → CANCELLED: Manual cancellation                                    │
│  COMPLETED → CANCELLED: Post-execution cancellation (rare)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Approval Escalation

```yaml
approval_escalation:
  levels:
    - role: ANALYST
      timeout: 4 hours
      escalate_to: SENIOR_ANALYST
      
    - role: SENIOR_ANALYST
      timeout: 8 hours
      escalate_to: TEAM_LEAD
      
    - role: TEAM_LEAD
      timeout: 12 hours
      escalate_to: CISO
      
    - role: CISO
      timeout: 24 hours
      escalate_to: MANUAL_OVERRIDE
      
  notifications:
    channels:
      - email
      - slack
      - teams
      - sms (critical)
      
    timing:
      initial: immediate
      reminder_1: 1 hour before timeout
      reminder_2: 30 minutes before timeout
      escalation: on timeout
```

### 6.3 Multi-Person Control

```yaml
multi_person_control:
  enabled: true
  
  requirements:
    exploitation:
      min_approvers: 2
      roles_required:
        - SENIOR_ANALYST
        - TEAM_LEAD
        
    critical_actions:
      min_approvers: 2
      roles_required:
        - TEAM_LEAD
        - CISO
        
  approval_types:
    single: Standard single-approver
    dual: Two different people required
    majority: Majority of team leads
    unanimous: All designated approvers
```

---

## 7. User Roles & RBAC Model

### 7.1 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ANPTOP Role Hierarchy                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌───────────┐                                   │
│                              │   CISO    │                                   │
│                              │ (Level 5) │                                   │
│                              └─────┬─────┘                                   │
│                                    │                                         │
│                          ┌─────────┴─────────┐                               │
│                          │    TEAM_LEAD      │                               │
│                          │    (Level 4)      │                               │
│                          └─────────┬─────────┘                               │
│                                    │                                         │
│              ┌─────────────────────┼─────────────────────┐                   │
│              │                     │                     │                   │
│     ┌────────┴────────┐   ┌───────┴───────┐   ┌────────┴────────┐          │
│     │ SENIOR_ANALYST  │   │  ENGAGEMENT   │   │     AUDITOR     │          │
│     │    (Level 3)    │   │   MANAGER     │   │    (Level 3)    │          │
│     └────────┬────────┘   │   (Level 3)   │   └─────────────────┘          │
│              │             └───────┬───────┘                               │
│              │                     │                                         │
│     ┌────────┴────────┐             │                                         │
│     │    ANALYST      │   ┌─────────┴─────────┐                              │
│     │    (Level 2)    │   │   REPORT_VIEWER   │                              │
│     └────────┬────────┘   │    (Level 1)      │                              │
│              │            └─────────────────────┘                              │
│              │                                                                │
│     ┌────────┴────────┐                                                       │
│     │    VIEWER       │                                                      │
│     │    (Level 1)    │                                                      │
│     └─────────────────┘                                                       │
│                                                                              │
│  Level 1: Read-only access                                                   │
│  Level 2: Standard operational access                                        │
│  Level 3: Senior operational access                                          │
│  Level 4: Management & supervision                                           │
│  Level 5: Executive & emergency access                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Detailed Role Permissions

#### VIEWER (Level 1)
```yaml
viewer:
  description: Read-only access for stakeholders
  permissions:
    - view_dashboard
    - view_engagements (own)
    - view_reports (own)
    - view_vulnerabilities (own)
    - export_data
    
  restrictions:
    - no_modification
    - no_execution
    - no_approval
    - no_audit_access
```

#### ANALYST (Level 2)
```yaml
analyst:
  description: Standard pentester operations
  inherits: VIEWER
  permissions:
    - create_engagement
    - edit_engagement (own)
    - start_scan
    - view_all_hosts
    - view_all_ports
    - view_all_services
    - create_enumeration
    - view_evidence
    - export_evidence
    
  restrictions:
    - cannot_approve_exploitation
    - cannot_start_exploitation
    - cannot_approve_lateral_movement
    - scope_restricted_to_own_engagements
```

#### SENIOR_ANALYST (Level 3)
```yaml
senior_analyst:
  description: Senior pentester with exploitation approval
  inherits: ANALYST
  permissions:
    - approve_standard_exploitation
    - approve_post_exploitation
    - view_all_engagements
    - access_all_evidence
    - create_custom_workflows
    - modify_scan_parameters
    - export_full_reports
    
  restrictions:
    - cannot_approve_critical_exploitation
    - cannot_modify_roles
    - cannot_access_audit_logs
```

#### ENGAGEMENT_MANAGER (Level 3)
```yaml
engagement_manager:
  description: Manages engagement scope and reporting
  inherits: ANALYST
  permissions:
    - manage_all_engagements
    - modify_scope
    - approve_report_generation
    - view_team_performance
    - manage_templates
    
  restrictions:
    - cannot_execute_scans
    - cannot_approve_exploitation
    - cannot_access_security_tools
```

#### AUDITOR (Level 3)
```yaml
auditor:
  description: Compliance and audit review
  permissions:
    - view_audit_logs
    - view_all_engagements
    - view_all_evidence
    - export_audit_reports
    - view_compliance_mappings
    
  restrictions:
    - no_modification
    - no_execution
    - no_approval
```

#### TEAM_LEAD (Level 4)
```yaml
team_lead:
  description: Team supervision and critical approvals
  inherits: SENIOR_ANALYST
  permissions:
    - approve_all_exploitation
    - approve_critical_actions
    - manage_team_members
    - view_team_audit_logs
    - override_engagement_scope
    - emergency_stop
    
  restrictions:
    - cannot_modify_own_permissions
    - cannot_access_system_config
```

#### CISO (Level 5)
```yaml
ciso:
  description: Executive oversight and emergency access
  inherits: TEAM_LEAD
  permissions:
    - full_system_access
    - approve_any_action
    - bypass_approval_gates (with justification)
    - modify_role_permissions
    - system_configuration
    - view_financial_reports
    - manage_api_keys
    
  restrictions:
    - must_log_all_bypasses
    - requires_justification_for_bypass
```

### 7.3 RBAC Implementation

```python
# FastAPI Dependencies for RBAC
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, Role
from app.core.security import get_current_user

# Role hierarchy levels
ROLE_LEVELS = {
    "VIEWER": 1,
    "ANALYST": 2,
    "SENIOR_ANALYST": 3,
    "ENGAGEMENT_MANAGER": 3,
    "AUDITOR": 3,
    "TEAM_LEAD": 4,
    "CISO": 5,
}

def require_role(required_roles: List[str]):
    """Dependency to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_min_level(min_level: int):
    """Dependency to require minimum role level"""
    def level_checker(current_user: User = Depends(get_current_user)):
        if ROLE_LEVELS.get(current_user.role.name, 0) < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Minimum role level {min_level} required"
            )
        return current_user
    return level_checker

# Example usage in API endpoints
@app.post("/engagements/{id}/scan")
async def start_scan(
    engagement_id: int,
    current_user: User = Depends(require_min_level(2)),  # Analyst or above
    db: Session = Depends(get_db)
):
    # Only analysts and above can start scans
    pass

@app.post("/exploitation/{id}/approve")
async def approve_exploitation(
    exploitation_id: int,
    current_user: User = Depends(require_role(["SENIOR_ANALYST", "TEAM_LEAD", "CISO"])),
    db: Session = Depends(get_db)
):
    # Only senior analysts, team leads, and CISO can approve exploitation
    pass
```

---

## 8. MVP vs Enterprise Feature Separation

### 8.1 MVP Features (v1.0)

#### Core Capabilities
```yaml
mvp:
  scanning:
    tools:
      - masscan (fast port discovery)
      - nmap (service detection)
      - basic NSE scripts
      
    features:
      - single target range
      - basic port scan
      - service version detection
      - host discovery
      
  vulnerability_assessment:
    tools:
      - OpenVAS (Greenbone CE)
      
    features:
      - full scan
      - basic CVE reporting
      
  exploitation:
    approval_gates: true
    tools:
      - Metasploit RPC (limited)
      - Basic exploit modules
      
    features:
      - manual exploitation
      - basic session handling
      
  reporting:
    formats:
      - HTML
      - basic PDF
      
    content:
      - scope summary
      - vulnerability list
      - basic remediation
      
  frontend:
    pages:
      - login
      - dashboard
      - engagements
      - scan results
      - vulnerabilities
      - basic reports
      
  backend:
    features:
      - JWT authentication
      - basic RBAC (3 roles)
      - engagement management
      - evidence storage
      
  deployment:
    docker_compose:
      - backend
      - frontend
      - n8n
      - postgres
      - redis
      - openvas
      
  limitations:
    - single engagement at a time
    - max 1000 targets
    - no lateral movement
    - no post-exploitation
    - no BloodHound integration
    - basic audit logging
```

### 8.2 Enterprise Features (v2.0+)

#### Advanced Scanning
```yaml
enterprise:
  scanning:
    tools:
      - rustscan (ultra-fast)
      - unicornscan
      - custom port scanners
      
    features:
      - distributed scanning
      - multi-target parallel
      - intelligent scan prioritization
      - adaptive scanning algorithms
      
  vulnerability_assessment:
    tools:
      - OpenVAS (distributed)
      - Nessus integration
      - Nuclei (custom templates)
      
    features:
      - real-time correlation
      - false positive reduction
      - intelligent prioritization
      - integration with threat intel
      
  exploitation:
    tools:
      - Metasploit RPC (full)
      - PowerShell Empire integration
      - Covenant C2 integration
      - CrackMapExec
      - BloodHound
      - Custom exploit frameworks
      
    features:
      - automated exploitation chains
      - credential replay
      - kerberoasting
      - lateral movement automation
      - privilege escalation
      - data exfiltration simulation
      
  post_exploitation:
    modules:
      - session management
      - persistence mechanisms
      - credential harvesting
      - data discovery
      - pivot identification
      
  reporting:
    formats:
      - HTML
      - PDF (professional templates)
      - Word
      - Excel (data exports)
      
    features:
      - executive summaries
      - technical deep-dives
      - MITRE ATT&CK mapping
      - NIST SP 800-115 alignment
      - compliance reports (PCI-DSS, HIPAA, SOC2)
      - custom branding
      - multi-language support
      
  frontend:
    pages:
      - all MVP pages
      - compliance dashboard
      - threat intelligence
      - team collaboration
      - advanced analytics
      - custom dashboards
      - API documentation
      
    features:
      - real-time updates
      - advanced visualizations
      - workflow builder
      - custom integrations
      
  backend:
    features:
      - advanced RBAC (custom roles)
      - SSO/SAML integration
      - LDAP/Active Directory
      - audit trail
      - multi-tenancy
      - API rate limiting
      - webhook integrations
      - advanced scheduling
      
  deployment:
    kubernetes:
      - horizontal scaling
      - load balancing
      - auto-scaling
      - high availability
      
    cloud:
      - AWS deployment
      - Azure deployment
      - GCP deployment
      
    security:
      - Vault integration
      - WAF integration
      - SIEM integration
      - EDR integration
      
  integrations:
    - JIRA
    - ServiceNow
    - Slack
    - Microsoft Teams
    - Splunk
    - Elastic
    - QRadar
```

### 8.3 Migration Path

```yaml
migration_strategy:
  v1_to_v2:
    - database migrations provided
    - configuration migration scripts
    - backward compatibility maintained
    
  v2_features:
    - enterprise edition license required
    - optional modules can be enabled
    - gradual rollout supported
    
  upgrade_path:
    1. v1.0 MVP deployment
    2. v1.5 feature additions
    3. v2.0 enterprise migration
    4. v2.x continuous improvements
```

---

## Appendix A: Compliance Mapping

### MITRE ATT&CK Alignment
```yaml
mitre_attack:
  reconnaissance:
    - T1595: Search Open Website/Domain
    - T1592: Gather Victim Host Information
    
  resource_development:
    - T1583: Acquire Infrastructure
    
  initial_access:
    - T1190: Exploit Public-Facing Application
    - T1133: External Remote Services
    
  execution:
    - T1059: Command and Scripting Interpreter
    
  persistence:
    - T1547: Boot or Logon Autostart Execution
    
  privilege_escalation:
    - T1068: Exploitation for Privilege Escalation
    
  defense_evasion:
    - T1070: Indicator Removal
    
  credential_access:
    - T1003: OS Credential Dumping
    
  discovery:
    - T1046: Network Service Discovery
    
  lateral_movement:
    - T1021: Remote Services
    
  collection:
    - T1213: Data from Information Repositories
```

### NIST SP 800-115 Alignment
```yaml
nist_sp_800_115:
  planning:
    - 3.1: Pentesting methodology defined
    - 3.2: Rules of engagement documented
    - 3.3: Scope defined
    
  reconnaissance:
    - 4.1: Passive reconnaissance
    - 4.2: Active reconnaissance
    
  scanning:
    - 4.3: Network discovery
    - 4.4: Port/service identification
    - 4.5: Vulnerability identification
    
  exploitation:
    - 4.6: Penetration attempts
    - 4.7: Privilege escalation
    - 4.8: Lateral movement
    
  post_exploitation:
    - 4.9: Data exfiltration simulation
    - 4.10: Persistence mechanisms
    
  reporting:
    - 5.1: Findings documentation
    - 5.2: Remediation recommendations
    - 5.3: Executive summary
```

---

## Appendix B: Threat Model Summary

### Assets
- Evidence data (highest sensitivity)
- Credentials and secrets
- Scan results and findings
- User authentication data
- System configurations

### Threats
- Unauthorized access to evidence
- Manipulation of scan results
- Privilege escalation
- Data exfiltration
- Service disruption

### Mitigation
- Zero-trust architecture
- Cryptographic evidence protection
- Comprehensive audit logging
- Approval-based operations
- Network segmentation

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
