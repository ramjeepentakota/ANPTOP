# ANPTOP - Automated Network Penetration Testing Orchestration Platform

**Version**: 2.0.0  
**Build Date**: 2024-02-06  
**Purpose**: Semi-automated network penetration testing orchestration platform for fintech red teaming

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ANPTOP Platform                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         React Frontend (UI)                           │  │
│  │     Dashboard │ Engagements │ Reports │ Settings │ Audit Logs        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    ▲                                        │
│                                    │ REST API                              │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Backend (Python)                          │  │
│  │   Auth │ RBAC │ Engagements │ Targets │ Workflows │ Reports          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                           ▲                  ▲                              │
│  ┌────────────────────────┴──────────────────┴────────────────────────────┐  │
│  │                     Data Layer                                      │  │
│  │  PostgreSQL (Main DB)  │  Redis (Cache)  │  MinIO (Evidence Storage)  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      n8n Workflow Engine                               │  │
│  │   Discovery │ Scanning │ Exploitation │ Post-Ex │ Reporting          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                           ▲                  ▲                              │
│  ┌────────────────────────┴──────────────────┴────────────────────────────┐  │
│  │                     Security Tools Stack                               │  │
│  │   Masscan │ Nmap │ OpenVAS │ Metasploit │ Nuclei │ + 190+ Tools      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **OS**: Linux/macOS/Windows (WSL2 recommended)
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 24+
- **Docker Compose**: 2.20+
- **PostgreSQL**: 15+
- **Redis**: 7+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/anptop.git
cd anptop

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize the database
alembic upgrade head

# 6. Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. In a new terminal, start the frontend
cd frontend
npm install
npm start
```

### Docker Quick Start

```bash
# Start all services with Docker Compose
docker-compose up -d

# Access the platform
# UI: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# n8n: http://localhost:5678
```

---

## 📁 Project Structure

```
anptop/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── engagements.py # Engagement management
│   │   │   ├── targets.py     # Target management
│   │   │   ├── workflows.py   # Workflow management
│   │   │   ├── reports.py     # Reporting endpoints
│   │   │   └── audit.py       # Audit logging
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings
│   │   │   ├── security.py    # Security utilities
│   │   │   └── exceptions.py  # Custom exceptions
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User model
│   │   │   ├── engagement.py  # Engagement model
│   │   │   ├── target.py      # Target model
│   │   │   ├── workflow.py    # Workflow model
│   │   │   └── evidence.py    # Evidence model
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── workflow.py    # Workflow execution
│   │   │   ├── scanner.py     # Scanner management
│   │   │   └── reporting.py   # Report generation
│   │   └── db/                # Database setup
│   │       ├── base.py        # Base class
│   │       ├── session.py     # Database session
│   │       └── init_db.py     # Database initialization
│   ├── requirements.txt      # Python dependencies
│   ├── main.py               # FastAPI application entry
│   └── .env.example          # Environment template
│
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   │   ├── Layout/        # App layout
│   │   │   ├── Dashboard/     # Dashboard widgets
│   │   │   ├── Engagement/    # Engagement forms
│   │   │   ├── Target/        # Target management
│   │   │   ├── Workflow/      # Workflow builder
│   │   │   ├── Report/        # Report viewer
│   │   │   └── Common/       # Shared components
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.py
│   │   │   ├── Engagements.py
│   │   │   ├── Targets.py
│   │   │   ├── Workflows.py
│   │   │   ├── Reports.py
│   │   │   ├── Settings.py
│   │   │   └── AuditLogs.py
│   │   ├── services/         # API services
│   │   │   ├── api.js        # API client
│   │   │   ├── auth.js       # Auth service
│   │   │   └── workflow.js   # Workflow service
│   │   ├── hooks/            # Custom React hooks
│   │   ├── store/            # State management
│   │   ├── utils/            # Utility functions
│   │   └── styles/           # CSS styles
│   ├── package.json
│   └── README.md
│
├── docker/                    # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── Dockerfile.n8n
│   └── nginx.conf
│
├── k8s/                       # Kubernetes configurations
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── n8n-deployment.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── ingress.yaml
│   └── secrets.yaml
│
├── n8n/                       # n8n workflow configurations
│   ├── workflows/
│   │   ├── target-intake.yaml
│   │   ├── host-discovery.yaml
│   │   ├── port-scanning.yaml
│   │   ├── service-detection.yaml
│   │   ├── vulnerability-assessment.yaml
│   │   ├── cve-correlation.yaml
│   │   ├── exploitation.yaml
│   │   ├── post-exploitation.yaml
│   │   ├── lateral-movement.yaml
│   │   ├── evidence-collection.yaml
│   │   └── reporting.yaml
│   └── n8n-credentials.yaml
│
├── scripts/                   # Utility scripts
│   ├── setup.sh
│   ├── backup.sh
│   ├── restore.sh
│   └── tools-setup.sh
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── BACKEND.md
│   ├── FRONTEND.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY_COMPLIANCE.md
│   ├── N8N_WORKFLOWS.md
│   ├── REPORTING_ENGINE.md
│   ├── TOOLS_INTEGRATION.md
│   ├── COMPLETE_TOOLS.md
│   ├── ENHANCED_TOOLS.md
│   └── GAP_ANALYSIS.md
│
├── .env.example               # Environment template
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── README.md
```

---

## 🔑 Key Features

### 1. Engagement Management
- Create and manage penetration testing engagements
- Define scope and rules of engagement (ROE)
- Track engagement lifecycle (Planning → Execution → Reporting)
- Multi-engagement support with team collaboration

### 2. Target Discovery & Scanning
- Automated host discovery (Masscan, Nmap)
- Port scanning with multiple engines
- Service and version detection
- OS fingerprinting
- Cloud asset discovery (AWS, Azure, GCP)

### 3. Vulnerability Assessment
- OpenVAS integration for comprehensive scanning
- Nuclei template-based scanning
- CVE correlation and prioritization
- Risk scoring based on CVSS
- Custom vulnerability definitions

### 4. Exploitation Framework
- Metasploit Framework integration
- Approval-gated exploitation workflow
- Automated exploitation attempts
- Post-exploitation automation
- Evidence collection and preservation

### 5. Reporting Engine
- Executive summary reports
- Technical detail reports
- Compliance reports (PCI-DSS, SOC2)
- Customizable report templates
- Evidence attachment support

### 6. Security & Compliance
- Role-Based Access Control (RBAC)
- Multi-Factor Authentication (MFA)
- Comprehensive audit logging
- Scope boundary enforcement
- Kill switch for emergency stops

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, all engagements |
| **Lead Tester** | Create/manage engagements, approve workflows, full access |
| **Senior Tester** | Execute workflows, access all engagements, export reports |
| **Tester** | Execute assigned workflows, access assigned engagements |
| **Analyst** | View reports, create findings, access read-only data |
| **Viewer** | Read-only access to assigned engagements |
| **API User** | Programmatic access via API tokens |

---

## 🔧 Configuration

### Environment Variables

```env
# Application
APP_NAME=ANPTOP
APP_VERSION=2.0.0
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/anptop
REDIS_URL=redis://localhost:6379/0

