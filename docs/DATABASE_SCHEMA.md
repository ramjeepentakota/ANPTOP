# ANPTOP - Database Schema & Evidence Model

## Table of Contents
1. [Database Overview](#database-overview)
2. [Core Entity Relationship Diagram](#core-entity-relationship-diagram)
3. [Table Definitions](#table-definitions)
4. [Enums and Lookup Tables](#enums-and-lookup-tables)
5. [Index Strategy](#index-strategy)
6. [Evidence Storage Design](#evidence-storage-design)
7. [Hashing & Immutability Model](#hashing--immutability-model)
8. [Retention Policies](#retention-policies)
9. [SQL Schema (Complete)](#sql-schema-complete)

---

## 1. Database Overview

### 1.1 Design Principles
- **ACID Compliant**: Full transactional support for audit integrity
- **Normalized**: Third normal form for data integrity
- **Indexed**: Strategic indexes for performance
- **Audit-Friendly**: All modifications tracked
- **Scalable**: Optimized for large engagements (10,000+ hosts)

### 1.2 Database Configuration
```yaml
database:
  engine: PostgreSQL 15+
  collation: en_US.UTF-8
  timezone: UTC
  
  connections:
    pool_size: 20
    max_overflow: 40
    idle_timeout: 300
    
  replication:
    synchronous_commit: on
    hot_standby: enabled
    
  backup:
    wal_level: replica
    retention: 30 days
```

---

## 2. Core Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ANPTOP Entity Relationship                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐         ┌─────────────┐                                   │
│   │    User     │────────>│ Engagement  │<──────────────┐                    │
│   └──────┬──────┘         └──────┬──────┘              │                    │
│          │                       │                     │                    │
│          │                       │                     │                    │
│   ┌──────┴──────┐         ┌──────┴──────┐     ┌───────┴───────┐           │
│   │ Audit_Log   │         │    Host     │<────│ Scope_Range    │           │
│   └─────────────┘         └──────┬──────┘     └───────────────┘           │
│                                  │                                       │
│                     ┌────────────┼────────────┐                          │
│                     │            │            │                          │
│              ┌──────┴──────┐    │    ┌───────┴───────┐                   │
│              │    Port     │    │    │   Evidence    │                   │
│              └──────┬──────┘    │    └───────────────┘                   │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │   Service   │                                  │
│                     │    └──────┬──────┘                                  │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │ Enumeration  │                                  │
│                     │    └──────┬──────┘                                  │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │ Vulnerability│                                  │
│                     │    └──────┬──────┘                                  │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │   Exploit    │                                  │
│                     │    └──────┬──────┘                                  │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │PostExploit  │                                  │
│                     │    └──────┬──────┘                                  │
│                     │           │                                         │
│                     │    ┌──────┴──────┐                                  │
│                     │    │ LateralMove │                                  │
│                     │    └─────────────┘                                  │
│                     │                                                     │
│              ┌──────┴──────┐                                              │
│              │    CVE     │                                              │
│              └─────────────┘                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Table Definitions

### 3.1 Users & Authentication

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    role VARCHAR(32) NOT NULL REFERENCES roles(name),
    department VARCHAR(64),
    is_active BOOLEAN DEFAULT true,
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(128),
    last_login TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_role CHECK (role IN ('VIEWER', 'ANALYST', 'SENIOR_ANALYST', 
                                          'ENGAGEMENT_MANAGER', 'AUDITOR', 
                                          'TEAM_LEAD', 'CISO'))
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### user_sessions
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    refresh_token_hash VARCHAR(64) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_expiry CHECK (expires_at > NOW())
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_sessions_expiry ON user_sessions(expires_at);
```

#### roles
```sql
CREATE TABLE roles (
    name VARCHAR(32) PRIMARY KEY,
    display_name VARCHAR(64) NOT NULL,
    description TEXT,
    level INTEGER NOT NULL UNIQUE,
    permissions JSONB NOT NULL DEFAULT '{}'
);

-- Insert default roles
INSERT INTO roles (name, display_name, description, level, permissions) VALUES
('VIEWER', 'Viewer', 'Read-only access to assigned engagements', 1, 
 '{"view_dashboard": true, "view_engagements": true, "view_reports": true}'),
('ANALYST', 'Analyst', 'Standard pentester operations', 2,
 '{"view_dashboard": true, "view_engagements": true, "create_engagement": true,
   "start_scan": true, "view_all_hosts": true}'),
('SENIOR_ANALYST', 'Senior Analyst', 'Senior pentester with approval rights', 3,
 '{"view_dashboard": true, "view_engagements": true, "create_engagement": true,
   "start_scan": true, "approve_standard_exploitation": true,
   "approve_post_exploitation": true}'),
('ENGAGEMENT_MANAGER', 'Engagement Manager', 'Manages engagement scope and reporting', 3,
 '{"view_dashboard": true, "manage_all_engagements": true, "modify_scope": true,
   "approve_report_generation": true}'),
('AUDITOR', 'Auditor', 'Compliance and audit review', 3,
 '{"view_audit_logs": true, "view_all_engagements": true, "view_all_evidence": true,
   "export_audit_reports": true}'),
('TEAM_LEAD', 'Team Lead', 'Team supervision and critical approvals', 4,
 '{"view_dashboard": true, "approve_all_exploitation": true, "approve_critical_actions": true,
   "manage_team_members": true, "emergency_stop": true}'),
('CISO', 'CISO', 'Executive oversight and emergency access', 5,
 '{"full_system_access": true, "approve_any_action": true, "bypass_approval_gates": true,
   "modify_role_permissions": true, "system_configuration": true}');
```

### 3.2 Engagements

#### engagements
```sql
CREATE TABLE engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    description TEXT,
    client_name VARCHAR(128),
    client_contact_name VARCHAR(128),
    client_contact_email VARCHAR(255),
    client_contact_phone VARCHAR(32),
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    type VARCHAR(32) NOT NULL DEFAULT 'network',
    methodology VARCHAR(64) DEFAULT 'blackbox',
    
    -- Scope
    scope_type VARCHAR(32) NOT NULL,
    scope_targets JSONB NOT NULL DEFAULT '[]',
    scope_exclusions JSONB NOT NULL DEFAULT '[]',
    scope_validation_status VARCHAR(16) DEFAULT 'pending',
    
    -- ROE
    rules_of_engagement TEXT,
    legal_contact_name VARCHAR(128),
    legal_contact_email VARCHAR(255),
    legal_case_number VARCHAR(64),
    
    -- Timing
    start_date DATE,
    end_date DATE,
    timezone VARCHAR(32) DEFAULT 'UTC',
    estimated_duration_days INTEGER,
    
    -- Risk
    impact_rating VARCHAR(16),
    risk_tolerance TEXT,
    
    -- Reporting
    report_template VARCHAR(64),
    executive_summary TEXT,
    
    -- Team
    team_lead_id UUID REFERENCES users(id),
    team_members JSONB DEFAULT '[]',
    
    -- Metadata
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_status CHECK (status IN ('draft', 'pending_approval', 'approved', 
                                              'in_progress', 'paused', 'completed', 
                                              'cancelled', 'archived')),
    CONSTRAINT valid_scope_type CHECK (scope_type IN ('ip_range', 'ip_list', 'domain', 
                                                       'hostname_list', 'cidr', 'url_list')),
    CONSTRAINT valid_type CHECK (type IN ('network', 'web_application', 'internal', 
                                           'external', 'social_engineering', 'physical'))
);

CREATE INDEX idx_engagements_status ON engagements(status);
CREATE INDEX idx_engagements_client ON engagements(client_name);
CREATE INDEX idx_engagements_dates ON engagements(start_date, end_date);
CREATE INDEX idx_engagements_team_lead ON engagements(team_lead_id);
CREATE INDEX idx_engagements_created_by ON engagements(created_by);
```

#### scope_ranges
```sql
CREATE TABLE scope_ranges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    type VARCHAR(16) NOT NULL,
    value VARCHAR(512) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    validation_status VARCHAR(16) DEFAULT 'pending',
    validation_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_type CHECK (type IN ('ip', 'cidr', 'range', 'hostname', 'domain', 'url'))
);

CREATE INDEX idx_scope_engagement ON scope_ranges(engagement_id);
CREATE INDEX idx_scope_value ON scope_ranges(value);
```

#### engagement_approvals
```sql
CREATE TABLE engagement_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    approval_type VARCHAR(32) NOT NULL,
    requested_by UUID NOT NULL REFERENCES users(id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    
    -- Decision
    decision_by UUID REFERENCES users(id),
    decision_at TIMESTAMP WITH TIME ZONE,
    decision_notes TEXT,
    justification TEXT,
    
    -- Escalation
    escalated_to UUID REFERENCES users(id),
    escalated_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    expires_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_approval_type CHECK (approval_type IN ('initiation', 'scope', 
                                                            'execution', 'report', 
                                                            'escalation', 'emergency')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 
                                                'expired', 'escalated', 'cancelled'))
);

CREATE INDEX idx_eng_approval_engagement ON engagement_approvals(engagement_id);
CREATE INDEX idx_eng_approval_status ON engagement_approvals(status);
CREATE INDEX idx_eng_approval_requested_by ON engagement_approvals(requested_by);
```

### 3.3 Hosts & Discovery

#### hosts
```sql
CREATE TABLE hosts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    
    -- Identification
    ip_address INET NOT NULL,
    hostname VARCHAR(256),
    fqdn VARCHAR(512),
    mac_address MACADDR,
    dns_name VARCHAR(512),
    
    -- Classification
    os_guess VARCHAR(256),
    os_confidence DECIMAL(3,2),
    os_family VARCHAR(64),
    os_vendor VARCHAR(64),
    os_version VARCHAR(128),
    
    -- Location
    network_segment VARCHAR(64),
    subnet_mask INET,
    gateway INET,
    domain VARCHAR(128),
    vlan VARCHAR(64),
    
    -- Discovery
    discovery_method VARCHAR(32),
    discovery_tool VARCHAR(64),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Status
    is_alive BOOLEAN DEFAULT true,
    is_reachable BOOLEAN,
    response_time_ms DECIMAL(10,3),
    
    -- Risk
    risk_score DECIMAL(5,2),
    tags JSONB DEFAULT '[]',
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_discovery_method CHECK (discovery_method IN ('ping', 'arp', 
                                                                    'dns', 'nbtstat', 
                                                                    'netbios', 'other'))
);

CREATE INDEX idx_hosts_engagement ON hosts(engagement_id);
CREATE INDEX idx_hosts_ip ON hosts(ip_address);
CREATE INDEX idx_hosts_hostname ON hosts(hostname);
CREATE INDEX idx_hosts_os ON hosts(os_family, os_vendor);
CREATE INDEX idx_hosts_risk ON hosts(risk_score DESC);
```

#### host_services
```sql
CREATE TABLE host_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    
    -- Service Info
    port INTEGER NOT NULL,
    protocol VARCHAR(8) NOT NULL DEFAULT 'tcp',
    service_name VARCHAR(128),
    product VARCHAR(256),
    version VARCHAR(256),
    banner TEXT,
    fingerprint TEXT,
    
    -- Detection
    detection_method VARCHAR(32),
    detection_tool VARCHAR(64),
    detectionConfidence DECIMAL(3,2) DEFAULT 1.0,
    
    -- SSL/TLS
    ssl_enabled BOOLEAN DEFAULT false,
    ssl_version VARCHAR(32),
    ssl_cipher_suite VARCHAR(256),
    ssl_certificate_hash VARCHAR(64),
    
    -- Status
    is_confirmed BOOLEAN DEFAULT true,
    last_checked TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_protocol CHECK (protocol IN ('tcp', 'udp')),
    CONSTRAINT unique_host_port_protocol UNIQUE (host_id, port, protocol)
);

CREATE INDEX idx_services_host ON host_services(host_id);
CREATE INDEX idx_services_port ON host_services(port);
CREATE INDEX idx_services_product ON host_services(product);
CREATE INDEX idx_services_ssl ON host_services(ssl_enabled);
```

### 3.4 Vulnerability Management

#### vulnerabilities
```sql
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    host_id UUID REFERENCES hosts(id),
    service_id UUID REFERENCES host_services(id),
    
    -- Identification
    source VARCHAR(32) NOT NULL,
    source_id VARCHAR(128),
    title VARCHAR(512) NOT NULL,
    description TEXT,
    solution TEXT,
    
    -- CVSS
    cvss_version VARCHAR(8) DEFAULT '3.1',
    cvss_vector VARCHAR(256),
    cvss_base_score DECIMAL(4,2),
    cvss_base_severity VARCHAR(16),
    cvss_temporal_score DECIMAL(4,2),
    cvss_environmental_score DECIMAL(4,2),
    
    -- Classification
    cwe_ids JSONB DEFAULT '[]',
    cve_id VARCHAR(32),
    cert_id VARCHAR(64),
    
    -- Risk
    risk_rating VARCHAR(16),
    exploitability_score DECIMAL(4,2),
    impact_score DECIMAL(4,2),
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'open',
    false_positive BOOLEAN DEFAULT false,
    confirmed BOOLEAN DEFAULT false,
    verified BOOLEAN DEFAULT false,
    
    -- Evidence
    evidence_summary TEXT,
    proof_of_concept TEXT,
    
    -- Remediation
    remediation_priority INTEGER,
    remediation_effort VARCHAR(32),
    remediation_complexity VARCHAR(32),
    
    -- References
    references_json JSONB DEFAULT '[]',
    
    -- Timing
    first_found TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_found TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_fixed TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_source CHECK (source IN ('openvas', 'nessus', 'nmap', 'manual', 
                                               'nuclei', 'custom', 'correlation')),
    CONSTRAINT valid_status CHECK (status IN ('open', 'in_progress', 'resolved', 
                                               'accepted', 'false_positive', 
                                               'reopened', 'closed')),
    CONSTRAINT valid_risk CHECK (risk_rating IN ('critical', 'high', 'medium', 
                                                   'low', 'informational', 'none'))
);

CREATE INDEX idx_vuln_engagement ON vulnerabilities(engagement_id);
CREATE INDEX idx_vuln_host ON vulnerabilities(host_id);
CREATE INDEX idx_vuln_cve ON vulnerabilities(cve_id);
CREATE INDEX idx_vuln_status ON vulnerabilities(status);
CREATE INDEX idx_vuln_cvss ON vulnerabilities(cvss_base_score DESC);
CREATE INDEX idx_vuln_risk ON vulnerabilities(risk_rating);
CREATE INDEX idx_vuln_title ON vulnerabilities(title);
```

#### cve_database
```sql
CREATE TABLE cve_database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cve_id VARCHAR(32) NOT NULL UNIQUE,
    
    -- Description
    description TEXT NOT NULL,
    short_description TEXT,
    
    -- CVSS
    cvss_version VARCHAR(8) DEFAULT '3.1',
    cvss_vector VARCHAR(256),
    cvss_base_score DECIMAL(4,2),
    cvss_base_severity VARCHAR(16),
    cvss_exploitability_score DECIMAL(4,2),
    cvss_impact_score DECIMAL(4,2),
    
    -- Classification
    cwe_id VARCHAR(32),
    capec_id VARCHAR(32),
    
    -- Affected
    vendor VARCHAR(256),
    product VARCHAR(256),
    version_start VARCHAR(64),
    version_end VARCHAR(64),
    version_type VARCHAR(32),
    
    -- References
    references_json JSONB DEFAULT '[]',
    
    -- Dates
    published_date DATE,
    modified_date DATE,
    
    -- Timeline
    exploit_published BOOLEAN DEFAULT false,
    exploit_url VARCHAR(512),
    exploit_status VARCHAR(16),
    
    -- Threat
    threat_type VARCHAR(32),
    threat_description TEXT,
    
    -- Metrics
    attack_complexity VARCHAR(32),
    privileges_required VARCHAR(32),
    user_interaction VARCHAR(32),
    scope VARCHAR(32),
    confidentiality_impact VARCHAR(32),
    integrity_impact VARCHAR(32),
    availability_impact VARCHAR(32,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_threat_type CHECK (threat_type IN ('available', 'proof_of_concept', 
                                                          'unconfirmed', 'unknown')),
    CONSTRAINT valid_exploit_status CHECK (exploit_status IN ('unconfirmed', 
                                                               'proof_of_concept', 
                                                               'functional', 'high'))
);

CREATE INDEX idx_cve_cve_id ON cve_database(cve_id);
CREATE INDEX idx_cve_cvss ON cve_database(cvss_base_score DESC);
CREATE INDEX idx_cve_vendor ON cve_database(vendor, product);
CREATE INDEX idx_cve_published ON cve_database(published_date DESC);
```

### 3.5 Exploitation & Post-Exploitation

#### exploits
```sql
CREATE TABLE exploits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    vulnerability_id UUID REFERENCES vulnerabilities(id),
    host_id UUID REFERENCES hosts(id),
    
    -- Exploit Info
    name VARCHAR(256) NOT NULL,
    module_name VARCHAR(128),
    type VARCHAR(32) NOT NULL,
    tool VARCHAR(64),
    
    -- MITRE ATT&CK
    mitre_technique_id VARCHAR(16),
    mitre_technique_name VARCHAR(256),
    mitre_tactic VARCHAR(32),
    
    -- Description
    description TEXT,
    parameters JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    
    -- Approval
    approval_id UUID REFERENCES engagement_approvals(id),
    
    -- Execution
    executed_by UUID REFERENCES users(id),
    executed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    result_summary TEXT,
    success BOOLEAN,
    output JSONB DEFAULT '{}',
    error_message TEXT,
    
    -- Session Info
    session_id VARCHAR(64),
    session_type VARCHAR(32),
    session_endpoint VARCHAR(256),
    
    -- Evidence
    evidence_ids JSONB DEFAULT '[]',
    
    -- Notes
    operator_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_type CHECK (type IN ('initial_access', 'execution', 'persistence',
                                           'privilege_escalation', 'defense_evasion',
                                           'credential_access', 'discovery', 'collection',
                                           'exfiltration', 'impact')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 
                                               'executing', 'completed', 'failed', 
                                               'cancelled', 'timeout'))
);

CREATE INDEX idx_exploit_engagement ON exploits(engagement_id);
CREATE INDEX idx_exploit_vulnerability ON exploits(vulnerability_id);
CREATE INDEX idx_exploit_host ON exploits(host_id);
CREATE INDEX idx_exploit_status ON exploits(status);
CREATE INDEX idx_exploit_mitre ON exploits(mitre_technique_id);
CREATE INDEX idx_exploit_executed_by ON exploits(executed_by);
```

#### post_exploitation
```sql
CREATE TABLE post_exploitation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    exploit_id UUID REFERENCES exploits(id) ON DELETE CASCADE,
    host_id UUID REFERENCES hosts(id),
    
    -- Action Info
    action_type VARCHAR(32) NOT NULL,
    name VARCHAR(256) NOT NULL,
    module_name VARCHAR(128),
    
    -- MITRE ATT&CK
    mitre_technique_id VARCHAR(16),
    mitre_technique_name VARCHAR(256),
    mitre_tactic VARCHAR(32),
    
    -- Description
    description TEXT,
    command_executed TEXT,
    parameters JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    
    -- Approval
    approval_id UUID REFERENCES engagement_approvals(id),
    
    -- Execution
    executed_by UUID REFERENCES users(id),
    executed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    output TEXT,
    error_message TEXT,
    success BOOLEAN,
    
    -- Evidence
    files_collected JSONB DEFAULT '[]',
    credentials_found JSONB DEFAULT '[]',
    data_exfiltrated JSONB DEFAULT '[]',
    
    -- Persistence
    persistence_mechanism VARCHAR(64),
    persistence_location VARCHAR(256),
    
    -- Privilege
    privilege_level VARCHAR(32),
    privilege_escalated_to VARCHAR(64),
    
    -- Notes
    operator_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_action_type CHECK (action_type IN ('enumeration', 'credential_harvesting',
                                                         'data_discovery', 'persistence_setup',
                                                         'privilege_escalation', 'pivoting',
                                                         'data_exfiltration', 'cleanup',
                                                         'backdoor', 'keylogging')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected',
                                               'executing', 'completed', 'failed',
                                               'cancelled', 'timeout'))
);

