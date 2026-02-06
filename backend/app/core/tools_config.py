"""
ANPTOP - Comprehensive Security Tools Configuration
196 Tools across 11 categories for penetration testing and security assessment
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ToolCategory(str, Enum):
    DISCOVERY = "discovery"
    SCANNING = "scanning"
    ENUMERATION = "enumeration"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    LATERAL_MOVEMENT = "lateral_movement"
    EVIDENCE_COLLECTION = "evidence_collection"
    PAYMENT_SYSTEMS = "payment_systems"
    API_SECURITY = "api_security"
    BLOCKCHAIN = "blockchain"


class ToolStatus(str, Enum):
    CONFIGURED = "configured"
    PENDING = "pending"
    TESTING = "testing"
    READY = "ready"


class OSType(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    CROSS_PLATFORM = "cross_platform"
    CLOUD = "cloud"


class SecurityTool(BaseModel):
    """Security tool configuration."""
    name: str
    category: ToolCategory
    description: str
    version: Optional[str] = None
    path: Optional[str] = None
    os_type: OSType = OSType.LINUX
    status: ToolStatus = ToolStatus.PENDING
    command_template: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    output_format: str = "text"
    timeout_seconds: int = 300
    requires_approval: bool = False
    risk_level: int = Field(ge=1, le=5, default=1)  # 1=low, 5=high risk


# =============================================================================
# DISCOVERY TOOLS (14 Tools)
# =============================================================================

DISCOVERY_TOOLS: Dict[str, SecurityTool] = {
    # Network Discovery (4)
    "masscan": SecurityTool(
        name="Masscan",
        category=ToolCategory.DISCOVERY,
        description="Ultra-fast TCP port scanner",
        os_type=OSType.LINUX,
        command_template="masscan {target} -p{ports} --rate={rate}",
        parameters={"ports": "1-65535", "rate": "1000"},
        output_format="json",
        timeout_seconds=600,
    ),
    "rustscan": SecurityTool(
        name="RustScan",
        category=ToolCategory.DISCOVERY,
        description="Fast port scanner (10x Nmap speed)",
        os_type=OSType.LINUX,
        command_template="rustscan -t {threads} -r {range} --ulimit {ulimit} {target}",
        parameters={"threads": "500", "range": "1-65535", "ulimit": "10000"},
        output_format="text",
        timeout_seconds=300,
    ),
    "nmap": SecurityTool(
        name="Nmap",
        category=ToolCategory.DISCOVERY,
        description="Network mapper and port scanner",
        os_type=OSType.LINUX,
        command_template="nmap -sV -sC --script=default -p- {target}",
        parameters={},
        output_format="xml",
        timeout_seconds=600,
    ),
    "unicornscan": SecurityTool(
        name="Unicornscan",
        category=ToolCategory.DISCOVERY,
        description="Async stateless scanner",
        os_type=OSType.LINUX,
        command_template="unicornscan {target}:{ports} -T5",
        parameters={"ports": "1-65535"},
        output_format="text",
        timeout_seconds=600,
    ),
    
    # DNS Enumeration (3)
    "dnsrecon": SecurityTool(
        name="DNSRecon",
        category=ToolCategory.DISCOVERY,
        description="DNS enumeration and zone transfers",
        os_type=OSType.LINUX,
        command_template="dnsrecon -d {domain} -t axfr",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "dnschef": SecurityTool(
        name="DNSChef",
        category=ToolCategory.DISCOVERY,
        description="DNS proxy for enumeration",
        os_type=OSType.LINUX,
        command_template="dnschef --fakeip {ip} --fakedomains {domains} --nameserver {ns}",
        parameters={"ip": "127.0.0.1"},
        output_format="text",
        timeout_seconds=300,
    ),
    "theharvester": SecurityTool(
        name="theHarvester",
        category=ToolCategory.DISCOVERY,
        description="OSINT gathering for targets",
        os_type=OSType.LINUX,
        command_template="theHarvester -d {domain} -b all -f {output}",
        parameters={"output": "results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    
    # Cloud Discovery (7)
    "aws_cli": SecurityTool(
        name="AWS CLI",
        category=ToolCategory.DISCOVERY,
        description="AWS resource enumeration",
        os_type=OSType.CLOUD,
        command_template="aws {service} {action} --profile {profile}",
        parameters={"service": "ec2", "action": "describe-instances"},
        output_format="json",
        timeout_seconds=300,
        risk_level=2,
    ),
    "azure_cli": SecurityTool(
        name="Azure CLI",
        category=ToolCategory.DISCOVERY,
        description="Azure resource enumeration",
        os_type=OSType.CLOUD,
        command_template="az {resource} list --resource-group {rg}",
        parameters={"resource": "vm"},
        output_format="json",
        timeout_seconds=300,
        risk_level=2,
    ),
    "gcloud": SecurityTool(
        name="gcloud CLI",
        category=ToolCategory.DISCOVERY,
        description="GCP resource enumeration",
        os_type=OSType.CLOUD,
        command_template="gcloud {compute} instances list --project {project}",
        parameters={"compute": "compute"},
        output_format="json",
        timeout_seconds=300,
        risk_level=2,
    ),
    "cloudmapper": SecurityTool(
        name="Cloud Mapper",
        category=ToolCategory.DISCOVERY,
        description="Cloud network visualization",
        os_type=OSType.LINUX,
        command_template="python cloudmapper.py collect --config config.json",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "skyark": SecurityTool(
        name="SkyArk",
        category=ToolCategory.DISCOVERY,
        description="Cloud asset discovery",
        os_type=OSType.LINUX,
        command_template="python skyark.py -awsscan",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=2,
    ),
    "cloudelist": SecurityTool(
        name="Cloudelist",
        category=ToolCategory.DISCOVERY,
        description="Cloud service enumeration",
        os_type=OSType.LINUX,
        command_template="cloudelist -provider aws",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "awsume": SecurityTool(
        name="AWSume",
        category=ToolCategory.DISCOVERY,
        description="AWS role credential management",
        os_type=OSType.LINUX,
        command_template="awsume {profile}",
        parameters={},
        output_format="text",
        timeout_seconds=60,
    ),
}


# =============================================================================
# SCANNING TOOLS (14 Tools)
# =============================================================================

SCANNING_TOOLS: Dict[str, SecurityTool] = {
    # Port Scanning (4)
    "masscan_scan": SecurityTool(
        name="Masscan",
        category=ToolCategory.SCANNING,
        description="Full TCP/UDP port scan (1-65535)",
        os_type=OSType.LINUX,
        command_template="masscan {target} -p{ports} --rate={rate} -oJ {output}",
        parameters={"ports": "1-65535", "rate": "10000", "output": "scan.json"},
        output_format="json",
        timeout_seconds=1200,
    ),
    "rustscan_scan": SecurityTool(
        name="RustScan",
        category=ToolCategory.SCANNING,
        description="Fast port scan with Nmap integration",
        os_type=OSType.LINUX,
        command_template="rustscan -t {threads} -r {range} -- --nmap-light -A {target}",
        parameters={"threads": "500", "range": "1-65535"},
        output_format="xml",
        timeout_seconds=600,
    ),
    "nmap_scan": SecurityTool(
        name="Nmap",
        category=ToolCategory.SCANNING,
        description="Comprehensive port and service scan",
        os_type=OSType.LINUX,
        command_template="nmap -sS -sV -O -p- -oX {output} {target}",
        parameters={"output": "nmap_scan.xml"},
        output_format="xml",
        timeout_seconds=1200,
    ),
    "unicornscan_scan": SecurityTool(
        name="Unicornscan",
        category=ToolCategory.SCANNING,
        description="Async port scanning",
        os_type=OSType.LINUX,
        command_template="unicornscan {target}:{ports} -T5",
        parameters={"ports": "1-65535"},
        output_format="text",
        timeout_seconds=600,
    ),
    
    # Service Detection (3)
    "amass": SecurityTool(
        name="Amass",
        category=ToolCategory.SCANNING,
        description="Subdomain enumeration and service discovery",
        os_type=OSType.LINUX,
        command_template="amass enum -d {domain} -o {output}",
        parameters={"output": "subdomains.txt"},
        output_format="text",
        timeout_seconds=600,
    ),
    "sublist3r": SecurityTool(
        name="Sublist3r",
        category=ToolCategory.SCANNING,
        description="Subdomain finder",
        os_type=OSType.LINUX,
        command_template="sublist3r -d {domain} -o {output}",
        parameters={"output": "subdomains.txt"},
        output_format="text",
        timeout_seconds=600,
    ),
    "nmap_service": SecurityTool(
        name="Nmap Service Detection",
        category=ToolCategory.SCANNING,
        description="Service version detection (-sV)",
        os_type=OSType.LINUX,
        command_template="nmap -sV {target}",
        parameters={},
        output_format="xml",
        timeout_seconds=300,
    ),
    
    # Cloud Security Scanning (7)
    "scoutsuite": SecurityTool(
        name="ScoutSuite",
        category=ToolCategory.SCANNING,
        description="Multi-cloud security scanner",
        os_type=OSType.LINUX,
        command_template="scout --provider {provider} --profile {profile} --report {output}",
        parameters={"provider": "aws", "output": "scout_report"},
        output_format="json",
        timeout_seconds=1200,
        risk_level=2,
    ),
    "prowler": SecurityTool(
        name="Prowler",
        category=ToolCategory.SCANNING,
        description="AWS CIS benchmark scanner",
        os_type=OSType.LINUX,
        command_template="prowler {provider} -M csv json",
        parameters={"provider": "aws"},
        output_format="json",
        timeout_seconds=1200,
        risk_level=2,
    ),
    "aws_inspector": SecurityTool(
        name="AWS Inspector",
        category=ToolCategory.SCANNING,
        description="AWS vulnerability assessment",
        os_type=OSType.CLOUD,
        command_template="aws inspector2 list-findings --filterCriteria {filter}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=1,
    ),
    "azure_security": SecurityTool(
        name="Azure Security Center",
        category=ToolCategory.SCANNING,
        description="Azure security scanning",
        os_type=OSType.CLOUD,
        command_template="az security assessmet list",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "gcp_scc": SecurityTool(
        name="GCP Security Command Center",
        category=ToolCategory.SCANNING,
        description="GCP security assessment",
        os_type=OSType.CLOUD,
        command_template="gcloud securitycenter findings list --organization {org}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "cloud_custodian": SecurityTool(
        name="Cloud Custodian",
        category=ToolCategory.SCANNING,
        description="Cloud resource policy enforcement",
        os_type=OSType.LINUX,
        command_template="custodian run --output {output} {policy}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=3,
    ),
    "trivy": SecurityTool(
        name="Trivy",
        category=ToolCategory.SCANNING,
        description="Container vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="trivy image --format json --output {output} {image}",
        parameters={"output": "trivy_results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
}


# =============================================================================
# ENUMERATION TOOLS (35 Tools)
# =============================================================================

ENUMERATION_TOOLS: Dict[str, SecurityTool] = {
    # Network Enumeration (4)
    "enum4linux": SecurityTool(
        name="Enum4linux",
        category=ToolCategory.ENUMERATION,
        description="SMB/CIFS enumeration",
        os_type=OSType.LINUX,
        command_template="enum4linux -a {target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
    ),
    "smbclient": SecurityTool(
        name="SMBClient",
        category=ToolCategory.ENUMERATION,
        description="SMB file share access",
        os_type=OSType.LINUX,
        command_template="smbclient //{target}/{share} -U {user}",
        parameters={"share": "IPC$"},
        output_format="text",
        timeout_seconds=300,
    ),
    "rpcclient": SecurityTool(
        name="RPCClient",
        category=ToolCategory.ENUMERATION,
        description="RPC endpoint enumeration",
        os_type=OSType.LINUX,
        command_template="rpcclient -U {user}%{password} {target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
    ),
    "snmpwalk": SecurityTool(
        name="SNMPWalk",
        category=ToolCategory.ENUMERATION,
        description="SNMP OID enumeration",
        os_type=OSType.LINUX,
        command_template="snmpwalk -v {version} -c {community} {target}",
        parameters={"version": "2c", "community": "public"},
        output_format="text",
        timeout_seconds=300,
    ),
    
    # Web Enumeration (4)
    "gobuster": SecurityTool(
        name="Gobuster",
        category=ToolCategory.ENUMERATION,
        description="Directory/file brute-forcing",
        os_type=OSType.LINUX,
        command_template="gobuster dir -u {url} -w {wordlist} -o {output}",
        parameters={"output": "gobuster.txt"},
        output_format="text",
        timeout_seconds=600,
    ),
    "dirsearch": SecurityTool(
        name="Dirsearch",
        category=ToolCategory.ENUMERATION,
        description="Web path discovery",
        os_type=OSType.LINUX,
        command_template="python3 dirsearch.py -u {url} -o {output}",
        parameters={"output": "dirsearch.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "wpscan": SecurityTool(
        name="WPScan",
        category=ToolCategory.ENUMERATION,
        description="WordPress vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="wpscan --url {url} --enumerate u p t --output {output}",
        parameters={"output": "wpscan.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "cmsmap": SecurityTool(
        name="CMSmap",
        category=ToolCategory.ENUMERATION,
        description="CMS vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="python3 cmsmap.py {url} -F",
        parameters={},
        output_format="text",
        timeout_seconds=300,
    ),
    
    # Active Directory (2)
    "bloodhound": SecurityTool(
        name="BloodHound",
        category=ToolCategory.ENUMERATION,
        description="AD attack path mapping",
        os_type=OSType.LINUX,
        command_template="python3 bloodhound.py -c All -d {domain}",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=3,
    ),
    "sharphound": SecurityTool(
        name="SharpHound",
        category=ToolCategory.ENUMERATION,
        description="BloodHound data collector",
        os_type=OSType.WINDOWS,
        command_template="SharpHound.exe -c All",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=3,
    ),
    
    # Kubernetes (4)
    "kubectl": SecurityTool(
        name="kubectl",
        category=ToolCategory.ENUMERATION,
        description="Kubernetes CLI",
        os_type=OSType.LINUX,
        command_template="kubectl get pods -A -o yaml",
        parameters={},
        output_format="yaml",
        timeout_seconds=120,
    ),
    "kubectx": SecurityTool(
        name="kubectx",
        category=ToolCategory.ENUMERATION,
        description="K8s context switching",
        os_type=OSType.LINUX,
        command_template="kubectx",
        parameters={},
        output_format="text",
        timeout_seconds=30,
    ),
    "kubens": SecurityTool(
        name="kubens",
        category=ToolCategory.ENUMERATION,
        description="K8s namespace switching",
        os_type=OSType.LINUX,
        command_template="kubens",
        parameters={},
        output_format="text",
        timeout_seconds=30,
    ),
    "kubeletctl": SecurityTool(
        name="kubeletctl",
        category=ToolCategory.ENUMERATION,
        description="Kubelet enumeration",
        os_type=OSType.LINUX,
        command_template="kubeletctl pods {node}",
        parameters={},
        output_format="text",
        timeout_seconds=120,
    ),
    
    # Cloud Enumeration (13)
    "pacu": SecurityTool(
        name="Pacu",
        category=ToolCategory.ENUMERATION,
        description="AWS exploitation framework",
        os_type=OSType.LINUX,
        command_template="python3 pacu.py",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=4,
    ),
    "cloudfox": SecurityTool(
        name="Cloud Fox",
        category=ToolCategory.ENUMERATION,
        description="Cloud attack surface mapping",
        os_type=OSType.LINUX,
        command_template="cloudfox aws {command}",
        parameters={},
        output_format="text",
        timeout_seconds=600,
        risk_level=3,
    ),
    "azurehound": SecurityTool(
        name="AzureHound",
        category=ToolCategory.ENUMERATION,
        description="Azure AD enumeration",
        os_type=OSType.LINUX,
        command_template="python3 azurehound.py",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=3,
    ),
    "roadtools": SecurityTool(
        name="ROADtools",
        category=ToolCategory.ENUMERATION,
        description="Azure AD exploration",
        os_type=OSType.LINUX,
        command_template="roadrecon auth",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=2,
    ),
    "s3recon": SecurityTool(
        name="s3recon",
        category=ToolCategory.ENUMERATION,
        description="S3 bucket enumeration",
        os_type=OSType.LINUX,
        command_template="python3 s3recon.py -w {wordlist}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "azure_powershell": SecurityTool(
        name="Azure PowerShell",
        category=ToolCategory.ENUMERATION,
        description="Azure enumeration and management",
        os_type=OSType.LINUX,
        command_template="powershell -c Connect-AzAccount; Get-AzVM",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=2,
    ),
    "aws_vpc": SecurityTool(
        name="AWS VPC",
        category=ToolCategory.ENUMERATION,
        description="VPC enumeration and analysis",
        os_type=OSType.CLOUD,
        command_template="aws ec2 describe-vpcs --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_iam": SecurityTool(
        name="GCP IAM",
        category=ToolCategory.ENUMERATION,
        description="GCP IAM enumeration",
        os_type=OSType.CLOUD,
        command_template="gcloud iam service-accounts list --project {project}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "k8s_enum": SecurityTool(
        name="k8s_enum",
        category=ToolCategory.ENUMERATION,
        description="Kubernetes enumeration framework",
        os_type=OSType.LINUX,
        command_template="python3 k8s_enum.py --target {cluster}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=3,
    ),
    "kubeconfig": SecurityTool(
        name="kubeconfig",
        category=ToolCategory.ENUMERATION,
        description="Kubeconfig analysis and extraction",
        os_type=OSType.LINUX,
        command_template="kubectl config view",
        parameters={},
        output_format="yaml",
        timeout_seconds=60,
    ),
    "aws_iam_enum": SecurityTool(
        name="AWS IAM",
        category=ToolCategory.ENUMERATION,
        description="IAM policy and user enumeration",
        os_type=OSType.CLOUD,
        command_template="aws iam list-users --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_ad_enum": SecurityTool(
        name="Azure AD",
        category=ToolCategory.ENUMERATION,
        description="Azure AD user and group enumeration",
        os_type=OSType.CLOUD,
        command_template="az ad user list --output json",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_compute_enum": SecurityTool(
        name="GCP Compute",
        category=ToolCategory.ENUMERATION,
        description="GCP compute instance enumeration",
        os_type=OSType.CLOUD,
        command_template="gcloud compute instances list --project {project}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    
    # Additional Cloud Enumeration (8 tools to reach 35)
    "aws_eks": SecurityTool(
        name="AWS EKS",
        category=ToolCategory.ENUMERATION,
        description="EKS cluster enumeration",
        os_type=OSType.CLOUD,
        command_template="aws eks list-clusters --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "aws_rds_enum": SecurityTool(
        name="AWS RDS",
        category=ToolCategory.ENUMERATION,
        description="RDS instance enumeration",
        os_type=OSType.CLOUD,
        command_template="aws rds describe-db-instances --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "aws_lambda_enum": SecurityTool(
        name="AWS Lambda",
        category=ToolCategory.ENUMERATION,
        description="Lambda function enumeration",
        os_type=OSType.CLOUD,
        command_template="aws lambda list-functions --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "aws_s3_enum": SecurityTool(
        name="AWS S3",
        category=ToolCategory.ENUMERATION,
        description="S3 bucket enumeration",
        os_type=OSType.CLOUD,
        command_template="aws s3api list-buckets --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_aks": SecurityTool(
        name="Azure AKS",
        category=ToolCategory.ENUMERATION,
        description="AKS cluster enumeration",
        os_type=OSType.CLOUD,
        command_template="az aks list --resource-group {rg}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_sql": SecurityTool(
        name="Azure SQL",
        category=ToolCategory.ENUMERATION,
        description="Azure SQL enumeration",
        os_type=OSType.CLOUD,
        command_template="az sql server list --resource-group {rg}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_gke": SecurityTool(
        name="GCP GKE",
        category=ToolCategory.ENUMERATION,
        description="GKE cluster enumeration",
        os_type=OSType.CLOUD,
        command_template="gcloud container clusters list --project {project}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_bigquery": SecurityTool(
        name="GCP BigQuery",
        category=ToolCategory.ENUMERATION,
        description="BigQuery dataset enumeration",
        os_type=OSType.CLOUD,
        command_template="gcloud beta bigquery datasets list --project {project}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
}


# =============================================================================
# VULNERABILITY ASSESSMENT TOOLS (22 Tools)
# =============================================================================

VULNERABILITY_ASSESSMENT_TOOLS: Dict[str, SecurityTool] = {
    # Primary VA (4)
    "openvas": SecurityTool(
        name="OpenVAS",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Comprehensive vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="omp -u {user} -w {pass} -h {host} -T {target}",
        parameters={},
        output_format="xml",
        timeout_seconds=1800,
    ),
    "nessus": SecurityTool(
        name="Nessus",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Commercial vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="nessuscli scan --name {name} --target {target}",
        parameters={},
        output_format="nessus",
        timeout_seconds=1800,
    ),
    "nuclei": SecurityTool(
        name="Nuclei",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Template-based vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="nuclei -u {target} -t {templates} -o {output}",
        parameters={"templates": "/opt/nuclei-templates", "output": "nuclei_results.json"},
        output_format="json",
        timeout_seconds=1200,
    ),
    "greenbone": SecurityTool(
        name="Greenbone CE",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="OpenVAS frontend/manager",
        os_type=OSType.LINUX,
        command_template="omp -u {user} -w {pass} -h {host}",
        parameters={},
        output_format="xml",
        timeout_seconds=1800,
    ),
    
    # Web VA (4)
    "xsser": SecurityTool(
        name="XSSer",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="XSS vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="python3 xsser --url {url} --auto",
        parameters={},
        output_format="html",
        timeout_seconds=600,
    ),
    "sqlmap": SecurityTool(
        name="SQLMap",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="SQL injection scanner",
        os_type=OSType.LINUX,
        command_template="python3 sqlmap.py -u {url} --batch --output-dir {output}",
        parameters={"output": "sqlmap_results"},
        output_format="text",
        timeout_seconds=1200,
        risk_level=4,
    ),
    "nikto": SecurityTool(
        name="Nikto",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Web server vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="nikto -h {host} -o {output}",
        parameters={"output": "nikto.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "sslscan": SecurityTool(
        name="SSLyze",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="SSL/TLS vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="sslyze --json_out {output} {target}",
        parameters={"output": "sslscan.json"},
        output_format="json",
        timeout_seconds=300,
    ),
    
    # Cloud VA (10)
    "checkov": SecurityTool(
        name="Checkov",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="IaC security scanning",
        os_type=OSType.LINUX,
        command_template="checkov -d {directory} -o json --output {output}",
        parameters={"output": "checkov_results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "terrascan": SecurityTool(
        name="Terrascan",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Terraform security scanning",
        os_type=OSType.LINUX,
        command_template="terrascan scan -d {directory} -o json",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "grype": SecurityTool(
        name="Grype",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="SBOM vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="grype {target} -o json -o {output}",
        parameters={"output": "grype_results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "clair": SecurityTool(
        name="Clair",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Container image analysis",
        os_type=OSType.LINUX,
        command_template="clair-scanner {image}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "anchore": SecurityTool(
        name="Anchore",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Container security analysis",
        os_type=OSType.LINUX,
        command_template="anchore-cli image add {image}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "cloud_custodian_va": SecurityTool(
        name="Cloud Custodian VA",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Policy enforcement",
        os_type=OSType.LINUX,
        command_template="custodian run --output {output} {policy}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=3,
    ),
    "aws_inspector_va": SecurityTool(
        name="AWS Inspector VA",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="AWS vulnerability assessment",
        os_type=OSType.CLOUD,
        command_template="aws inspector2 list-findings",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=1,
    ),
    "scoutsuite_va": SecurityTool(
        name="ScoutSuite VA",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Multi-cloud security scanner",
        os_type=OSType.LINUX,
        command_template="scout --provider {provider}",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=2,
    ),
    "prowler_va": SecurityTool(
        name="Prowler VA",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="AWS CIS benchmark",
        os_type=OSType.LINUX,
        command_template="prowler {provider}",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=2,
    ),
    "trivy_va": SecurityTool(
        name="Trivy VA",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Container image scanning",
        os_type=OSType.LINUX,
        command_template="trivy image {image}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    
    # Kubernetes VA (4)
    "kube_hunter": SecurityTool(
        name="kube-hunter",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="K8s penetration testing",
        os_type=OSType.LINUX,
        command_template="kube-hunter --report json",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "kube_bench": SecurityTool(
        name="kube-bench",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="CIS K8s benchmark",
        os_type=OSType.LINUX,
        command_template="kube-bench run --targets master",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "falco": SecurityTool(
        name="Falco",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Runtime security detection",
        os_type=OSType.LINUX,
        command_template="falco",
        parameters={},
        output_format="json",
        timeout_seconds=0,
    ),
    "opa_gatekeeper": SecurityTool(
        name="OPA Gatekeeper",
        category=ToolCategory.VULNERABILITY_ASSESSMENT,
        description="Policy enforcement",
        os_type=OSType.LINUX,
        command_template="kubectl get constrainttemplates",
        parameters={},
        output_format="yaml",
        timeout_seconds=120,
    ),
}


# =============================================================================
# EXPLOITATION TOOLS (23 Tools)
# =============================================================================

EXPLOITATION_TOOLS: Dict[str, SecurityTool] = {
    # Primary Framework (2)
    "metasploit": SecurityTool(
        name="Metasploit Framework",
        category=ToolCategory.EXPLOITATION,
        description="Exploitation and post-exploitation",
        os_type=OSType.LINUX,
        command_template="msfconsole -q -x '{command}'",
        parameters={},
        output_format="xml",
        timeout_seconds=1800,
        risk_level=5,
        requires_approval=True,
    ),
    "metasploit_rpc": SecurityTool(
        name="Metasploit RPC",
        category=ToolCategory.EXPLOITATION,
        description="Remote API automation",
        os_type=OSType.LINUX,
        command_template="msfrpcd -P {password}",
        parameters={},
        output_format="xml",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    
    # Exploitation Utils (3)
    "crackmapexec": SecurityTool(
        name="CrackMapExec",
        category=ToolCategory.EXPLOITATION,
        description="Network exploitation toolkit",
        os_type=OSType.LINUX,
        command_template="crackmapexec smb {target} -u {user} -p {password}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "responder": SecurityTool(
        name="Responder",
        category=ToolCategory.EXPLOITATION,
        description="LLMNR/NBT-NS poisoning",
        os_type=OSType.LINUX,
        command_template="responder -I {interface}",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "impacket": SecurityTool(
        name="Impacket",
        category=ToolCategory.EXPLOITATION,
        description="Python exploitation library",
        os_type=OSType.LINUX,
        command_template="python3 {script} {target}",
        parameters={},
        output_format="text",
        timeout_seconds=600,
        risk_level=4,
    ),
    
    # Cloud Exploitation (13)
    "pacu_exploit": SecurityTool(
        name="Pacu",
        category=ToolCategory.EXPLOITATION,
        description="AWS exploitation framework",
        os_type=OSType.LINUX,
        command_template="python3 pacu.py",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=5,
        requires_approval=True,
    ),
    "cloudfox_exploit": SecurityTool(
        name="Cloud Fox",
        category=ToolCategory.EXPLOITATION,
        description="Cloud attack surface",
        os_type=OSType.LINUX,
        command_template="cloudfox aws {command}",
        parameters={},
        output_format="text",
        timeout_seconds=600,
        risk_level=4,
        requires_approval=True,
    ),
    "cloudbrute": SecurityTool(
        name="Cloudbrute",
        category=ToolCategory.EXPLOITATION,
        description="Cloud asset brute-forcing",
        os_type=OSType.LINUX,
        command_template="cloudbrute -k {keyword} -d {domain}",
        parameters={},
        output_format="text",
        timeout_seconds=600,
        risk_level=3,
    ),
    # Additional Cloud Exploitation (10 tools)
    "aws_exploit": SecurityTool(
        name="AWS Exploit",
        category=ToolCategory.EXPLOITATION,
        description="AWS-specific exploits",
        os_type=OSType.CLOUD,
        command_template="python3 aws_exploit.py --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "azure_exploit": SecurityTool(
        name="Azure Exploit",
        category=ToolCategory.EXPLOITATION,
        description="Azure-specific exploits",
        os_type=OSType.CLOUD,
        command_template="python3 azure_exploit.py --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "gcp_exploit": SecurityTool(
        name="GCP Exploit",
        category=ToolCategory.EXPLOITATION,
        description="GCP-specific exploits",
        os_type=OSType.CLOUD,
        command_template="python3 gcp_exploit.py --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "cloud_privesc": SecurityTool(
        name="Cloud PrivEsc",
        category=ToolCategory.EXPLOITATION,
        description="Cloud privilege escalation",
        os_type=OSType.CLOUD,
        command_template="python3 cloud_privesc.py --provider {provider}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "aws_iam_exploit": SecurityTool(
        name="AWS IAM Exploit",
        category=ToolCategory.EXPLOITATION,
        description="IAM vulnerability exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 aws_iam_exploit.py --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "azure_ad_exploit": SecurityTool(
        name="Azure AD Exploit",
        category=ToolCategory.EXPLOITATION,
        description="Azure AD exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 azure_ad_exploit.py --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "s3_exploit": SecurityTool(
        name="S3 Exploit",
        category=ToolCategory.EXPLOITATION,
        description="S3 bucket exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 s3_exploit.py --bucket {bucket}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=4,
        requires_approval=True,
    ),
    "lambda_exploit": SecurityTool(
        name="Lambda Exploit",
        category=ToolCategory.EXPLOITATION,
        description="Lambda function injection",
        os_type=OSType.CLOUD,
        command_template="python3 lambda_exploit.py --function {function}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "aws_vpc_exploit": SecurityTool(
        name="AWS VPC Exploit",
        category=ToolCategory.EXPLOITATION,
        description="VPC endpoint exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 vpc_exploit.py --vpc {vpc_id}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=4,
        requires_approval=True,
    ),
    "kms_exploit": SecurityTool(
        name="KMS Exploit",
        category=ToolCategory.EXPLOITATION,
        description="Key Management Service exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 kms_exploit.py --key {key_id}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    
    # C2 Frameworks (5)
    "sliver": SecurityTool(
        name="Sliver",
        category=ToolCategory.EXPLOITATION,
        description="Open source C2 framework",
        os_type=OSType.LINUX,
        command_template="sliver-server",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "covenant": SecurityTool(
        name="Covenant",
        category=ToolCategory.EXPLOITATION,
        description=".NET C2 framework",
        os_type=OSType.LINUX,
        command_template="dotnet Covenant.dll",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "havoc": SecurityTool(
        name="Havoc",
        category=ToolCategory.EXPLOITATION,
        description="Modern C2 framework",
        os_type=OSType.LINUX,
        command_template="./Havoc",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "mythic": SecurityTool(
        name="Mythic",
        category=ToolCategory.EXPLOITATION,
        description="Cross-platform C2",
        os_type=OSType.LINUX,
        command_template="python3 mythic",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "merlin": SecurityTool(
        name="Merlin",
        category=ToolCategory.EXPLOITATION,
        description="Golang C2 framework",
        os_type=OSType.LINUX,
        command_template="./merlin-server",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
}


# =============================================================================
# POST-EXPLOITATION TOOLS (30 Tools)
# =============================================================================

POST_EXPLOITATION_TOOLS: Dict[str, SecurityTool] = {
    # Credential Harvesting (4)
    "mimikatz": SecurityTool(
        name="Mimikatz",
        category=ToolCategory.POST_EXPLOITATION,
        description="Windows credential extraction",
        os_type=OSType.WINDOWS,
        command_template="mimikatz.exe sekurlsa::logonpasswords",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "secretsdump": SecurityTool(
        name="Secretsdump",
        category=ToolCategory.POST_EXPLOITATION,
        description="SAM/LSADump extraction",
        os_type=OSType.LINUX,
        command_template="secretsdump.py {domain}/{user}:{password}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "lazagne": SecurityTool(
        name="LaZagne",
        category=ToolCategory.POST_EXPLOITATION,
        description="Multi-platform credential recovery",
        os_type=OSType.LINUX,
        command_template="python3 laZagne.py all",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=4,
        requires_approval=True,
    ),
    "keepass": SecurityTool(
        name="KeePass",
        category=ToolCategory.POST_EXPLOITATION,
        description="Password database extraction",
        os_type=OSType.LINUX,
        command_template="keepass2john {database}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
    ),
    
    # Data Discovery (3)
    "snaffler": SecurityTool(
        name="Snaffler",
        category=ToolCategory.POST_EXPLOITATION,
        description="Share file discovery",
        os_type=OSType.WINDOWS,
        command_template="Snaffler.exe -s -o snaffler.log",
        parameters={},
        output_format="text",
        timeout_seconds=600,
    ),
    "powerup": SecurityTool(
        name="PowerUp",
        category=ToolCategory.POST_EXPLOITATION,
        description="Windows privilege escalation",
        os_type=OSType.WINDOWS,
        command_template="powershell -exec bypass -c Import-Module .\\PowerUp.ps1; Invoke-AllChecks",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "bloodhound_post": SecurityTool(
        name="BloodHound Post",
        category=ToolCategory.POST_EXPLOITATION,
        description="AD attack path mapping",
        os_type=OSType.LINUX,
        command_template="python3 bloodhound.py -c All",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
        risk_level=3,
    ),
    
    # Cloud Post-Exploitation (15)
    "gitleaks": SecurityTool(
        name="Gitleaks",
        category=ToolCategory.POST_EXPLOITATION,
        description="Git repository secrets detection",
        os_type=OSType.LINUX,
        command_template="gitleaks detect --source={directory}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "trufflehog": SecurityTool(
        name="TruffleHog",
        category=ToolCategory.POST_EXPLOITATION,
        description="Git secrets scanning",
        os_type=OSType.LINUX,
        command_template="trufflehog filesystem {directory}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "aws_secrets": SecurityTool(
        name="AWS Secrets Manager",
        category=ToolCategory.POST_EXPLOITATION,
        description="Secrets Manager enumeration",
        os_type=OSType.CLOUD,
        command_template="aws secretsmanager list-secrets",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_keyvault": SecurityTool(
        name="Azure Key Vault",
        category=ToolCategory.POST_EXPLOITATION,
        description="Key vault access",
        os_type=OSType.CLOUD,
        command_template="az keyvault secret list --vault-name {vault}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_secret_manager": SecurityTool(
        name="GCP Secret Manager",
        category=ToolCategory.POST_EXPLOITATION,
        description="Secret manager access",
        os_type=OSType.CLOUD,
        command_template="gcloud secrets list --filter={filter}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    # Additional Cloud Post-Exploitation (10 tools)
    "aws_keys": SecurityTool(
        name="AWS Keys",
        category=ToolCategory.POST_EXPLOITATION,
        description="AWS credential harvesting",
        os_type=OSType.CLOUD,
        command_template="curl http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        parameters={},
        output_format="json",
        timeout_seconds=60,
        risk_level=5,
        requires_approval=True,
    ),
    "azure_keys": SecurityTool(
        name="Azure Keys",
        category=ToolCategory.POST_EXPLOITATION,
        description="Azure credential harvesting",
        os_type=OSType.CLOUD,
        command_template="az keyvault secret list --vault-name {vault}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
        risk_level=5,
        requires_approval=True,
    ),
    "gcp_keys": SecurityTool(
        name="GCP Keys",
        category=ToolCategory.POST_EXPLOITATION,
        description="GCP credential harvesting",
        os_type=OSType.CLOUD,
        command_template="gcloud compute instances describe {instance} --zone {zone}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
        risk_level=5,
        requires_approval=True,
    ),
    "aws_ssm_post": SecurityTool(
        name="AWS SSM",
        category=ToolCategory.POST_EXPLOITATION,
        description="Systems Manager execution",
        os_type=OSType.CLOUD,
        command_template="aws ssm send-command --instance-ids {instance}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "aws_lambda_post": SecurityTool(
        name="AWS Lambda",
        category=ToolCategory.POST_EXPLOITATION,
        description="Lambda function enumeration",
        os_type=OSType.CLOUD,
        command_template="aws lambda list-functions --profile {profile}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_functions": SecurityTool(
        name="Azure Functions",
        category=ToolCategory.POST_EXPLOITATION,
        description="Azure function app access",
        os_type=OSType.CLOUD,
        command_template="az functionapp list --resource-group {rg}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "cloudtrail": SecurityTool(
        name="CloudTrail",
        category=ToolCategory.POST_EXPLOITATION,
        description="CloudTrail log analysis",
        os_type=OSType.CLOUD,
        command_template="aws cloudtrail lookup-events --start-time {start}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "cloud_metadata": SecurityTool(
        name="Cloud Metadata",
        category=ToolCategory.POST_EXPLOITATION,
        description="Instance metadata enumeration",
        os_type=OSType.LINUX,
        command_template="curl http://169.254.169.254/latest/meta-data/",
        parameters={},
        output_format="text",
        timeout_seconds=60,
        risk_level=4,
    ),
    "role_tricks": SecurityTool(
        name="Role Tricks",
        category=ToolCategory.POST_EXPLOITATION,
        description="IAM role chain exploitation",
        os_type=OSType.CLOUD,
        command_template="python3 role_tricks.py --target {role}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    
    # Kubernetes Post-Exploitation (8)
    "peirates": SecurityTool(
        name="Peirates",
        category=ToolCategory.POST_EXPLOITATION,
        description="Kubernetes exploitation",
        os_type=OSType.LINUX,
        command_template="python3 peirates.py",
        parameters={},
        output_format="text",
        timeout_seconds=600,
        risk_level=4,
    ),
    "helm": SecurityTool(
        name="Helm",
        category=ToolCategory.POST_EXPLOITATION,
        description="K8s package manager",
        os_type=OSType.LINUX,
        command_template="helm list -A",
        parameters={},
        output_format="text",
        timeout_seconds=120,
    ),
    "k9s": SecurityTool(
        name="k9s",
        category=ToolCategory.POST_EXPLOITATION,
        description="K8s CLI dashboard",
        os_type=OSType.LINUX,
        command_template="k9s",
        parameters={},
        output_format="text",
        timeout_seconds=0,
    ),
    "stern": SecurityTool(
        name="stern",
        category=ToolCategory.POST_EXPLOITATION,
        description="K8s log tailing",
        os_type=OSType.LINUX,
        command_template="stern --all-namespaces",
        parameters={},
        output_format="text",
        timeout_seconds=0,
    ),
    "kubens_post": SecurityTool(
        name="kubens",
        category=ToolCategory.POST_EXPLOITATION,
        description="K8s namespace access",
        os_type=OSType.LINUX,
        command_template="kubens {namespace}",
        parameters={},
        output_format="text",
        timeout_seconds=30,
    ),
    "privileged": SecurityTool(
        name="Privileged",
        category=ToolCategory.POST_EXPLOITATION,
        description="K8s privilege escalation",
        os_type=OSType.LINUX,
        command_template="kubectl auth can-i --list --namespace={namespace}",
        parameters={},
        output_format="text",
        timeout_seconds=60,
        risk_level=4,
    ),
    "service_account": SecurityTool(
        name="Service Account",
        category=ToolCategory.POST_EXPLOITATION,
        description="SA token abuse",
        os_type=OSType.LINUX,
        command_template="kubectl get serviceaccounts",
        parameters={},
        output_format="text",
        timeout_seconds=60,
    ),
    
    # Additional Post-Exploitation (2 tools to reach 30)
    "pypykatz": SecurityTool(
        name="Pypykatz",
        category=ToolCategory.POST_EXPLOITATION,
        description="Mimikatz alternative in Python",
        os_type=OSType.LINUX,
        command_template="python3 pypykatz live -p",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "katana": SecurityTool(
        name="Katana",
        category=ToolCategory.POST_EXPLOITATION,
        description="AWS key dump",
        os_type=OSType.LINUX,
        command_template="katana -u {user} -p {password}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
}


# =============================================================================
# LATERAL MOVEMENT TOOLS (22 Tools)
# =============================================================================

LATERAL_MOVEMENT_TOOLS: Dict[str, SecurityTool] = {
    # Windows (5)
    "wmiexec": SecurityTool(
        name="WMIExec",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="WMI lateral movement",
        os_type=OSType.WINDOWS,
        command_template="wmiexec.py {domain}/{user}:{password}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "psexec": SecurityTool(
        name="PsExec",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Remote execution",
        os_type=OSType.WINDOWS,
        command_template="psexec \\\\\\{target} -u {user} -p {password}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "smbexec": SecurityTool(
        name="SMBExec",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="SMB execution",
        os_type=OSType.LINUX,
        command_template="smbexec.py {domain}/{user}:{password}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "atexec": SecurityTool(
        name="atexec",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Scheduled task lateral",
        os_type=OSType.LINUX,
        command_template="atexec.py {domain}/{user}:{password}@{target} '{command}'",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "dcomexec": SecurityTool(
        name="DCOMExec",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="DCOM execution",
        os_type=OSType.LINUX,
        command_template="dcomexec.py {domain}/{user}:{password}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    
    # Linux (3)
    "ssh": SecurityTool(
        name="SSH",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="SSH pivot",
        os_type=OSType.LINUX,
        command_template="ssh -i {key} {user}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "ansible": SecurityTool(
        name="Ansible",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Ansible pivot",
        os_type=OSType.LINUX,
        command_template="ansible all -m ping",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "rsync": SecurityTool(
        name="rsync",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Data transfer",
        os_type=OSType.LINUX,
        command_template="rsync -avz {source} {user}@{target}:{dest}",
        parameters={},
        output_format="text",
        timeout_seconds=600,
    ),
    
    # Database (2)
    "powerupsql": SecurityTool(
        name="PowerUpSQL",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="SQL Server pivot",
        os_type=OSType.WINDOWS,
        command_template="powershell -exec bypass -c Import-Module .\\PowerUpSQL.ps1",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "mssqlclient": SecurityTool(
        name="mssqlclient",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="MSSQL client",
        os_type=OSType.LINUX,
        command_template="mssqlclient.py {domain}/{user}:{password}@{target}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    
    # Cloud Lateral (8)
    "aws_ssm": SecurityTool(
        name="AWS Systems Manager",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="SSM lateral movement",
        os_type=OSType.CLOUD,
        command_template="aws ssm start-session --target {instance}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
        requires_approval=True,
    ),
    "aws_session_manager": SecurityTool(
        name="AWS Session Manager",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Session management",
        os_type=OSType.CLOUD,
        command_template="session-manager-plugin",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=3,
    ),
    "aws_rds": SecurityTool(
        name="AWS RDS",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Database lateral",
        os_type=OSType.CLOUD,
        command_template="aws rds describe-db-instances",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "azure_vm_run": SecurityTool(
        name="Azure VM Run Command",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Azure VM execution",
        os_type=OSType.CLOUD,
        command_template="az vm run-command invoke --resource-group {rg} --name {vm}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=4,
        requires_approval=True,
    ),
    "azure_automation": SecurityTool(
        name="Azure Automation",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Azure automation",
        os_type=OSType.CLOUD,
        command_template="az automation account list",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "gcp_compute": SecurityTool(
        name="GCP Compute",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="GCP compute access",
        os_type=OSType.CLOUD,
        command_template="gcloud compute ssh {user}@{instance} --zone {zone}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "cross_account": SecurityTool(
        name="Cross-Account",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Cross-account access",
        os_type=OSType.CLOUD,
        command_template="python3 cross_account.py --source {source} --target {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=5,
        requires_approval=True,
    ),
    "role_chaining": SecurityTool(
        name="Role Chaining",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="IAM role chaining",
        os_type=OSType.CLOUD,
        command_template="aws sts assume-role --role-arn {role} --role-session-name {session}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
        risk_level=5,
        requires_approval=True,
    ),
    
    # Kubernetes Lateral (4)
    "kubectl_exec": SecurityTool(
        name="kubectl",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="K8s pod lateral",
        os_type=OSType.LINUX,
        command_template="kubectl exec -it {pod} -- {command}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=4,
    ),
    "service_account_lat": SecurityTool(
        name="Service Account",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="SA token abuse",
        os_type=OSType.LINUX,
        command_template="kubectl exec -it {pod} -- cat /var/run/secrets/kubernetes.io/serviceaccount/token",
        parameters={},
        output_format="text",
        timeout_seconds=60,
        risk_level=4,
    ),
    "pod_escape": SecurityTool(
        name="Pod Escape",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Container escape",
        os_type=OSType.LINUX,
        command_template="kubectl {command}",
        parameters={},
        output_format="text",
        timeout_seconds=300,
        risk_level=5,
        requires_approval=True,
    ),
    "cluster_admin": SecurityTool(
        name="Cluster Admin",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="K8s privilege escalation",
        os_type=OSType.LINUX,
        command_template="kubectl auth can-i '*' '*'",
        parameters={},
        output_format="text",
        timeout_seconds=60,
        risk_level=5,
        requires_approval=True,
    ),
}


# =============================================================================
# EVIDENCE COLLECTION TOOLS (12 Tools)
# =============================================================================

EVIDENCE_COLLECTION_TOOLS: Dict[str, SecurityTool] = {
    # Network Capture (2)
    "tcpdump": SecurityTool(
        name="Tcpdump",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Packet capture",
        os_type=OSType.LINUX,
        command_template="tcpdump -i {interface} -w {output} -c {count}",
        parameters={"count": "1000", "output": "capture.pcap"},
        output_format="pcap",
        timeout_seconds=600,
    ),
    "wireshark": SecurityTool(
        name="Wireshark",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Packet analysis",
        os_type=OSType.LINUX,
        command_template="tshark -r {input} -T json",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    
    # Evidence Capture (2)
    "screenshooter": SecurityTool(
        name="Screenshooter",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Screenshot capture",
        os_type=OSType.LINUX,
        command_template="import -window root {output}",
        parameters={"output": "screenshot.png"},
        output_format="png",
        timeout_seconds=30,
    ),
    "bulk_extractor": SecurityTool(
        name="Bulk Extractor",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="File carving",
        os_type=OSType.LINUX,
        command_template="bulk_extractor {input} -o {output}",
        parameters={},
        output_format="text",
        timeout_seconds=1200,
    ),
    
    # Hashing (2)
    "sha256sum_tool": SecurityTool(
        name="SHA-256 Hash",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="SHA-256 hashing",
        os_type=OSType.LINUX,
        command_template="sha256sum {file}",
        parameters={},
        output_format="text",
        timeout_seconds=60,
    ),
    "sha512sum_tool": SecurityTool(
        name="SHA-512 Hash",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="SHA-512 hashing",
        os_type=OSType.LINUX,
        command_template="sha512sum {file}",
        parameters={},
        output_format="text",
        timeout_seconds=60,
    ),
    
    # Cloud Logs (6)
    "aws_logs": SecurityTool(
        name="AWS CloudTrail",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="CloudTrail evidence",
        os_type=OSType.CLOUD,
        command_template="aws cloudtrail lookup-events --start-time {start}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "azure_logs": SecurityTool(
        name="Azure Activity Logs",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Azure activity logs",
        os_type=OSType.CLOUD,
        command_template="az monitor activity-log list --resource-group {rg}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "gcp_logs": SecurityTool(
        name="GCP Audit Logs",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Cloud audit logs",
        os_type=OSType.CLOUD,
        command_template="gcloud logging read --resource={resource}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "k8s_logs": SecurityTool(
        name="Kubernetes Logs",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="K8s audit logs",
        os_type=OSType.LINUX,
        command_template="kubectl logs -A --since={time}",
        parameters={"time": "24h"},
        output_format="text",
        timeout_seconds=300,
    ),
    "payment_logs": SecurityTool(
        name="Payment Logs",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Payment transaction logs",
        os_type=OSType.LINUX,
        command_template="python3 collect_payment_logs.py {target}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "blockchain_logs": SecurityTool(
        name="Blockchain Logs",
        category=ToolCategory.EVIDENCE_COLLECTION,
        description="Smart contract logs",
        os_type=OSType.LINUX,
        command_template="python3 collect_blockchain_logs.py {address}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
}


# =============================================================================
# PAYMENT SYSTEMS TOOLS (10 Tools)
# =============================================================================

PAYMENT_SYSTEMS_TOOLS: Dict[str, SecurityTool] = {
    # Payment Gateways (4)
    "stripe_cli": SecurityTool(
        name="Stripe CLI",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Stripe API testing",
        os_type=OSType.LINUX,
        command_template="stripe listen --forward-to {webhook}",
        parameters={},
        output_format="json",
        timeout_seconds=0,
    ),
    "paypal_sdk": SecurityTool(
        name="PayPal SDK",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="PayPal testing",
        os_type=OSType.LINUX,
        command_template="python3 paypal_test.py {config}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "braintree_sdk": SecurityTool(
        name="Braintree SDK",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Braintree testing",
        os_type=OSType.LINUX,
        command_template="python3 braintree_test.py {config}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "square_sdk": SecurityTool(
        name="Square SDK",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Square payment testing",
        os_type=OSType.LINUX,
        command_template="python3 square_test.py {config}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    
    # PCI-DSS Compliance (6)
    "pci_dss_scanner": SecurityTool(
        name="PCI DSS Scanner",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Compliance scanning",
        os_type=OSType.LINUX,
        command_template="python3 pci_scan.py {target}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "card_data_discovery": SecurityTool(
        name="Card Data Discovery",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="PAN/CVV discovery",
        os_type=OSType.LINUX,
        command_template="python3 card_scanner.py {directory}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=4,
    ),
    "encryption_validator": SecurityTool(
        name="Encryption Validator",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Encryption verification",
        os_type=OSType.LINUX,
        command_template="python3 encryption_check.py {target}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "tokenization_checker": SecurityTool(
        name="Tokenization Checker",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Tokenization validation",
        os_type=OSType.LINUX,
        command_template="python3 tokenization_check.py {target}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "hashicorp_vault": SecurityTool(
        name="HashiCorp Vault",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="Secrets management",
        os_type=OSType.LINUX,
        command_template="vault secrets list",
        parameters={},
        output_format="json",
        timeout_seconds=120,
    ),
    "tls_config": SecurityTool(
        name="TLS Config",
        category=ToolCategory.PAYMENT_SYSTEMS,
        description="TLS configuration testing",
        os_type=OSType.LINUX,
        command_template="testssl --json={output} {target}",
        parameters={"output": "tls_results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
}


# =============================================================================
# API SECURITY TOOLS (8 Tools)
# =============================================================================

API_SECURITY_TOOLS: Dict[str, SecurityTool] = {
    "burp_suite": SecurityTool(
        name="Burp Suite",
        category=ToolCategory.API_SECURITY,
        description="Web API testing proxy",
        os_type=OSType.LINUX,
        command_template="java -jar burpsuite.jar",
        parameters={},
        output_format="xml",
        timeout_seconds=0,
    ),
    "owasp_zap": SecurityTool(
        name="OWASP ZAP",
        category=ToolCategory.API_SECURITY,
        description="Automated API vulnerability scanner",
        os_type=OSType.LINUX,
        command_template="zap-cli quick-scan {url}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "postman": SecurityTool(
        name="Postman",
        category=ToolCategory.API_SECURITY,
        description="API testing and automation",
        os_type=OSType.LINUX,
        command_template="newman run {collection}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "httpie": SecurityTool(
        name="HTTPie",
        category=ToolCategory.API_SECURITY,
        description="User-friendly HTTP client",
        os_type=OSType.LINUX,
        command_template="http {url}",
        parameters={},
        output_format="json",
        timeout_seconds=60,
    ),
    "curl": SecurityTool(
        name="cURL",
        category=ToolCategory.API_SECURITY,
        description="Command-line HTTP client",
        os_type=OSType.LINUX,
        command_template="curl -X {method} {url} {headers}",
        parameters={"method": "GET"},
        output_format="text",
        timeout_seconds=60,
    ),
    "jq": SecurityTool(
        name="jq",
        category=ToolCategory.API_SECURITY,
        description="JSON data processing",
        os_type=OSType.LINUX,
        command_template="jq '.key' {input}",
        parameters={},
        output_format="json",
        timeout_seconds=60,
    ),
    "jwt_tool": SecurityTool(
        name="JWT Tool",
        category=ToolCategory.API_SECURITY,
        description="JWT token testing",
        os_type=OSType.LINUX,
        command_template="python3 jwt_tool.py -t {token} -v",
        parameters={},
        output_format="text",
        timeout_seconds=300,
    ),
    "graphql": SecurityTool(
        name="GraphQL",
        category=ToolCategory.API_SECURITY,
        description="GraphQL introspection and vulnerability testing",
        os_type=OSType.LINUX,
        command_template="python3 graphql_scan.py --url {url} --introspection",
        parameters={},
        output_format="json",
        timeout_seconds=600,
        risk_level=3,
    ),
}


# =============================================================================
# BLOCKCHAIN SECURITY TOOLS (6 Tools)
# =============================================================================

BLOCKCHAIN_TOOLS: Dict[str, SecurityTool] = {
    # Smart Contract (4)
    "mythril": SecurityTool(
        name="Mythril",
        category=ToolCategory.BLOCKCHAIN,
        description="Solidity analysis",
        os_type=OSType.LINUX,
        command_template="mythril analyze {contract}",
        parameters={},
        output_format="json",
        timeout_seconds=600,
    ),
    "slither": SecurityTool(
        name="Slither",
        category=ToolCategory.BLOCKCHAIN,
        description="Static analysis for Solidity",
        os_type=OSType.LINUX,
        command_template="slither {contract} --json {output}",
        parameters={"output": "slither_results.json"},
        output_format="json",
        timeout_seconds=600,
    ),
    "echidna": SecurityTool(
        name="Echidna",
        category=ToolCategory.BLOCKCHAIN,
        description="Smart contract fuzzing",
        os_type=OSType.LINUX,
        command_template="echidna-test {contract} --contract {contract_name}",
        parameters={},
        output_format="json",
        timeout_seconds=1200,
    ),
    "manticore": SecurityTool(
        name="Manticore",
        category=ToolCategory.BLOCKCHAIN,
        description="Symbolic execution",
        os_type=OSType.LINUX,
        command_template="manticore {contract}",
        parameters={},
        output_format="text",
        timeout_seconds=1200,
    ),
    
    # Blockchain (2)
    "web3py": SecurityTool(
        name="Web3.py",
        category=ToolCategory.BLOCKCHAIN,
        description="Ethereum interaction",
        os_type=OSType.LINUX,
        command_template="python3 web3_test.py {config}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
    "btc_rpc": SecurityTool(
        name="Bitcoin RPC",
        category=ToolCategory.BLOCKCHAIN,
        description="Bitcoin node testing",
        os_type=OSType.LINUX,
        command_template="bitcoin-cli {command}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
    ),
}


# =============================================================================
# SOCIAL ENGINEERING TOOLS (3 Tools)
# =============================================================================

SOCIAL_ENGINEERING_TOOLS: Dict[str, SecurityTool] = {
    "gophish": SecurityTool(
        name="Gophish",
        category=ToolCategory.DISCOVERY,
        description="Open-source phishing framework",
        os_type=OSType.LINUX,
        command_template="gophish",
        parameters={},
        output_format="json",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "setoolkit": SecurityTool(
        name="Social Engineering Toolkit (SET)",
        category=ToolCategory.DISCOVERY,
        description="Social Engineering Toolkit",
        os_type=OSType.LINUX,
        command_template="python3 setoolkit",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
    "evilginx2": SecurityTool(
        name="Evilginx2",
        category=ToolCategory.DISCOVERY,
        description="Advanced phishing framework for bypassing 2FA",
        os_type=OSType.LINUX,
        command_template="evilginx2",
        parameters={},
        output_format="text",
        timeout_seconds=0,
        risk_level=5,
        requires_approval=True,
    ),
}


# =============================================================================
# COMBINED ALL TOOLS DICTIONARY
# =============================================================================

ALL_SECURITY_TOOLS: Dict[str, SecurityTool] = {
    **DISCOVERY_TOOLS,
    **SCANNING_TOOLS,
    **ENUMERATION_TOOLS,
    **VULNERABILITY_ASSESSMENT_TOOLS,
    **EXPLOITATION_TOOLS,
    **POST_EXPLOITATION_TOOLS,
    **LATERAL_MOVEMENT_TOOLS,
    **EVIDENCE_COLLECTION_TOOLS,
    **PAYMENT_SYSTEMS_TOOLS,
    **BLOCKCHAIN_TOOLS,
    **API_SECURITY_TOOLS,
    **SOCIAL_ENGINEERING_TOOLS,
}


class ToolManager:
    """Tool management class."""
    
    def __init__(self):
        self.tools = ALL_SECURITY_TOOLS
    
    def get_tool(self, tool_name: str) -> Optional[SecurityTool]:
        """Get a specific tool by name."""
        return self.tools.get(tool_name.lower())
    
    def get_tools_by_category(self, category: ToolCategory) -> Dict[str, SecurityTool]:
        """Get all tools in a specific category."""
        return {k: v for k, v in self.tools.items() if v.category == category}
    
    def get_tools_by_os(self, os_type: OSType) -> Dict[str, SecurityTool]:
        """Get all tools for a specific OS type."""
        return {k: v for k, v in self.tools.items() if v.os_type in [os_type, OSType.CROSS_PLATFORM]}
    
    def get_high_risk_tools(self) -> Dict[str, SecurityTool]:
        """Get all high-risk tools (risk_level >= 4)."""
        return {k: v for k, v in self.tools.items() if v.risk_level >= 4}
    
    def get_approval_required_tools(self) -> Dict[str, SecurityTool]:
        """Get all tools requiring approval."""
        return {k: v for k, v in self.tools.items() if v.requires_approval}
    
    def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())
    
    def build_command(self, tool_name: str, parameters: Dict[str, str]) -> str:
        """Build execution command for a tool."""
        tool = self.get_tool(tool_name)
        if not tool or not tool.command_template:
            return ""
        
        command = tool.command_template
        for key, value in parameters.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        return command
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get summary of all configured tools."""
        summary = {
            "total_tools": len(self.tools),
            "by_category": {},
            "by_os": {},
            "high_risk_count": len(self.get_high_risk_tools()),
            "approval_required_count": len(self.get_approval_required_tools()),
        }
        
        # Count by category
        for category in ToolCategory:
            tools = self.get_tools_by_category(category)
            summary["by_category"][category.value] = len(tools)
        
        # Count by OS
        for os_type in OSType:
            tools = self.get_tools_by_os(os_type)
            summary["by_os"][os_type.value] = len(tools)
        
        return summary


# Global tool manager instance
tool_manager = ToolManager()
