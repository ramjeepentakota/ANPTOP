# ANPTOP - Complete Tools Integration Summary (Fintech Edition)

## Executive Summary
**Total Tools: 196** (Original: 75 + Fintech Additions: 121)  
**Total n8n Workflows: 21** (Original: 13 + New: 8)

---

## Complete Tools Catalog

### Category 1: Discovery Tools (14 Tools)

#### Network Discovery (4)
| Tool | Version | Purpose | n8n Integration |
|------|---------|---------|-----------------|
| Masscan | Latest | Ultra-fast TCP port scanner | Execute Command Node |
| RustScan | Latest | Fast port scanner (10x Nmap) | Execute Command Node |
| Nmap | 7.94+ | Network mapper and port scanner | Execute Command Node |
| Unicornscan | Latest | Async stateless scanner | Execute Command Node |

#### DNS Enumeration (3)
| Tool | Version | Purpose | n8n Integration |
|------|---------|---------|-----------------|
| dnsrecon | Latest | DNS enumeration and zone transfers | Execute Command Node |
| dnschef | Latest | DNS proxy for enumeration | Execute Command Node |
| theHarvester | Latest | OSINT gathering for targets | Execute Command Node |

#### Cloud Discovery (7)
| Tool | Version | Purpose | n8n Integration |
|------|---------|---------|-----------------|
| AWS CLI | Latest | AWS resource enumeration | Execute Command Node |
| Azure CLI (az) | Latest | Azure resource enumeration | Execute Command Node |
| gcloud | Latest | GCP resource enumeration | Execute Command Node |
| Cloud Mapper | Latest | Cloud network visualization | Execute Command Node |
| SkyArk | Latest | Cloud asset discovery | Execute Command Node |
| Cloudelist | Latest | Cloud service enumeration | Execute Command Node |
| AWSume | Latest | AWS role credential management | Execute Command Node |

---

### Category 2: Scanning Tools (14 Tools)

#### Port Scanning (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Masscan | Latest | Full TCP/UDP port scan (1-65535) | Execute Command Node |
| RustScan | Latest | Fast port scan with Nmap integration | Execute Command Node |
| Nmap | 7.94+ | Comprehensive port and service scan | Execute Command Node |
| Unicornscan | Latest | Async port scanning | Execute Command Node |

#### Service Detection (3)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Nmap | 7.94+ | Service version detection (-sV) | Execute Command Node |
| Amass | Latest | Subdomain enumeration | Execute Command Node |
| Sublist3r | Latest | Subdomain finder | Execute Command Node |

#### Cloud Security Scanning (7)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| ScoutSuite | Latest | Multi-cloud security scanner | Execute Command Node |
| Prowler | Latest | AWS CIS benchmark scanner | Execute Command Node |
| AWS Inspector | Latest | AWS vulnerability assessment | Execute Command Node |
| Azure Security Center | Latest | Azure security scanning | Execute Command Node |
| GCP Security Command Center | Latest | GCP security assessment | Execute Command Node |
| Cloud Custodian | Latest | Cloud resource policy enforcement | Execute Command Node |
| Trivy | Latest | Container vulnerability scanner | Execute Command Node |

---

### Category 3: Enumeration Tools (35 Tools)

#### Network Enumeration (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Enum4linux | Latest | SMB/CIFS enumeration | Execute Command Node |
| SMBClient | Latest | SMB file share access | Execute Command Node |
| RPCClient | Latest | RPC endpoint enumeration | Execute Command Node |
| SNMPWalk | Latest | SNMP OID enumeration | Execute Command Node |

#### Web Enumeration (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Gobuster | Latest | Directory/file brute-forcing | Execute Command Node |
| Dirsearch | Latest | Web path discovery | Execute Command Node |
| WPScan | Latest | WordPress vulnerability scanner | Execute Command Node |
| CMSmap | Latest | CMS vulnerability scanner | Execute Command Node |

#### Active Directory (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| BloodHound | Latest | AD attack path mapping | Execute Command Node |
| SharpHound | Latest | BloodHound data collector | Execute Command Node |

#### API Security (8)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Burp Suite | Latest | Web API testing proxy | HTTP Request Node |
| OWASP ZAP | Latest | Automated API vulnerability scanner | Execute Command Node |
| Postman | Latest | API testing and automation | Execute Command Node |
| HTTPie | Latest | User-friendly HTTP client | Execute Command Node |
| curl | Latest | Command-line HTTP client | Execute Command Node |
| jq | Latest | JSON data processing | Execute Command Node |
| jwt_tool | Latest | JWT token testing | Execute Command Node |
| API Fuzzer | Latest | API fuzzing | Execute Command Node |