CREATE INDEX idx_post_exploit_engagement ON post_exploitation(engagement_id);
CREATE INDEX idx_post_exploit_exploit ON post_exploitation(exploit_id);
CREATE INDEX idx_post_exploit_host ON post_exploitation(host_id);
CREATE INDEX idx_post_exploit_type ON post_exploitation(action_type);
CREATE INDEX idx_post_exploit_status ON post_exploitation(status);
```

#### lateral_movement
```sql
CREATE TABLE lateral_movement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    source_host_id UUID NOT NULL REFERENCES hosts(id),
    target_host_id UUID NOT NULL REFERENCES hosts(id),
    
    -- Technique
    technique VARCHAR(32) NOT NULL,
    protocol VARCHAR(16) NOT NULL,
    service VARCHAR(128),
    
    -- MITRE ATT&CK
    mitre_technique_id VARCHAR(16),
    mitre_technique_name VARCHAR(256),
    
    -- Credentials Used
    credential_id UUID,
    username VARCHAR(128),
    credential_type VARCHAR(32),
    
    -- Method
    method VARCHAR(64),
    command_executed TEXT,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    
    -- Approval
    approval_id UUID REFERENCES engagement_approvals(id),
    
    -- Execution
    executed_by UUID REFERENCES users(id),
    executed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    success BOOLEAN,
    error_message TEXT,
    output TEXT,
    
    -- Session
    new_session_id VARCHAR(64),
    pivot_point VARCHAR(256),
    
    -- Evidence
    evidence_ids JSONB DEFAULT '[]',
    
    -- Notes
    operator_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_technique CHECK (technique IN ('wmiexec', 'psexec', 'smbexec', 
                                                     'atexec', 'dcomexec', 'ssh',
                                                     'rdp', 'winrm', 'vnc', 'other')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected',
                                               'executing', 'completed', 'failed',
                                               'cancelled', 'timeout'))
);

