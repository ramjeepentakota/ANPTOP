# ANPTOP - Missing Tools Gap Analysis

## Summary
Based on cross-referencing `docs/COMPLETE_TOOLS.md` with the current `tools_config.py`, the following tools are MISSING:

---

## MISSING TOOLS BY CATEGORY

### 1. ENUMERATION TOOLS (Missing: 8 tools)
Current: 27 | Required: 35

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | Azure PowerShell | Azure enumeration | MISSING |
| 2 | AWS VPC | VPC enumeration | MISSING |
| 3 | GCP IAM | GCP IAM enumeration | MISSING |
| 4 | k8s_enum | Kubernetes enumeration | MISSING |
| 5 | kubeconfig | Kubeconfig analysis | MISSING |
| 6 | AWS IAM | IAM policy enumeration | MISSING |
| 7 | Azure AD | Azure AD enumeration | MISSING |
| 8 | GCP Compute | GCP compute enumeration | MISSING |

---

### 2. EXPLOITATION TOOLS (Missing: 10 tools)
Current: 13 | Required: 23

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | AWS Exploit | AWS-specific exploits | MISSING |
| 2 | Azure Exploit | Azure-specific exploits | MISSING |
| 3 | GCP Exploit | GCP-specific exploits | MISSING |
| 4 | Cloud PrivEsc | Cloud privilege escalation | MISSING |
| 5 | AWS IAM Exploit | IAM vulnerability exploitation | MISSING |
| 6 | Azure AD Exploit | Azure AD exploitation | MISSING |
| 7 | S3 Exploit | S3 bucket exploitation | MISSING |
| 8 | Lambda Exploit | Lambda function injection | MISSING |
| 9 | AWS VPC Exploit | VPC endpoint exploitation | MISSING |
| 10 | KMS Exploit | Key management service exploitation | MISSING |

---

### 3. POST-EXPLOITATION TOOLS (Missing: 8 tools)
Current: 22 | Required: 30

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | AWS Keys | AWS credential harvesting | MISSING |
| 2 | Azure Keys | Azure credential harvesting | MISSING |
| 3 | GCP Keys | GCP credential harvesting | MISSING |
| 4 | AWS SSM | Systems Manager execution | MISSING |
| 5 | AWS Lambda | Lambda function enumeration | MISSING |
| 6 | Azure Functions | Azure function access | MISSING |
| 7 | CloudTrail | CloudTrail log analysis | MISSING |
| 8 | Cloud Metadata | Instance metadata enumeration | MISSING |
| 9 | Role Tricks | IAM role chain exploitation | MISSING |

---

### 4. LATERAL MOVEMENT TOOLS (Missing: 2 tools)
Current: 20 | Required: 22

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | Cross-Account | Cross-account access | MISSING |
| 2 | Role Chaining | IAM role chaining | MISSING |

---

### 5. API SECURITY TOOLS (Missing: 1 tool)
Current: 7 | Required: 8

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | GraphQL | GraphQL introspection | MISSING |

---

### 6. SOCIAL ENGINEERING TOOLS (Optional - 3 tools)
Current: 0 | Required: 0 (Optional)

| # | Tool Name | Purpose | Status |
|---|-----------|---------|--------|
| 1 | Gophish | Phishing campaign framework | OPTIONAL |
| 2 | SET | Social Engineering Toolkit | OPTIONAL |
| 3 | Evilginx2 | Advanced phishing framework | OPTIONAL |

---

## TOTAL MISSING TOOLS

| Category | Current | Required | Missing |
|----------|---------|----------|---------|
| Discovery | 14 | 14 | 0 |
| Scanning | 14 | 14 | 0 |
| Enumeration | 27 | 35 | 8 |
| Vulnerability Assessment | 22 | 22 | 0 |
| Exploitation | 13 | 23 | 10 |
| Post-Exploitation | 22 | 30 | 8 |
| Lateral Movement | 20 | 22 | 2 |
| Evidence Collection | 12 | 12 | 0 |
| Payment Systems | 10 | 10 | 0 |
| API Security | 7 | 8 | 1 |
| Blockchain | 6 | 6 | 0 |
| **TOTAL** | **167** | **196** | **29** |

---

## ACTION REQUIRED

To complete the 196 tools configuration, the following MUST be added:

1. **8 Enumeration tools**
2. **10 Exploitation tools**
3. **8 Post-Exploitation tools**
4. **2 Lateral Movement tools**
5. **1 API Security tool**

**Total: 29 tools**
