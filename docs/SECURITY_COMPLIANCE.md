# ANPTOP - Security & Compliance Documentation

## Table of Contents
1. [Threat Model](#threat-model)
2. [Security Controls](#security-controls)
3. [Compliance Mapping](#compliance-mapping)
4. [Abuse Case Analysis](#abuse-case-analysis)
5. [Legal Safeguards](#legal-safeguards)
6. [Audit Framework](#audit-framework)
7. [Hardening Checklist](#hardening-checklist)

---

## 1. Threat Model

### 1.1 Asset Classification
```yaml
assets:
  critical:
    - evidence_data: "All collected evidence with cryptographic hashes"
    - credentials: "User credentials and session tokens"
    - scan_results: "Raw scan data and vulnerability findings"
    - audit_logs: "Complete audit trail of all actions"
    
  high:
    - engagement_data: "Engagement scope and findings"
    - user_data: "User profiles and roles"
    - configurations: "System and tool configurations"
    
  medium:
    - reports: "Generated reports (already anonymized)"
    - templates: "Report templates and configurations"
    - logs: "Application and access logs"
    
  low:
    - documentation: "Public documentation"
    - metrics: "Aggregated statistics (no PII)"
```

### 1.2 Threat Actors
```yaml
threat_actors:
  external:
    - description: "External attackers attempting unauthorized access"
      motivation: "Data theft, disruption, financial gain"
      capability: "Sophisticated - Nation state level"
      
    - description: "Opportunistic attackers"
      motivation: "Proof of concept, notoriety"
      capability: "Moderate - Standard attack tools"
      
  internal:
    - description: "Malicious insider"
      motivation: "Data theft, sabotage, espionage"
      capability: "High - Authorized access"
      
    - description: "Negligent employee"
      motivation: "Accidental data exposure"
      capability: "Unintended - Misconfiguration"
      
  third_party:
    - description: "Tool vendors and integrators"
      motivation: "Access for support/maintenance"
      capability: "Limited - Restricted access"
```

### 1.3 Attack Surface
```yaml
attack_surface:
  network:
    - frontend: "React application (HTTPS only)"
    - api: "FastAPI backend (HTTPS only)"
    - n8n: "Workflow engine (internal only)"
    - databases: "PostgreSQL (internal only)"
    
  endpoints:
    - users: "Web browser access"
    - operators: "Workstations with tool access"
    - servers: "Backend servers"
    
  data_flows:
    - user_authentication: "JWT-based auth with MFA"
    - evidence_collection: "Hash-verified storage"
    - tool_execution: "Approval-gated execution"
```

### 1.4 Threat Analysis Matrix
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Threat Analysis Matrix                              │
├──────────────┬───────────────┬───────────────┬───────────────┬───────────────┤
│ Threat       │ Likelihood    │ Impact        │ Risk Score    │ Mitigation    │
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Unauthorized │ HIGH          │ CRITICAL      │ HIGH (9.0)    │ RBAC, MFA    │
│ Access       │               │               │               │ Audit, Alerts│
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Evidence     │ MEDIUM        │ HIGH          │ MEDIUM (6.0)  │ Hash verify  │
│ Tampering    │               │               │ │ Immutability │
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Exploitation │ LOW          │ CRITICAL      │ MEDIUM (7.0)  │ Approval     │
│ Abuse        │               │               │ │ Kill switches│
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Data Leakage │ MEDIUM        │ HIGH          │ MEDIUM (6.0)  │ Encryption   │
│              │               │               │ │ DLP          │
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Service      │ LOW           │ MEDIUM        │ LOW (3.0)     │ HA, Monitoring│
│ Disruption   │               │               │ │ Failover     │
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Privilege    │ MEDIUM        │ CRITICAL      │ HIGH (8.0)    │ Least priv   │
│ Escalation   │               │               │ │ Session mgmt │
└──────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
```

---

## 2. Security Controls

### 2.1 Authentication Controls
```yaml
authentication:
  mfa_required: true
  
  mfa_methods:
    - totp: "Time-based one-time passwords (RFC 6238)"
    - hardware: "FIDO2/YubiKey hardware tokens"
    - sms: "SMS fallback (not recommended for critical)"
    
  password_policy:
    min_length: 16
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special: true
    max_age_days: 90
    history_count: 12
    
  session_management:
    access_token_minutes: 15
    refresh_token_hours: 8
    max_sessions: 5
    concurrent_limit: 2
    session_timeout: 30
```

### 2.2 Authorization Controls
```yaml
authorization:
  rbac:
    enabled: true
    model: "RBAC with attribute-based extensions"
    
  roles:
    viewer:
      - view_dashboard
      - view_engagements
      - view_reports
      
    analyst:
      - inherits: viewer
      - create_engagement
      - start_scan
      - view_all_hosts
      
    senior_analyst:
      - inherits: analyst
      - approve_standard_exploitation
      - approve_post_exploitation
      
    team_lead:
      - inherits: senior_analyst
      - approve_all_exploitation
      - emergency_stop
      - manage_team
      
    ciso:
      - inherits: team_lead
      - bypass_approval
      - modify_roles
      - system_config
      
  separation_of_duties:
    - role: "exploitation_approver"
      requires: "not_executor"
    - role: "evidence_collector"
      requires: "not_auditor"
```

### 2.3 Data Protection Controls
```yaml
data_protection:
  encryption:
    at_rest:
      algorithm: "AES-256-GCM"
      key_management: "HashiCorp Vault"
      key_rotation: 90 days
      
    in_transit:
      protocol: "TLS 1.3"
      cipher_suites:
        - "TLS_AES_256_GCM_SHA384"
        - "TLS_AES_128_GCM_SHA256"
      certificate: "RSA 4096-bit"
      
  evidence_integrity:
    hashing_algorithm: "SHA-256"
    sensitive_hashing: "SHA-512"
    timestamp_source: "NTP-synchronized"
    
  data_classification:
    - level: "public"
      handling: "No protection required"
      encryption: false
      
    - level: "internal"
      handling: "Standard protection"
      encryption: false
      
    - level: "confidential"
      handling: "Enhanced protection"
      encryption: true
      access_logging: true
      
    - level: "restricted"
      handling: "Maximum protection"
      encryption: true
      access_logging: true
      mfa_required: true
```

### 2.4 Network Security Controls
```yaml
network_security:
  segmentation:
    management_network:
      cidr: "10.0.0.0/24"
      access: "Admin only"
      
    tool_network:
      cidr: "10.0.1.0/24"
      access: "Authorized tools only"
      
    data_network:
      cidr: "10.0.2.0/24"
      access: "Backend services only"
      
  firewalls:
    ingress:
      - port: 443
        source: "0.0.0.0/0"
        action: "allow"
        
    egress:
      - port: 443
        destination: "api.nvd.nist.gov"
        action: "allow"
      - port: 25
        destination: "smtp.example.com"
        action: "allow"
        
  monitoring:
    ids: "Suricata on tool network"
    logging: "All traffic logged"
    alerts: "Anomaly detection enabled"
```

### 2.5 Application Security Controls
```yaml
app_security:
  input_validation:
    enabled: true
    method: "Whitelist validation"
    
  output_encoding:
    enabled: true
    context_aware: true
    
  security_headers:
    - "Strict-Transport-Security: max-age=31536000; includeSubDomains"
    - "X-Content-Type-Options: nosniff"
    - "X-Frame-Options: DENY"
    - "Content-Security-Policy: default-src 'self'"
    
  vulnerability_management:
    sast: "Static analysis on all code"
    dast: "Dynamic scanning in CI/CD"
    dependency_check: "Automated daily scans"
```

---

## 3. Compliance Mapping

### 3.1 MITRE ATT&CK Mapping
```yaml
mitre_attack_mapping:
  initial_access:
    techniques:
      - id: "T1190"
        name: "Exploit Public-Facing Application"
        coverage: "OpenVAS scanning, vulnerability correlation"
        
      - id: "T1133"
        name: "External Remote Services"
        coverage: "Port scanning, service enumeration"
        
  execution:
    techniques:
      - id: "T1059"
        name: "Command and Scripting Interpreter"
        coverage: "Command logging, session management"
        
      - id: "T1204"
        name: "User Execution"
        coverage: "Approval workflow for exploitation"
        
  persistence:
    techniques:
      - id: "T1547"
        name: "Boot or Logon Autostart Execution"
        coverage: "Post-exploitation evidence collection"
        
  privilege_escalation:
    techniques:
      - id: "T1068"
        name: "Exploitation for Privilege Escalation"
        coverage: "Privilege escalation tracking"
        
  defense_evasion:
    techniques:
      - id: "T1070"
        name: "Indicator Removal"
        coverage: "Comprehensive logging, evidence preservation"
        
  credential_access:
    techniques:
      - id: "T1003"
        name: "OS Credential Dumping"
        coverage: "Credential harvesting tracking"
        
  discovery:
    techniques:
      - id: "T1046"
        name: "Network Service Discovery"
        coverage: "Port and service enumeration"
        
  lateral_movement:
    techniques:
      - id: "T1021"
        name: "Remote Services"
        coverage: "Lateral movement approval workflow"
        
  collection:
    techniques:
      - id: "T1213"
        name: "Data from Information Repositories"
        coverage: "Data collection tracking"
        
  exfiltration:
    techniques:
      - id: "T1041"
        name: "Exfiltration Over C2 Channel"
        coverage: "Data exfiltration prevention"
```

### 3.2 NIST SP 800-115 Mapping
```yaml
nist_sp_800_115:
  section_3_planning:
    req: "Pentesting methodology defined"
    status: "Implemented"
    evidence: "Documentation in /docs/methodology"
    
    req: "Rules of engagement documented"
    status: "Implemented"
    evidence: "ROE stored per engagement"
    
    req: "Scope defined and approved"
    status: "Implemented"
    evidence: "Scope validation workflow"
    
  section_4_reconnaissance:
    req: "Passive reconnaissance conducted"
    status: "Implemented"
    evidence: "OSINT module in n8n"
    
    req: "Active reconnaissance conducted"
    status: "Implemented"
    evidence: "Host discovery workflow"
    
  section_4_scanning:
    req: "Network discovery performed"
    status: "Implemented"
    evidence: "Masscan, RustScan, Nmap integration"
    
    req: "Port/service identification performed"
    status: "Implemented"
    evidence: "Service detection workflow"
    
    req: "Vulnerability identification performed"
    status: "Implemented"
    evidence: "OpenVAS integration"
    
  section_4_exploitation:
    req: "Controlled exploitation methodology"
    status: "Implemented"
    evidence: "Approval workflow, execution logging"
    
    req: "Privilege escalation documented"
    status: "Implemented"
    evidence: "Post-exploitation tracking"
    
    req: "Lateral movement documented"
    status: "Implemented"
    evidence: "Lateral movement workflow"
    
  section_5_reporting:
    req: "Findings documented"
    status: "Implemented"
    evidence: "Automated reporting engine"
    
    req: "Remediation recommendations provided"
    status: "Implemented"
    evidence: "Technical report template"
    
    req: "Executive summary provided"
    status: "Implemented"
    evidence: "Executive report template"
```

### 3.3 PCI-DSS Mapping
```yaml
pci_dss:
  requirement_1:
    name: "Install and maintain firewall configuration"
    status: "Compliant"
    evidence: "Network segmentation implemented"
    
  requirement_2:
    name: "Do not use vendor-supplied defaults"
    status: "Compliant"
    evidence: "Hardened configurations, custom credentials"
    
  requirement_3:
    name: "Protect stored cardholder data"
    status: "Compliant"
    evidence: "No cardholder data in system, encryption at rest"
    
  requirement_6:
    name: "Develop and maintain secure systems"
    status: "Compliant"
    evidence: "Secure development lifecycle, vulnerability scanning"
    
  requirement_7:
    name: "Restrict access to cardholder data"
    status: "Compliant"
    evidence: "RBAC implementation, least privilege"
    
  requirement_8:
    name: "Identify and authenticate access"
    status: "Compliant"
    evidence: "MFA required, session management"
    
  requirement_10:
    name: "Track and monitor all access"
    status: "Compliant"
    evidence: "Comprehensive audit logging"
```

---

## 4. Abuse Case Analysis

### 4.1 Unauthorized Access
```yaml
abuse_case:
  id: "UC-001"
  name: "Unauthorized Access to Evidence"
  
  description: |
    An attacker gains unauthorized access to sensitive evidence data
    through compromised credentials or session hijacking.
    
  preconditions:
    - Valid user session exists
    - Attacker has valid credentials or session token
    
  attack_steps:
    1. "Attacker obtains valid credentials through phishing"
    2. "Attacker authenticates to the system"
    3. "Attacker navigates to evidence repository"
    4. "Attacker downloads sensitive evidence"
    
  postconditions:
    - Evidence data compromised
    - Chain of custody broken
    
  impact: "HIGH - Legal and compliance implications"
  
  mitigations:
    - "MFA required for all users"
    - "Session tokens have 15-minute expiry"
    - "Evidence access logged and monitored"
    - "Sensitive evidence requires additional approval"
```

### 4.2 Evidence Tampering
```yaml
abuse_case:
  id: "UC-002"
  name: "Evidence Tampering"
  
  description: |
    A user with legitimate access modifies or deletes evidence
    to hide findings or destroy proof of compromise.
    
  preconditions:
    - User has evidence access permissions
    - User has write access to evidence storage
    
  attack_steps:
    1. "User with access logs into system"
    2. "User navigates to evidence management"
    3. "User modifies evidence files"
    4. "User updates evidence records"
    
  postconditions:
    - Evidence integrity compromised
    - Legal proceedings impacted
    
  impact: "CRITICAL - Legal proceedings compromised"
  
  mitigations:
    - "All evidence hash-verified before use"
    - "Chain of custody fully tracked"
    - "Evidence immutability enforced"
    - "Unauthorized modifications trigger alerts"
```

### 4.3 Unauthorized Exploitation
```yaml
abuse_case:
  id: "UC-003"
  name: "Unauthorized Exploitation"
  
  description: |
    An attacker or insider performs unauthorized exploitation
    activities outside of approved scope.
    
  preconditions:
    - User has exploitation tool access
    - Approval bypass attempted
    
  attack_steps:
    1. "User creates exploitation request"
    2. "User bypasses approval workflow"
    3. "User executes exploitation tools"
    4. "User covers tracks"
    
  postconditions:
    - Unauthorized access gained
    - Scope violations
    
  impact: "CRITICAL - Legal liability, system compromise"
  
  mitigations:
    - "All exploitation requires approval"
    - "Dual-approver for critical actions"
    - "Kill switches for immediate halt"
    - "Comprehensive execution logging"
```

### 4.4 Scope Violation
```yaml
abuse_case:
  id: "UC-004"
  name: "Scope Violation"
  
  description: |
    A pentester scans or attacks systems outside of the
    approved engagement scope.
    
  preconditions:
    - Engagement has defined scope
    - Tools can access out-of-scope systems
    
  attack_steps:
    1. "Pentester identifies out-of-scope system"
    2. "Pentester launches scan against system"
    3. "Pentester discovers vulnerability"
    4. "Pentester reports findings"
    
  postconditions:
    - Unauthorized access to third-party systems
    - Legal liability
    
  impact: "CRITICAL - Legal liability, regulatory violation"
  
  mitigations:
    - "Scope validation before each action"
    - "Automatic scope boundary enforcement"
    - "DNS-based scope validation"
    - "Real-time scope violation alerts"
```

---

## 5. Legal Safeguards

### 5.1 Rules of Engagement Enforcement
```yaml
roe_enforcement:
  required_documents:
    - "Signed authorization letter"
    - "Rules of engagement document"
    - "Scope approval form"
    - "Legal contact information"
    
  pre_execution_checks:
    - "Scope validation against approved list"
    - "Target ownership verification"
    - "Legal authorization confirmation"
    
  real_time_controls:
    - "Automatic scope enforcement"
    - "Boundary detection"
    - "Rate limiting"
    - "Impact monitoring"
    
  post_execution:
    - "Scope violation detection"
    - "Impact assessment"
    - "Legal review trigger"
```

### 5.2 Approval Workflow Legal Requirements
```yaml
approval_requirements:
  exploitation_approval:
    minimum_approvers: 1
    roles_required:
      - "SENIOR_ANALYST"
      - "TEAM_LEAD"
      - "CISO"
    documentation_required:
      - "Target identification"
      - "Expected impact"
      - "Mitigation measures"
      
  critical_exploitation:
    minimum_approvers: 2
    roles_required:
      - "TEAM_LEAD"
      - "CISO"
    additional_requirements:
      - "Legal approval"
      - "Client notification"
      - "Emergency response ready"
      
  lateral_movement:
    minimum_approvers: 2
    roles_required:
      - "TEAM_LEAD"
      - "CISO"
    justification_required: true
```

### 5.3 Evidence Handling Legal Requirements
```yaml
evidence_handling:
  chain_of_custody:
    required_fields:
      - "Evidence ID"
      - "Collection timestamp"
      - "Collector identification"
      - "Storage location"
      - "Hash values"
      - "Access log"
      
  retention_requirements:
    pci_engagement: "2555 days (7 years)"
    hipaa_engagement: "2555 days (7 years)"
    standard_engagement: "730 days (2 years)"
    
  access_controls:
    - "Role-based access required"
    - "MFA for sensitive evidence"
    - "Access logging mandatory"
    - "Unauthorized access = alert"
```

---

## 6. Audit Framework

### 6.1 Audit Log Requirements
```yaml
audit_requirements:
  what_to_log:
    authentication:
      - "Login attempts (success/failure)"
      - "Logout events"
      - "Session creation/destruction"
      - "MFA events"
      
    authorization:
      - "Permission changes"
      - "Role assignments"
      - "Scope modifications"
      - "Approval requests/actions"
      
    data_access:
      - "Evidence access"
      - "Report generation"
      - "Configuration changes"
      - "Data exports"
      
    operations:
      - "Scan initiation"
      - "Exploitation execution"
      - "Evidence collection"
      - "Report generation"
      
  log_format:
    fields:
      - timestamp
      - user_id
      - user_ip
      - action
      - resource_type
      - resource_id
      - result
      - details
      
  log_protection:
    - "Immutable storage"
    - "Hash-verified"
    - "Signed by system"
    - "Retained per policy"
```

### 6.2 Audit Log Schema
```python
class AuditLogEntry:
    """
    Comprehensive audit log entry
    """
    timestamp: datetime
    correlation_id: UUID
    
    # Actor
    user_id: UUID
    user_ip: IPv4Address
    user_agent: str
    session_id: UUID
    
    # Action
    action: AuditAction
    resource_type: ResourceType
    resource_id: UUID
    resource_name: str
    
    # Context
    engagement_id: UUID
    tool_used: str
    command_executed: str
    
    # Result
    success: bool
    error_message: str
    
    # Risk Assessment
    risk_level: RiskLevel
    approval_id: UUID
    
    # Compliance
    compliance_tags: List[str]
    requires_review: bool
```

### 6.3 Audit Review Process
```yaml
audit_review:
  daily:
    - "Failed authentication attempts > 10"
    - "Scope modifications"
    - "Approval rejections"
    
  weekly:
    - "All exploitation activities"
    - "Evidence access patterns"
    - "Permission changes"
    
  monthly:
    - "Full audit log review"
    - "Compliance check"
    - "Anomaly detection review"
    
  quarterly:
    - "External audit"
    - "Policy review"
    - "Access certification"
```

---

## 7. Hardening Checklist

### 7.1 Operating System Hardening
```yaml
os_hardening:
  linux:
    - "Disable unused services"
    - "Enable firewall (iptables/nftables)"
    - "Configure SELinux/AppArmor"
    - "Patch management enabled"
    - "Kernel hardening (sysctl)"
    
  windows:
    - "Enable Windows Defender"
    - "Configure Windows Firewall"
    - "Enable BitLocker"
    - "Apply security baselines"
    - "Disable SMBv1"
```

### 7.2 Database Hardening
```yaml
database_hardening:
  postgresql:
    - "Enable SSL connections only"
    - "Configure strong authentication"
    - "Enable audit logging"
    - "Restrict network access"
    - "Enable row-level security"
    - "Configure connection limits"
    - "Enable encryption at rest"
```

### 7.3 Application Hardening
```yaml
application_hardening:
  backend:
    - "Enable HTTPS only"
    - "Configure HSTS"
    - "Enable CORS restrictions"
    - "Configure rate limiting"
    - "Enable request validation"
    - "Configure security headers"
    
  frontend:
    - "Enable CSP"
    - "XSS protection enabled"
    - "Clickjacking protection"
    - "Subresource integrity"
```

### 7.4 Docker/Kubernetes Hardening
```yaml
container_hardening:
  docker:
    - "Use non-root user"
    - "Enable seccomp profile"
    - "Configure capability drops"
    - "Enable user namespace remapping"
    - "Use minimal base images"
    - "Enable content trust"
    - "Configure resource limits"
    
  kubernetes:
    - "Enable RBAC"
    - "Configure network policies"
    - "Enable pod security policies"
    - "Configure secrets encryption"
    - "Enable audit logging"
    - "Configure resource quotas"
```

### 7.5 Network Hardening
```yaml
network_hardening:
  firewall:
    - "Deny all by default"
    - "Allow specific rules only"
    - "Enable connection logging"
    - "Configure IPS rules"
    
  segmentation:
    - "Management network isolated"
    - "Tool network isolated"
    - "Data network isolated"
    - "DMZ configured"
    
  monitoring:
    - "Enable IDS/IPS"
    - "Configure NetFlow"
    - "Enable packet capture"
    - "Configure SIEM integration"
```

### 7.6 Compliance Verification Checklist
```yaml
compliance_checklist:
  authentication:
    [x] MFA enabled
    [x] Password policy enforced
    [x] Session timeout configured
    [x] Failed login lockout enabled
    
  authorization:
    [x] RBAC implemented
    [x] Least privilege enforced
    [x] Separation of duties configured
    [x] Access reviews scheduled
    
  encryption:
    [x] TLS 1.3 configured
    [x] Certificate pinning enabled
    [x] Encryption at rest configured
    [x] Key rotation enabled
    
  logging:
    [x] Audit logging enabled
    [x] Log integrity protected
    [x] Log retention configured
    [x] Alerting configured
    
  monitoring:
    [x] IDS/IPS enabled
    [x] Anomaly detection configured
    [x] Incident response defined
    [x] Escalation procedures documented
    
  backup:
    [x] Automated backups configured
    [x] Backup encryption enabled
    [x] Backup testing scheduled
    [x] Recovery procedures documented
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