CREATE INDEX idx_latmov_engagement ON lateral_movement(engagement_id);
CREATE INDEX idx_latmov_source ON lateral_movement(source_host_id);
CREATE INDEX idx_latmov_target ON lateral_movement(target_host_id);
CREATE INDEX idx_latmov_status ON lateral_movement(status);
CREATE INDEX idx_latmov_credential ON lateral_movement(credential_id);
```

### 3.6 Evidence & Artifacts

#### evidence
```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    host_id UUID REFERENCES hosts(id),
    
    -- Identification
    evidence_type VARCHAR(32) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    
    -- Storage
    storage_path TEXT NOT NULL,
    storage_bucket VARCHAR(128),
    object_key VARCHAR(512),
    file_size BIGINT,
    mime_type VARCHAR(128),
    
    -- Integrity
    sha256_hash VARCHAR(64) NOT NULL,
    sha512_hash VARCHAR(128),
    md5_hash VARCHAR(32),
    file_signature VARCHAR(256),
    
    -- Context
    source_type VARCHAR(32),
    source_id UUID,
    source_tool VARCHAR(64),
    command_used TEXT,
    
    -- Classification
    sensitivity_level VARCHAR(16) DEFAULT 'confidential',
    contains_credentials BOOLEAN DEFAULT false,
    contains_pii BOOLEAN DEFAULT false,
    
    -- Chain of Custody
    collected_by UUID REFERENCES users(id),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Retention
    retention_until DATE,
    deletion_requested BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES users(id),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT valid_evidence_type CHECK (evidence_type IN ('screenshot', 'pcap', 
                                                             'log_file', 'command_output',
                                                             'configuration', 'credential',
                                                             'document', 'exploit_script',
                                                             'memory_dump', 'database_dump',
                                                             'certificate', 'key_file',
                                                             'other')),
    CONSTRAINT valid_sensitivity CHECK (sensitivity_level IN ('public', 'internal',
                                                                'confidential', 'restricted'))
);