#### Cloud Enumeration (13)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Pacu | Latest | AWS exploitation framework | Execute Command Node |
| Cloud Fox | Latest | Cloud attack surface mapping | Execute Command Node |
| AzureHound | Latest | Azure AD enumeration | Execute Command Node |
| ROADtools | Latest | Azure AD exploration | Execute Command Node |
| Azure PowerShell | Latest | Azure enumeration | Execute Command Node |
| AWS VPC | Latest | VPC enumeration | Execute Command Node |
| GCP IAM | Latest | GCP IAM enumeration | Execute Command Node |
| s3recon | Latest | S3 bucket enumeration | Execute Command Node |
| k8s_enum | Latest | Kubernetes enumeration | Execute Command Node |
| kubeconfig | Latest | Kubeconfig analysis | Execute Command Node |
| AWS IAM | Latest | IAM policy enumeration | Execute Command Node |
| Azure AD | Latest | Azure AD enumeration | Execute Command Node |
| GCP Compute | Latest | GCP compute enumeration | Execute Command Node |

#### Kubernetes (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| kubectl | Latest | Kubernetes CLI | Execute Command Node |
| kubectx | Latest | K8s context switching | Execute Command Node |
| kubens | Latest | K8s namespace switching | Execute Command Node |
| kubeletctl | Latest | Kubelet enumeration | Execute Command Node |

---

### Category 4: Vulnerability Assessment (22 Tools)

#### Primary VA (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| OpenVAS | Latest | Comprehensive vulnerability scanner | HTTP Request (OMP) |
| Greenbone CE | Latest | OpenVAS frontend/manager | HTTP Request (OMP) |
| Nessus | Latest | Commercial vulnerability scanner (optional) | HTTP Request API |
| Nuclei | Latest | Template-based vulnerability scanner | Execute Command Node |

#### Web VA (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| XSSer | Latest | XSS vulnerability scanner | Execute Command Node |
| SQLMap | Latest | SQL injection scanner | Execute Command Node |
| Nikto | Latest | Web server vulnerability scanner | Execute Command Node |
| SSLScan | Latest | SSL/TLS vulnerability scanner | Execute Command Node |

#### Cloud VA (10)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| ScoutSuite | Latest | Multi-cloud security scanner | Execute Command Node |
| Prowler | Latest | AWS CIS benchmark | Execute Command Node |
| checkov | Latest | IaC security scanning | Execute Command Node |
| terrascan | Latest | Terraform security scanning | Execute Command Node |
| Trivy | Latest | Container image scanning | Execute Command Node |
| Grype | Latest | SBOM vulnerability scanner | Execute Command Node |
| Clair | Latest | Container image analysis | Execute Command Node |
| Anchore | Latest | Container security analysis | Execute Command Node |
| AWS Inspector | Latest | AWS vulnerability assessment | Execute Command Node |
| Cloud Custodian | Latest | Policy enforcement | Execute Command Node |

#### Kubernetes VA (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| kube-hunter | Latest | K8s penetration testing | Execute Command Node |
| kube-bench | Latest | CIS K8s benchmark | Execute Command Node |
| Falco | Latest | Runtime security detection | Execute Command Node |
| OPA Gatekeeper | Latest | Policy enforcement | Execute Command Node |

---

### Category 5: Exploitation (23 Tools)

#### Primary Framework (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Metasploit Framework | Latest | Exploitation and post-exploitation | Execute Command Node |
| Metasploit RPC | Latest | Remote API automation | HTTP Request Node |

#### Exploitation Utils (3)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| CrackMapExec | Latest | Network exploitation toolkit | Execute Command Node |
| Responder | Latest | LLMNR/NBT-NS poisoning | Execute Command Node |
| Impacket | Latest | Python exploitation library | Python Script Node |

#### Cloud Exploitation (13)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Pacu | Latest | AWS exploitation framework | Execute Command Node |
| Cloud Fox | Latest | Cloud attack surface | Execute Command Node |
| AWS Exploit | Latest | AWS-specific exploits | Execute Command Node |
| Azure Exploit | Latest | Azure-specific exploits | Execute Command Node |
| GCP Exploit | Latest | GCP-specific exploits | Execute Command Node |
| Cloud PrivEsc | Latest | Cloud privilege escalation | Execute Command Node |
| AWS IAM Exploit | Latest | IAM vulnerability exploitation | Execute Command Node |
| Azure AD Exploit | Latest | Azure AD exploitation | Execute Command Node |
| S3 Exploit | Latest | S3 bucket exploitation | Execute Command Node |
| Lambda Exploit | Latest | Lambda function injection | Execute Command Node |
| Cloudbrute | Latest | Cloud asset brute-forcing | Execute Command Node |
| AWS VPC Exploit | Latest | VPC endpoint exploitation | Execute Command Node |
| KMS Exploit | Latest | Key management service exploitation | Execute Command Node |