# Authentication
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MFA_ENABLED=true

# n8n Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key

# Evidence Storage
EVIDENCE_STORAGE_PATH=/data/evidence
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET=anptop-evidence

# External Tools
METASPLOIT_RPC_URL=http://localhost:55552
METASPLOIT_RPC_USER=msfrpc
METASPLOIT_RPC_PASSWORD=your-password

# Security
ENABLE_KILL_SWITCH=true
SCOPE_VALIDATION=true
AUDIT_LOG_RETENTION_DAYS=365
```

---

## 📊 Supported Security Tools

### Discovery & Scanning (14 tools)
- Masscan, RustScan, Nmap, Unicornscan
- DNSRecon, DNSChef, TheHarvester
- AWS CLI, Azure CLI, gcloud

### Vulnerability Assessment (22 tools)
- OpenVAS, Greenbone CE, Nessus, Nuclei
- XSSer, SQLMap, Nikto, SSLScan
- ScoutSuite, Prowler, Trivy, kube-hunter

### Exploitation (23 tools)
- Metasploit Framework, CrackMapExec, Responder
- Pacu, Cloud Fox, Sliver, Covenant

### Post-Exploitation (30 tools)
- Mimikatz, LaZagne, BloodHound
- Gitleaks, Peirates, kubectl

### Specialized (Fintech Tools)
- Payment Systems: Stripe CLI, PCI DSS Scanner
- Blockchain: Mythril, Slither, Echidna
- API Security: Burp Suite, OWASP ZAP

**Total: 196 integrated security tools**

---

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React UI |
| Backend | 8000 | FastAPI |
| API Docs | 8000 | Swagger UI |
| n8n | 5678 | Workflow Engine |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| MinIO | 9000 | Evidence Storage |

---

## ☸️ Kubernetes Deployment

```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy all services
kubectl apply -f k8s/

# Check status
kubectl get pods -n anptop
```

---

## 📝 API Documentation

FastAPI automatically generates OpenAPI documentation.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Example API Usage

```bash
# Authentication
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'

# List engagements
curl -X GET "http://localhost:8000/api/v1/engagements" \
  -H "Authorization: Bearer <token>"

# Trigger workflow
curl -X POST "http://localhost:8000/api/v1/workflows/1/execute" \
  -H "Authorization: Bearer <token>"
```

---

## 🔒 Security Considerations

1. **Scope Validation**: All targets are validated against engagement scope before scanning
2. **Kill Switch**: Emergency stop for all running scans
3. **Evidence Immutability**: Cryptographic hashing of all evidence
4. **Audit Trail**: Comprehensive logging of all actions
5. **RBAC**: Fine-grained permissions system
6. **MFA**: Two-factor authentication support
7. **Session Management**: Secure JWT token handling
8. **Data Encryption**: At-rest and in-flight encryption

---

## 📄 License

Proprietary - All rights reserved

---

## 🤝 Support

- Documentation: `/docs`
- API Docs: `/api/docs`
- n8n Workflows: `/n8n/workflows`