CREATE INDEX idx_evidence_engagement ON evidence(engagement_id);
CREATE INDEX idx_evidence_host ON evidence(host_id);
CREATE INDEX idx_evidence_type ON evidence(evidence_type);
CREATE INDEX idx_evidence_hash ON evidence(sha256_hash);
CREATE INDEX idx_evidence_collected_by ON evidence(collected_by);
CREATE INDEX idx_evidence_retention ON evidence(retention_until);
```

#### command_logs
```sql
CREATE TABLE command_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    host_id UUID REFERENCES hosts(id),
    
    -- Command Info
    command TEXT NOT NULL,
    command_hash VARCHAR(64) NOT NULL,
    tool_used VARCHAR(64),
    
    -- Execution
    executed_by VARCHAR(64),
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Status
    exit_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    
    -- Output
    stdout TEXT,
    stderr TEXT,
    
    -- Evidence Link
    evidence_id UUID REFERENCES evidence(id),
    
    -- Context
    n8n_workflow_id UUID,
    n8n_node_id VARCHAR(128),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT valid_tool CHECK (tool_used IN ('nmap', 'masscan', 'rustscan', 
                                                 'unicornscan', 'metasploit',
                                                 'crackmapexec', 'bloodhound',
                                                 'powerupsql', 'Responder',
                                                 'other'))
);