#### C2 Frameworks (5)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Sliver | Latest | Open source C2 framework | Execute Command Node |
| Covenant | Latest | .NET C2 framework | Execute Command Node |
| Havoc | Latest | Modern C2 framework | Execute Command Node |
| Mythic | Latest | Cross-platform C2 | Execute Command Node |
| Merlin | Latest | Golang C2 framework | Execute Command Node |

---

### Category 6: Post-Exploitation (30 Tools)

#### Credential Harvesting (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Mimikatz | Latest | Windows credential extraction | Execute Command Node |
| Secretsdump | Latest | SAM/LSADump extraction | Execute Command Node |
| LaZagne | Latest | Multi-platform credential recovery | Execute Command Node |
| KeePass | Latest | Password database extraction | Execute Command Node |

#### Data Discovery (3)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| BloodHound | Latest | AD attack path mapping | Execute Command Node |
| Snaffler | Latest | Share file discovery | Execute Command Node |
| PowerUp | Latest | Windows privilege escalation | Execute Command Node |

#### Cloud Post-Exploitation (15)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Pacu | Latest | AWS post-exploitation | Execute Command Node |
| AWS Keys | Latest | AWS credential harvesting | Execute Command Node |
| Azure Keys | Latest | Azure credential harvesting | Execute Command Node |
| GCP Keys | Latest | GCP credential harvesting | Execute Command Node |
| Gitleaks | Latest | Git repository secrets detection | Execute Command Node |
| TruffleHog | Latest | Git secrets scanning | Execute Command Node |
| AWS SSM | Latest | Systems Manager execution | Execute Command Node |
| AWS Lambda | Latest | Lambda function enumeration | Execute Command Node |
| Azure Functions | Latest | Azure function access | Execute Command Node |
| CloudTrail | Latest | CloudTrail log analysis | Execute Command Node |
| AWS Secrets | Latest | Secrets Manager enumeration | Execute Command Node |
| Azure Key Vault | Latest | Key vault access | Execute Command Node |
| GCP Secret Manager | Latest | Secret manager access | Execute Command Node |
| Cloud Metadata | Latest | Instance metadata enumeration | Execute Command Node |
| Role Tricks | Latest | IAM role chain exploitation | Execute Command Node |

#### Kubernetes Post-Exploitation (8)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Peirates | Latest | Kubernetes exploitation | Execute Command Node |
| kubectl | Latest | K8s command execution | Execute Command Node |
| helm | Latest | K8s package manager | Execute Command Node |
| k9s | Latest | K8s CLI dashboard | Execute Command Node |
| stern | Latest | K8s log tailing | Execute Command Node |
| kubens | Latest | K8s namespace access | Execute Command Node |
| privileged | Latest | K8s privilege escalation | Execute Command Node |
| Service Account | Latest | SA token abuse | Execute Command Node |

---

### Category 7: Lateral Movement (22 Tools)

#### Windows (5)
| Tool | Version | Technique | Integration |
|------|---------|-----------|-------------|
| WMIExec | Latest | WMI lateral movement | Execute Command Node |
| PsExec | Latest | Remote execution | Execute Command Node |
| SMBExec | Latest | SMB execution | Execute Command Node |
| atexec | Latest | Scheduled task lateral | Execute Command Node |
| dcomexec | Latest | DCOM execution | Execute Command Node |

#### Linux (3)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| SSH | Latest | SSH pivot | Execute Command Node |
| Ansible | Latest | Ansible pivot | Execute Command Node |
| rsync | Latest | Data transfer | Execute Command Node |

#### Database (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| PowerUpSQL | Latest | SQL Server pivot | Execute Command Node |
| mssqlclient | Latest | MSSQL client | Execute Command Node |

#### Cloud Lateral (8)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| AWS SSM | Latest | Systems Manager lateral | Execute Command Node |
| AWS Session Manager | Latest | Session management | Execute Command Node |
| AWS RDS | Latest | Database lateral | Execute Command Node |
| Azure VM Run | Latest | Azure VM execution | Execute Command Node |
| Azure Automation | Latest | Azure automation | Execute Command Node |
| GCP Compute | Latest | GCP compute access | Execute Command Node |
| Cross-Account | Latest | Cross-account access | Execute Command Node |
| Role Chaining | Latest | IAM role chaining | Execute Command Node |

#### Kubernetes Lateral (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| kubectl | Latest | K8s pod lateral | Execute Command Node |
| Service Account | Latest | SA token abuse | Execute Command Node |
| Pod Escape | Latest | Container escape | Execute Command Node |
| Cluster Admin | Latest | K8s privilege escalation | Execute Command Node |

---

### Category 8: Evidence Collection (12 Tools)

#### Network Capture (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Tcpdump | Latest | Packet capture | Execute Command Node |
| Wireshark | Latest | Packet analysis | Execute Command Node |

