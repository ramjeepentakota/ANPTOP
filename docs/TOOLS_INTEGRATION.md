# ANPTOP - Tools Integration Summary

## Overview
This document provides a comprehensive summary of all security tools integrated into ANPTOP and their n8n workflow integration points.

---

## 1. Discovery Tools

### 1.1 Host Discovery Tools
| Tool | Purpose | Integration Point | Protocol |
|------|---------|-------------------|----------|
| **Masscan** | Ultra-fast port scanner for initial host discovery | [`Workflow 2: Host Discovery`](N8N_WORKFLOWS.md#workflow-2-host-discovery) | TCP SYN |
| **RustScan** | Fast port scanner for responsive hosts | [`Workflow 2: Host Discovery`](N8N_WORKFLOWS.md#workflow-2-host-discovery) | TCP SYN |
| **Nmap** | Network mapper with ping sweep capabilities | [`Workflow 2: Host Discovery`](N8N_WORKFLOWS.md#workflow-2-host-discovery) | ICMP, TCP ACK, TCP SYN |
| **Unicornscan** | Async stateless port scanner | [`Workflow 2: Host Discovery`](N8N_WORKFLOWS.md#workflow-2-host-discovery) | TCP, UDP |

### 1.2 DNS Enumeration Tools
| Tool | Purpose | Integration Point |
|------|---------|-------------------|
| **dnsrecon** | DNS enumeration and zone transfers | Workflow 2 - Passive Reconnaissance |
| **dnschef** | DNS proxy for enumeration | Workflow 2 - Active Reconnaissance |
| **theHarvester** | OSINT gathering for targets | Workflow 2 - Target Intake |

---

## 2. Scanning Tools

### 2.1 Port Scanning Tools
| Tool | Purpose | Ports Scanned | Integration |
|------|---------|----------------|-------------|
| **Masscan** | Full port scan (1-65535) | All TCP ports | n8n Execute Command Node |
| **RustScan** | Fast port scan | Common ports | n8n Execute Command Node |
| **Nmap** | Comprehensive port scan | 1-65535 TCP/UDP | n8n Execute Command Node |
| **Unicornscan** | Async port scan | All ports | n8n Execute Command Node |

### 2.2 Service Detection Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Nmap** | Service version detection (-sV) | [`Workflow 4: Service Detection`](N8N_WORKFLOWS.md#workflow-4-service--version-detection) |
| **Amass** | Subdomain enumeration | Workflow 2 - Target Discovery |
| **Sublist3r** | Subdomain finder | Workflow 2 - Target Discovery |

---

## 3. Enumeration Tools

### 3.1 Nmap NSE Scripts Integration
```python
# Dynamic NSE Script Selection based on discovered ports
SCRIPT_MAPPING = {
    21: ['ftp-anon', 'ftp-bounce', 'ftp-proftpd-backdoor'],
    22: ['ssh-auth-methods', 'ssh2-enum-algos', 'ssh-hostkey'],
    23: ['telnet-encryption', 'telnet-ntlm-info'],
    25: ['smtp-commands', 'smtp-enum-users', 'smtp-ntlm-info'],
    53: ['dns-brute', 'dns-cache-snoop', 'dns-nsec3'],
    80: ['http-headers', 'http-methods', 'http-title', 'http-robots.txt'],
    110: ['pop3-capabilities', 'pop3-ntlm-info'],
    111: ['rpcinfo', 'rpc-grind'],
    135: ['msrpc-enum'],
    139: ['smb-enum-shares', 'smb-enum-users', 'smb-os-discovery'],
    443: ['ssl-cert', 'ssl-date', 'tls-heartbleed', 'http-headers'],
    445: ['smb-enum-shares', 'smb-enum-users', 'smb-os-discovery', 'smb-vuln-ms17-010'],
    993: ['imap-capabilities', 'imap-ntlm-info'],
    995: ['pop3-capabilities', 'pop3-ntlm-info'],
    1433: ['ms-sql-info', 'ms-sql-empty-password', 'ms-sql-brute'],
    1521: ['oracle-tns-version', 'oracle-enum-users'],
    3306: ['mysql-info', 'mysql-enum', 'mysql-empty-password'],
    3389: ['rdp-enum-encryption', 'rdp-ntlm-info'],
    5432: ['pgsql-info', 'postgres-enum-users'],
    5900: ['vnc-info', 'realvnc-auth-bypass'],
    8080: ['http-headers', 'http-methods', 'http-title', 'http-proxy']
}
```

### 3.2 Web Application Enumeration
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Nikto** | Web server vulnerability scanner | Workflow 5 - Dynamic Enumeration |
| **Gobuster** | Directory/file brute-forcing | Workflow 5 - Web Enumeration |
| **Dirsearch** | Path discovery | Workflow 5 - Web Enumeration |
| **WPScan** | WordPress vulnerability scanner | Workflow 5 - CMS Enumeration |
| **CMSmap** | CMS vulnerability scanner | Workflow 5 - CMS Enumeration |

### 3.3 Network Enumeration
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Enum4linux** | SMB enumeration | Workflow 5 - SMB Enumeration |
| **SMBClient** | SMB/CIFS access | Workflow 5 - SMB Enumeration |
| **RPCClient** | RPC enumeration | Workflow 5 - RPC Enumeration |
| **SNMPWalk** | SNMP enumeration | Workflow 5 - SNMP Enumeration |
| **Onesixtyone** | SNMP scanner | Workflow 5 - SNMP Enumeration |

---

## 4. Vulnerability Assessment Tools

### 4.1 Primary VA Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **OpenVAS** | Comprehensive vulnerability scanner | [`Workflow 6: OpenVAS Assessment`](N8N_WORKFLOWS.md#workflow-6-openvas-vulnerability-assessment) |
| **Greenbone Community Edition** | OpenVAS frontend/manager | OMP Protocol Integration |
| **Nessus** | Commercial vulnerability scanner (optional) | API Integration |
| **Nuclei** | Template-based vulnerability scanner | Workflow 6 - Additional Scans |

### 4.2 OpenVAS Integration Details
```yaml
openvas_config:
  host: "openvas:9392"
  protocol: "OMP"  # OpenVAS Management Protocol
  credentials:
    username: "admin"
    password: "admin"
    
  scan_configs:
    - name: "Full and Fast"
      oid: "daba56c8-73ec-11df-a475-002264764cea"
      
    - name: "Full and Fast Ultimate"
      oid: "69869169-28ca-46b5-961c-5a51e81c1e3d"
      
    - name: "Host Discovery"
      oid: "1d61db57-7047-11e2-98b9-0021862c3e0e"
```

### 4.3 Specialized Scanners
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Nuclei** | Template-based scanning | Workflow 6 - Custom Templates |
| **XSSer** | XSS vulnerability scanner | Workflow 6 - Web VA |
| **SQLMap** | SQL injection scanner | Workflow 6 - Web VA |
| **SSLScan** | SSL/TLS vulnerability scanner | Workflow 6 - SSL Assessment |
| **TestSSL** | TLS configuration testing | Workflow 6 - SSL Assessment |

---

## 5. Exploitation Tools

### 5.1 Primary Exploitation Framework
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Metasploit Framework** | Exploitation and post-exploitation | [`Workflow 9: Exploitation Execution`](N8N_WORKFLOWS.md#workflow-9-exploitation-execution-workflow) |
| **Metasploit RPC** | Remote API for automation | n8n HTTP Request Node |
| **Meterpreter** | Advanced post-exploitation payload | Session Management |

### 5.2 Metasploit Integration
```python
# Exploitation command construction
MSF_COMMANDS = {
    'exploit_modules': {
        'windows/smb/ms17_010_eternalblue': {
            'rport': 445,
            'payload': 'windows/x64/meterpreter/reverse_tcp'
        },
        'exploit/multi/http/jenkins_script_console': {
            'rport': 8080,
            'payload': 'java/meterpreter/reverse_tcp'
        }
    },
    'post_modules': {
        'windows/gather/enum_domains': 'Domain enumeration',
        'windows/gather/credentials/vnc': 'VNC credential harvesting',
        'linux/gather/enum_network': 'Network enumeration'
    }
}
```

### 5.3 Auxiliary Exploitation Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **CrackMapExec** | Network exploitation toolkit | [`Workflow 11: Lateral Movement`](N8N_WORKFLOWS.md#workflow-11-lateral-movement-approval--execution) |
| **Responder** | LLMNR/NBT-NS poisoning | Workflow 10 - Credential Harvesting |
| **Impacket** | Python exploitation library | Direct Python Integration |
| **PowerSploit** | PowerShell exploitation | Metasploit Session Integration |
| **Empire** | PowerShell C2 (optional) | API Integration |

---

## 6. Post-Exploitation Tools

### 6.1 Credential Harvesting Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Mimikatz** | Windows credential extraction | Workflow 10 - Session Commands |
| **Secretsdump** | SAM database extraction | Workflow 10 - Session Commands |
| **LaZagne** | Multi-platform credential recovery | Workflow 10 - Cross-Platform |
| **KeePass** | Password database extraction | Workflow 10 - Data Discovery |

### 6.2 Data Discovery & Collection
| Tool | Purpose | Integration |
|------|---------|-------------|
| **BloodHound** | Active Directory mapping | [`Workflow 10: Post-Exploitation`](N8N_WORKFLOWS.md#workflow-10-post-exploitation-approval--execution) |
| **SharpHound** | BloodHound data collector | Windows Session Integration |
| **PowerView** | Active Directory enumeration | Workflow 10 - AD Enumeration |
| **Snaffler** | Share file discovery | Workflow 10 - Data Discovery |

### 6.3 Privilege Escalation Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **PowerUp** | Windows privilege escalation | Workflow 10 - PrivEsc |
| **Windows-Exploit-Suggester** | Windows kernel exploits | Workflow 10 - PrivEsc |
| **Linux-Exploit-Suggester** | Linux kernel exploits | Workflow 10 - PrivEsc |
| **Sherlock** | Windows missing patches | Workflow 10 - Vulnerability ID |

---

## 7. Lateral Movement Tools

### 7.1 Windows Lateral Movement
| Tool | Technique | Integration |
|------|-----------|-------------|
| **CrackMapExec** | WMIExec | [`Workflow 11: Lateral Movement`](N8N_WORKFLOWS.md#workflow-11-lateral-movement-approval--execution) |
| **CrackMapExec** | PsExec | Workflow 11 |
| **CrackMapExec** | SMBExec | Workflow 11 |
| **atexec** | Scheduled Task | Workflow 11 |
| **dcomexec** | DCOM Execution | Workflow 11 |

### 7.2 Linux Lateral Movement
| Tool | Purpose | Integration |
|------|---------|-------------|
| **SSH** | SSH pivot | Workflow 11 - SSH Lateral |
| **Ansible** | Configuration management pivot | Workflow 11 - Ansible Pivot |
| **rsync** | Data exfiltration | Workflow 11 - Data Transfer |

### 7.3 Database Lateral Movement
| Tool | Purpose | Integration |
|------|---------|-------------|
| **PowerUpSQL** | SQL Server pivot | Workflow 11 - Database |
| **mssqlclient** | MSSQL client | Workflow 11 - MSSQL |
| **Sqsh** | Sybase client | Workflow 11 - Database |

---

## 8. Evidence Collection Tools

### 8.1 Evidence Collection Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **Tcpdump** | Network packet capture | [`Workflow 12: Evidence Collection`](N8N_WORKFLOWS.md#workflow-12-evidence-collection-workflow) |
| **Wireshark** | Packet analysis | Workflow 12 |
| **Screenshooter** | Screenshot capture | Workflow 12 |
| **Bulk Extractor** | File carving | Workflow 12 - File Discovery |

### 8.2 Hash Calculation Tools
| Tool | Purpose | Integration |
|------|---------|-------------|
| **sha256sum** | SHA-256 hashing | [`Workflow 12: Evidence Collection`](N8N_WORKFLOWS.md#workflow-12-evidence-collection-workflow) |
| **sha512sum** | SHA-512 hashing | Workflow 12 - Sensitive Evidence |
| **md5sum** | MD5 hashing | Workflow 12 - Legacy Support |

---

## 9. n8n Tool Integration Architecture

### 9.1 n8n Workflow Integration Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           n8n Workflow Engine                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      TOOL INTEGRATION LAYER                           │  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │  Execute    │  │   HTTP       │  │   Script    │             │  │
│  │  │  Command    │  │   Request    │  │   Node      │             │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Tool Wrappers                               │ │  │
│  │  │                                                                 │ │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │ │  │
│  │  │  │ Nmap     │ │Masscan  │ │Metasploit│ │OpenVAS   │        │ │  │
│  │  │  │ Wrapper  │ │Wrapper  │ │ Wrapper  │ │ Wrapper  │        │ │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │ │  │
│  │  │                                                                 │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Tool Configuration in n8n

#### Execute Command Node Configuration
```json
{
  "name": "Execute Nmap Scan",
  "type": "n8n-nodes-base.executeCommand",
  "parameters": {
    "command": "nmap -sV --script={{$node['Port Scan Type'].json['nse_scripts']}} -oN {{$node['Output File'].json['path']}} {{$node['Target'].json['ip']}}",
    "timeout": 300,
    "options": {
      "workingDirectory": "/tmp/anptop/scans"
    }
  }
}
```

#### HTTP Request Node Configuration (Metasploit RPC)
```json
{
  "name": "Create Metasploit Session",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "post",
    "url": "={{$node['Metasploit Config'].json['rpc_url']}}/api/1.0/session.create",
    "authentication": "basicAuth",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "LHOST",
          "value": "={{$node['Listener Config'].json['lhost']}}"
        },
        {
          "name": "LPORT",
          "value": "={{$node['Listener Config'].json['lport']}}"
        }
      ]
    }
  }
}
```

---

## 10. Complete Tool List Summary

### 10.1 Discovery Tools (6)
| Category | Tools |
|----------|-------|
| Host Discovery | Masscan, RustScan, Nmap, Unicornscan |
| DNS Enumeration | dnsrecon, dnschef, theHarvester |

### 10.2 Scanning Tools (8)
| Category | Tools |
|----------|-------|
| Port Scanning | Masscan, RustScan, Nmap, Unicornscan |
| Service Detection | Nmap, Amass, Sublist3r |
| Web Scanning | Nikto, Gobuster, Dirsearch |

### 10.3 Enumeration Tools (15)
| Category | Tools |
|----------|-------|
| Network Enumeration | Enum4linux, SMBClient, RPCClient |
| SNMP Enumeration | SNMPWalk, Onesixtyone |
| Web Enumeration | Gobuster, Dirsearch, WPScan, CMSmap |
| AD Enumeration | BloodHound, SharpHound, PowerView |

### 10.4 Vulnerability Assessment Tools (10)
| Category | Tools |
|----------|-------|
| Primary Scanners | OpenVAS, Greenbone CE, Nessus, Nuclei |
| Web VA | XSSer, SQLMap, Nikto |
| SSL Testing | SSLScan, TestSSL |

### 10.5 Exploitation Tools (8)
| Category | Tools |
|----------|-------|
| Primary Framework | Metasploit Framework, Metasploit RPC |
| Exploitation Utils | CrackMapExec, Responder, Impacket |
| Advanced C2 | Empire, PowerSploit |

### 10.6 Post-Exploitation Tools (12)
| Category | Tools |
|----------|-------|
| Credential Harvesting | Mimikatz, Secretsdump, LaZagne |
| Data Discovery | BloodHound, Snaffler, PowerUp |
| Privilege Escalation | PowerUp, Windows-Exploit-Suggester |
| Session Management | Meterpreter, PowerShell Empire |

### 10.7 Lateral Movement Tools (10)
| Category | Tools |
|----------|-------|
| Windows | WMIExec, PsExec, SMBExec, atexec, dcomexec |
| Linux | SSH, Ansible, rsync |
| Database | PowerUpSQL, mssqlclient, Sqsh |

### 10.8 Evidence Collection Tools (6)
| Category | Tools |
|----------|-------|
| Network Capture | Tcpdump, Wireshark |
| Evidence Capture | Screenshooter, Bulk Extractor |
| Hashing | sha256sum, sha512sum |

---

## 11. Total Tool Count

| Category | Count |
|----------|-------|
| Discovery Tools | 6 |
| Scanning Tools | 8 |
| Enumeration Tools | 15 |
| Vulnerability Assessment Tools | 10 |
| Exploitation Tools | 8 |
| Post-Exploitation Tools | 12 |
| Lateral Movement Tools | 10 |
| Evidence Collection Tools | 6 |
| **TOTAL** | **75 Tools** |

---

## 12. Integration Status

| Integration Type | Status | Details |
|-----------------|--------|---------|
| n8n Execute Command | ✅ Implemented | All CLI tools |
| n8n HTTP Request | ✅ Implemented | API-based tools (Metasploit RPC, OpenVAS OMP) |
| n8n Script Node | ✅ Implemented | Python/JS script execution |
| Webhook Triggers | ✅ Implemented | Tool completion notifications |
| Redis Queue | ✅ Implemented | Async tool execution |

---

**Document Version**: 1.1  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