CREATE INDEX idx_cmd_engagement ON command_logs(engagement_id);
CREATE INDEX idx_cmd_host ON command_logs(host_id);
CREATE INDEX idx_cmd_executed_at ON command_logs(executed_at);
CREATE INDEX idx_cmd_tool ON command_logs(tool_used);
CREATE INDEX idx_cmd_hash ON command_logs(command_hash);
```

### 3.7 Audit & Compliance

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Who
    user_id UUID REFERENCES users(id),
    user_ip INET NOT NULL,
    user_agent TEXT,
    session_id UUID,
    
    -- What
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id UUID,
    resource_name VARCHAR(256),
    
    -- Details
    old_value JSONB,
    new_value JSONB,
    details JSONB DEFAULT '{}',
    
    -- Result
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Compliance
    compliance_tags JSONB DEFAULT '[]',
    requires_review BOOLEAN DEFAULT false,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    
    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete',
                                               'execute', 'approve', 'reject',
                                               'login', 'logout', 'export',
                                               'download', 'upload', 'archive',
                                               'restore', 'escalate', 'emergency_stop'))
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_ip ON audit_logs(user_ip);
CREATE INDEX idx_audit_review ON audit_logs(requires_review, reviewed_by);
```

### 3.8 Approval Workflow Tables