#### Evidence Capture (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Screenshooter | Latest | Screenshot capture | Execute Command Node |
| Bulk Extractor | Latest | File carving | Execute Command Node |

#### Hashing (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| sha256sum | Latest | SHA-256 hashing | Execute Command Node |
| sha512sum | Latest | SHA-512 hashing | Execute Command Node |

#### Cloud Logs (6)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| AWS Logs | Latest | CloudTrail evidence | Execute Command Node |
| Azure Logs | Latest | Azure activity logs | Execute Command Node |
| GCP Logs | Latest | Cloud audit logs | Execute Command Node |
| Kubernetes Logs | Latest | K8s audit logs | Execute Command Node |
| Payment Logs | Latest | Payment transaction logs | Execute Command Node |
| Blockchain Logs | Latest | Smart contract logs | Execute Command Node |

---

### Category 9: Payment Systems (10 Tools)

#### Payment Gateways (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Stripe CLI | Latest | Stripe API testing | Execute Command Node |
| PayPal SDK | Latest | PayPal testing | Execute Command Node |
| Braintree SDK | Latest | Braintree testing | Execute Command Node |
| Square SDK | Latest | Square payment testing | Execute Command Node |

#### PCI-DSS Compliance (6)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| PCI DSS Scanner | Latest | Compliance scanning | Execute Command Node |
| Card Data Discovery | Latest | PAN/CVV discovery | Execute Command Node |
| Encryption Validator | Latest | Encryption verification | Execute Command Node |
| Tokenization Checker | Latest | Tokenization validation | Execute Command Node |
| HashiCorp Vault | Latest | Secrets management | Execute Command Node |
| TLS Config | Latest | TLS configuration testing | Execute Command Node |

---

### Category 10: API Security (8 Tools)

#### REST API (5)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Burp Suite | Latest | Web API testing | HTTP Proxy Node |
| OWASP ZAP | Latest | Automated API scanning | Execute Command Node |
| Postman | Latest | API testing automation | Execute Command Node |
| HTTPie | Latest | HTTP client | Execute Command Node |
| curl | Latest | Command-line HTTP | Execute Command Node |

#### API Security (3)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| jwt_tool | Latest | JWT token testing | Execute Command Node |
| API Fuzzer | Latest | API fuzzing | Execute Command Node |
| GraphQL | Latest | GraphQL introspection | Execute Command Node |

---

### Category 11: Blockchain Security (6 Tools)

#### Smart Contract (4)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Mythril | Latest | Solidity analysis | Execute Command Node |
| Slither | Latest | Static analysis | Execute Command Node |
| Echidna | Latest | Smart contract fuzzing | Execute Command Node |
| Manticore | Latest | Symbolic execution | Execute Command Node |

#### Blockchain (2)
| Tool | Version | Purpose | Integration |
|------|---------|---------|-------------|
| Web3.py | Latest | Ethereum interaction | Python Script Node |
| BTC RPC | Latest | Bitcoin node testing | Execute Command Node |

---

## n8n Workflow Integration

### Workflow 14: Cloud Discovery
```yaml
name: cloud-discovery
trigger: API webhook
tools: AWS CLI, Azure CLI, gcloud, Pacu
outputs: Cloud assets, IAM policies, S3 buckets
```

### Workflow 15: Cloud Vulnerability Assessment
```yaml
name: cloud-va
trigger: Scheduled
tools: ScoutSuite, Prowler, Trivy, checkov
outputs: Vulnerability report
```

### Workflow 16: Cloud Exploitation
```yaml
name: cloud-exploitation
trigger: Approval required
tools: Pacu, Cloud Fox, AWS Exploit
outputs: Cloud sessions, credentials
```

### Workflow 17: Kubernetes Security Assessment
```yaml
name: k8s-assessment
trigger: API webhook
tools: kube-hunter, kube-bench, kubectx
outputs: K8s vulnerabilities
```

### Workflow 18: Kubernetes Exploitation
```yaml
name: k8s-exploitation
trigger: Approval required
tools: Peirates, kubectl, Service Account
outputs: K8s sessions, pod access
```

### Workflow 19: API Security Assessment
```yaml
name: api-security
trigger: Scheduled
tools: Burp Suite, OWASP ZAP, jwt_tool
outputs: API vulnerabilities
```

### Workflow 20: Payment Systems Assessment
```yaml
name: payment-assessment
trigger: Approval required
tools: Stripe CLI, PCI DSS Scanner, Card Data Discovery
outputs: PCI-DSS gaps, card data exposure
```

### Workflow 21: Social Engineering (Optional)
```yaml
name: social-engineering
trigger: Approval required
tools: Gophish, SET, Evilginx2
outputs: Phishing success rate
```

---

**Document Version**: 2.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