#### approvals
```sql
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    
    -- Request Info
    approval_type VARCHAR(32) NOT NULL,
    request_type VARCHAR(32) NOT NULL,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    
    -- Target
    target_host_id UUID REFERENCES hosts(id),
    target_service VARCHAR(128),
    target_vulnerability UUID REFERENCES vulnerabilities(id),
    
    -- Action Details
    action_details JSONB NOT NULL DEFAULT '{}',
    command_to_execute TEXT,
    
    -- Risk Assessment
    risk_level VARCHAR(16) NOT NULL,
    impact_description TEXT,
    mitigation_measures TEXT,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    priority VARCHAR(16) DEFAULT 'normal',
    
    -- Requester
    requested_by UUID NOT NULL REFERENCES users(id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Approvers
    required_approvers INTEGER DEFAULT 1,
    current_approvers JSONB DEFAULT '[]',
    
    -- Decision
    decided_by UUID REFERENCES users(id),
    decided_at TIMESTAMP WITH TIME ZONE,
    decision_notes TEXT,
    justification TEXT,
    
    -- Escalation
    escalated_to UUID REFERENCES users(id),
    escalated_at TIMESTAMP WITH TIME ZONE,
    
    -- Timing
    expires_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Execution
    execution_id UUID,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_approval_type CHECK (approval_type IN ('exploitation', 
                                                              'post_exploitation',
                                                              'lateral_movement',
                                                              'credential_access',
                                                              'data_exfiltration',
                                                              'scope_change',
                                                              'emergency')),
    CONSTRAINT valid_request_type CHECK (request_type IN ('host_discovery', 
                                                           'port_scan', 'service_scan',
                                                           'vulnerability_scan',
                                                           'exploit_attempt',
                                                           'session_maintenance',
                                                           'credential_dump',
                                                           'data_access',
                                                           'other')),
    CONSTRAINT valid_risk_level CHECK (risk_level IN ('low', 'medium', 'high', 
                                                       'critical')),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'normal', 'high', 
                                                   'critical', 'emergency'))
);

CREATE INDEX idx_approval_engagement ON approvals(engagement_id);
CREATE INDEX idx_approval_status ON approvals(status);
CREATE INDEX idx_approval_type ON approvals(approval_type);
CREATE INDEX idx_approval_requested_by ON approvals(requested_by);
CREATE INDEX idx_approval_expiry ON approvals(expires_at);
```

#### approval_signatures
```sql
CREATE TABLE approval_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_id UUID NOT NULL REFERENCES approvals(id) ON DELETE CASCADE,
    
    -- Signer
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Signature
    signature_type VARCHAR(16) NOT NULL,
    digital_signature TEXT,
    signature_hash VARCHAR(64),
    
    -- Context
    role_at_approval VARCHAR(32) NOT NULL,
    comment TEXT,
    
    -- Timing
    signed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_signature_type CHECK (signature_type IN ('password', 
                                                               'mfa', 'token',
                                                               'biometric', 'hardware'))
);

CREATE INDEX idx_approval_sig_approval ON approval_signatures(approval_id);
CREATE INDEX idx_approval_sig_user ON approval_signatures(user_id);
```

---

## 4. Enums and Lookup Tables

### 4.1 Status Enums
```sql
-- Engagement Status
CREATE TYPE engagement_status AS ENUM (
    'draft', 'pending_approval', 'approved', 
    'in_progress', 'paused', 'completed', 
    'cancelled', 'archived'
);

-- Scan Status  
CREATE TYPE scan_status AS ENUM (
    'pending', 'queued', 'running', 
    'paused', 'completed', 'failed', 
    'cancelled', 'timeout'
);

-- Vulnerability Status
CREATE TYPE vuln_status AS ENUM (
    'open', 'in_progress', 'resolved', 
    'accepted', 'false_positive', 
    'reopened', 'closed'
);

-- Risk Rating
CREATE TYPE risk_rating AS ENUM (
    'critical', 'high', 'medium', 
    'low', 'informational', 'none'
);

-- Approval Status
CREATE TYPE approval_status AS ENUM (
    'pending', 'approved', 'rejected', 
    'expired', 'escalated', 'cancelled'
);
```

### 4.2 Lookup Tables

#### scan_types
```sql
CREATE TABLE scan_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    display_name VARCHAR(128) NOT NULL,
    description TEXT,
    default_parameters JSONB DEFAULT '{}',
    tool_preference VARCHAR(64),
    estimated_duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT true
);

INSERT INTO scan_types (name, display_name, description, tool_preference, estimated_duration) VALUES
('host_discovery', 'Host Discovery', 'Discover active hosts in target range', 'masscan', 10),
('quick_scan', 'Quick Port Scan', 'Fast scan of common ports', 'rustscan', 15),
('full_scan', 'Full Port Scan', 'Complete TCP/UDP port scan 1-65535', 'nmap', 60),
('service_detection', 'Service Detection', 'Identify services and versions', 'nmap', 30),
('vulnerability_scan', 'Vulnerability Assessment', 'Comprehensive vulnerability scanning', 'openvas', 120),
('intense_scan', 'Intense Scan', 'In-depth scanning with scripts', 'nmap', 90),
('stealth_scan', 'Stealth Scan', 'Evasion techniques and stealth', 'nmap', 45);
```

#### mitre_techniques
```sql
CREATE TABLE mitre_techniques (
    id VARCHAR(16) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    tactic VARCHAR(64),
    platforms JSONB DEFAULT '["Windows", "Linux", "macOS", "Network"]',
    data_sources JSONB DEFAULT '[]',
    url VARCHAR(512),
    is_subtechnique BOOLEAN DEFAULT false,
    parent_technique VARCHAR(16)
);
```

---

## 5. Index Strategy

### 5.1 Primary Indexes (Already Included in Table Definitions)

### 5.2 Composite Indexes
```sql
-- Vulnerability composite indexes
CREATE INDEX idx_vuln_critical_open 
ON vulnerabilities(engagement_id, risk_rating, status)
WHERE risk_rating IN ('critical', 'high') AND status = 'open';

-- Host composite indexes
CREATE INDEX idx_host_engagement_risk 
ON hosts(engagement_id, risk_score DESC);

-- Evidence composite indexes
CREATE INDEX idx_evidence_sensitive 
ON evidence(engagement_id, sensitivity_level, contains_credentials)
WHERE sensitivity_level IN ('confidential', 'restricted') 
   OR contains_credentials = true;

-- Audit composite indexes
CREATE INDEX idx_audit_critical_actions 
ON audit_logs(timestamp DESC)
WHERE action IN ('execute', 'approve', 'delete', 'emergency_stop');
```

### 5.3 Full-Text Search Indexes
```sql
-- Vulnerability search
CREATE INDEX idx_vuln_search 
ON vulnerabilities USING GIN (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
);

-- Host search
CREATE INDEX idx_host_search 
ON hosts USING GIN (
    to_tsvector('english', coalesce(hostname, '') || ' ' || coalesce(fqdn, ''))
);

-- Evidence search
CREATE INDEX idx_evidence_search 
ON evidence USING GIN (
    to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, ''))
);
```

---

## 6. Evidence Storage Design

### 6.1 Storage Structure
```
evidence/
├── {engagement_id}/
│   ├── {year}/
│   │   ├── {month}/
│   │   │   ├── {day}/
│   │   │   │   ├── screenshots/
│   │   │   │   │   └── {evidence_id}_{hostname}_{timestamp}.png
│   │   │   │   ├── pcaps/
│   │   │   │   │   └── {evidence_id}_{hostname}_{port}_{timestamp}.pcap
│   │   │   │   ├── logs/
│   │   │   │   │   └── {evidence_id}_{tool}_{timestamp}.log
│   │   │   │   ├── credentials/
│   │   │   │   │   └── {evidence_id}_{type}_{timestamp}.txt.enc
│   │   │   │   ├── exploits/
│   │   │   │   │   └── {evidence_id}_{name}_{timestamp}.py
│   │   │   │   ├── certificates/
│   │   │   │   │   └── {evidence_id}_{hostname}_{port}.pem
│   │   │   │   └── other/
│   │   │   │       └── {evidence_id}_{name}_{timestamp}.{ext}
```

### 6.2 Storage Configuration
```yaml
evidence_storage:
  backend: "minio"  # or "s3", "azure", "gcp"
  
  buckets:
    evidence: "anptop-evidence"
    sensitive: "anptop-sensitive"
    public: "anptop-public"
    
  encryption:
    at_rest: AES-256-GCM
    sensitive_files: additional_encryption
    
  access_control:
    evidence_bucket: "authenticated_read"
    sensitive_bucket: "admin_only"
    
  lifecycle:
    evidence_ttl: 365 days
    sensitive_ttl: 730 days
    archive_after: 90 days
```

### 6.3 Evidence Lifecycle
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Evidence Lifecycle                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │Created   │───>│Verified  │───>│Archived  │───>│Deleted   │            │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│        │               │               │               │                  │
│        │               │               │               │                  │
│   ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐               │
│   │ Hash     │    │ Chain    │    │ Compress│    │ Secure  │               │
│   │ Created  │    │ of       │    │ &       │    │ Wipe     │               │
│   │          │    │ Custody  │    │ Encrypt │    │         │               │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Hashing & Immutability Model

### 7.1 Hashing Strategy
```python
# Evidence Hashing Algorithm
def calculate_evidence_hash(file_path, sensitive=False):
    """
    Calculate cryptographic hash for evidence integrity
    """
    # Primary hash (SHA-256)
    sha256_hash = hashlib.sha256()
    
    # Secondary hash (SHA-512 for sensitive)
    sha512_hash = hashlib.sha512()
    
    # Metadata hash
    metadata = {
        'file_size': os.path.getsize(file_path),
        'mime_type': get_mime_type(file_path),
        'created_at': datetime.utcnow().isoformat(),
        'algorithm': 'SHA-256/SHA-512'
    }
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
            if sensitive:
                sha512_hash.update(chunk)
    
    return {
        'sha256': sha256_hash.hexdigest(),
        'sha512': sha512_hash.hexdigest() if sensitive else None,
        'metadata_hash': hashlib.sha256(
            json.dumps(metadata, sort_keys=True).encode()
        ).hexdigest()
    }
```

### 7.2 Chain of Custody
```sql
CREATE TABLE chain_of_custody (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id UUID NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    
    -- Action
    action_type VARCHAR(32) NOT NULL,
    action_description TEXT,
    
    -- From
    from_user UUID REFERENCES users(id),
    from_location VARCHAR(256),
    
    -- To  
    to_user UUID REFERENCES users(id),
    to_location VARCHAR(256),
    
    -- Integrity
    hash_before VARCHAR(64),
    hash_after VARCHAR(64),
    signature TEXT,
    
    -- Context
    reason TEXT,
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_action_type CHECK (action_type IN ('created', 'collected',
                                                          'transferred', 'accessed',
                                                          'verified', 'archived',
                                                          'restored', 'deleted',
                                                          'exported'))
);

CREATE INDEX idx_coc_evidence ON chain_of_custody(evidence_id);
CREATE INDEX idx_coc_timestamp ON chain_of_custody(timestamp DESC);
CREATE INDEX idx_coc_user ON chain_of_custody(to_user);
```

### 7.3 Immutability Rules
```yaml
immutability_rules:
  evidence_immutable: true
  audit_immutable: true
  approval_immutable: true
  
  exceptions:
    - role: CISO
      action: modify_evidence
      requires_audit: true
      
    - role: AUDITOR
      action: reclassify_sensitivity
      requires_justification: true
      
  tamper_detection:
    enabled: true
    check_interval: 3600  # seconds
    alert_on_mismatch: true
```

---

## 8. Retention Policies

### 8.1 Default Retention Periods
```yaml
retention_policies:
  engagement_data:
    default_retention: 365 days
    archive_after: 90 days
    deletion_after: 730 days
    
  evidence:
    default_retention: 365 days
    sensitive_retention: 730 days
    confidential_retention: 1095 days
    
  audit_logs:
    retention: 2555 days  # 7 years for compliance
    
  reports:
    retention: 2555 days
    executive_reports: 2555 days
    
  temporary_scans:
    retention: 30 days
    archive: false
```

### 8.2 Compliance-Based Retention
```sql
-- Create retention policies table
CREATE TABLE retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL UNIQUE,
    description TEXT,
    retention_days INTEGER NOT NULL,
    archive_days INTEGER,
    deletion_days INTEGER,
    applies_to VARCHAR(64)[],
    conditions JSONB DEFAULT '{}',
    compliance_standards JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO retention_policies (name, description, retention_days, archive_days, deletion_days, compliance_standards) VALUES
('standard_engagement', 'Standard engagement data', 365, 90, 730, NULL, NULL),
('pci_engagement', 'PCI-DSS compliant engagement', 2555, 365, 2920, NULL, 'PCI-DSS'),
('hipaa_engagement', 'HIPAA compliant engagement', 2555, 365, 2920, NULL, 'HIPAA'),
('sox_engagement', 'SOX compliant engagement', 2555, 365, 2920, NULL, 'SOX'),
('evidence_sensitive', 'Sensitive evidence', 730, 180, 1095, NULL, NULL),
('evidence_confidential', 'Confidential evidence', 1095, 365, 2555, NULL, NULL);
```

### 8.3 Retention Enforcement
```python
# Retention enforcement job
def enforce_retention_policies():
    """
    Run daily to enforce retention policies
    """
    # Mark expired evidence for deletion
    UPDATE evidence
    SET deletion_requested = true,
        updated_at = NOW()
    WHERE retention_until < NOW()
      AND deletion_requested = false;
    
    # Archive old engagement data
    SELECT * FROM engagements
    WHERE status = 'completed'
      AND completed_at < NOW() - INTERVAL '90 days';
    
    # Export audit logs for compliance
    SELECT * FROM audit_logs
    WHERE timestamp < NOW() - INTERVAL '2555 days';
```

---

## 9. SQL Schema (Complete)

### 9.1 Complete Schema File
```sql
-- ANPTOP Database Schema v1.0
-- PostgreSQL 15+
-- Designed for ACID compliance and audit integrity

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Custom types
CREATE TYPE engagement_status AS ENUM (
    'draft', 'pending_approval', 'approved', 
    'in_progress', 'paused', 'completed', 
    'cancelled', 'archived'
);

CREATE TYPE scan_status AS ENUM (
    'pending', 'queued', 'running', 
    'paused', 'completed', 'failed', 
    'cancelled', 'timeout'
);

CREATE TYPE vuln_status AS ENUM (
    'open', 'in_progress', 'resolved', 
    'accepted', 'false_positive', 
    'reopened', 'closed'
);

CREATE TYPE risk_rating AS ENUM (
    'critical', 'high', 'medium', 
    'low', 'informational', 'none'
);

CREATE TYPE approval_status AS ENUM (
    'pending', 'approved', 'rejected', 
    'expired', 'escalated', 'cancelled'
);

-- Full schema would continue here...
-- (All tables defined above are included in the complete schema)

-- Views
CREATE VIEW engagement_summary AS
SELECT 
    e.id,
    e.name,
    e.client_name,
    e.status,
    e.start_date,
    e.end_date,
    COUNT(DISTINCT h.id) as host_count,
    COUNT(DISTINCT v.id) as vuln_count,
    COUNT(DISTINCT CASE WHEN v.risk_rating = 'critical' THEN v.id END) as critical_count,
    COUNT(DISTINCT CASE WHEN v.risk_rating = 'high' THEN v.id END) as high_count,
    COUNT(DISTINCT e2.id) as exploit_count
FROM engagements e
LEFT JOIN hosts h ON h.engagement_id = e.id
LEFT JOIN vulnerabilities v ON v.engagement_id = e.id
LEFT JOIN exploits e2 ON e2.engagement_id = e.id
GROUP BY e.id;

CREATE VIEW vuln_summary AS
SELECT 
    engagement_id,
    risk_rating,
    status,
    COUNT(*) as count
FROM vulnerabilities
GROUP BY engagement_id, risk_rating, status;

-- Functions
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_engagements_updated_at
    BEFORE UPDATE ON engagements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_hosts_updated_at
    BEFORE UPDATE ON hosts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_vulnerabilities_updated_at
    BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_exploits_updated_at
    BEFORE UPDATE ON exploits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_evidence_updated_at
    BEFORE UPDATE ON evidence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 9.2 Migration Scripts Location
```
migrations/
├── versions/
│   ├── 001_initial_schema.sql
│   ├── 002_add_mitre_mapping.sql
│   ├── 003_enhance_audit.sql
│   └── 004_add_retention.sql
├── alembic.ini
└── env.py
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
