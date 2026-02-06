"""
ANPTOP - Missing Tools Configuration
29 Tools that need to be added to complete 196 tools
"""

from typing import Dict, List
from pydantic import Field
from app.core.tools_config import (
    SecurityTool, ToolCategory, OSType, ToolStatus,
)


# =============================================================================
# ADDITIONAL ENUMERATION TOOLS (8 Tools)
# These should be added to ENUMERATION_TOOLS dict
# =============================================================================

ADDITIONAL_ENUMERATION_TOOLS: Dict[str, SecurityTool] = {
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
}


# =============================================================================
# ADDITIONAL EXPLOITATION TOOLS (10 Tools)
# These should be added to EXPLOITATION_TOOLS dict
# =============================================================================

ADDITIONAL_EXPLOITATION_TOOLS: Dict[str, SecurityTool] = {
    "aws_exploit": SecurityTool(
        name="AWS Exploit",
        category=ToolCategory.EXPLOITATION,
        description="AWS-specific exploits and attack vectors",
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
        description="Azure-specific exploits and attack vectors",
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
        description="GCP-specific exploits and attack vectors",
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
        description="Cloud privilege escalation detection and exploitation",
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
        description="Azure AD exploitation and privilege escalation",
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
        description="S3 bucket misconfiguration exploitation",
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
        description="Lambda function injection and exploitation",
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
}


# =============================================================================
# ADDITIONAL POST-EXPLOITATION TOOLS (9 Tools)
# These should be added to POST_EXPLOITATION_TOOLS dict
# =============================================================================

ADDITIONAL_POST_EXPLOITATION_TOOLS: Dict[str, SecurityTool] = {
    "aws_keys": SecurityTool(
        name="AWS Keys",
        category=ToolCategory.POST_EXPLOITATION,
        description="AWS credential harvesting from metadata and config",
        os_type=OSType.CLOUD,
        command_template="curl http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        parameters={},
        output_format="json",
        timeout_seconds=60,
        risk_level=5,
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
    ),
    "gcp_keys": SecurityTool(
        name="GCP Keys",
        category=ToolCategory.POST_EXPLOITATION,
        description="GCP credential harvesting",
        os_type=OSType.CLOUD,
        command_template="gcloud compute instances describe {instance} --zone {zone} --format='json(serviceAccounts)'",
        parameters={},
        output_format="json",
        timeout_seconds=120,
        risk_level=5,
    ),
    "aws_ssm_post": SecurityTool(
        name="AWS SSM",
        category=ToolCategory.POST_EXPLOITATION,
        description="Systems Manager command execution",
        os_type=OSType.CLOUD,
        command_template="aws ssm send-command --instance-ids {instance} --document-name AWS-RunShellScript --parameters commands={command}",
        parameters={},
        output_format="json",
        timeout_seconds=300,
        risk_level=5,
    ),
    "aws_lambda_post": SecurityTool(
        name="AWS Lambda",
        category=ToolCategory.POST_EXPLOITATION,
        description="Lambda function enumeration and access",
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
        description="CloudTrail log analysis and manipulation",
        os_type=OSType.CLOUD,
        command_template="aws cloudtrail lookup-events --start-time {start} --end-time {end}",
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
    ),
}


# =============================================================================
# ADDITIONAL LATERAL MOVEMENT TOOLS (2 Tools)
# These should be added to LATERAL_MOVEMENT_TOOLS dict
# =============================================================================

ADDITIONAL_LATERAL_MOVEMENT_TOOLS: Dict[str, SecurityTool] = {
    "cross_account": SecurityTool(
        name="Cross-Account",
        category=ToolCategory.LATERAL_MOVEMENT,
        description="Cross-account access via role chaining",
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
        description="IAM role chaining for lateral movement",
        os_type=OSType.CLOUD,
        command_template="aws sts assume-role --role-arn {role} --role-session-name {session}",
        parameters={},
        output_format="json",
        timeout_seconds=120,
        risk_level=5,
        requires_approval=True,
    ),
}


# =============================================================================
# ADDITIONAL API SECURITY TOOLS (1 Tool)
# This should be added to API SECURITY section
# =============================================================================

ADDITIONAL_API_SECURITY_TOOLS: Dict[str, SecurityTool] = {
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
# SOCIAL ENGINEERING TOOLS (3 - Optional)
# These are optional tools for social engineering campaigns
# =============================================================================

SOCIAL_ENGINEERING_TOOLS: Dict[str, SecurityTool] = {
    "gophish": SecurityTool(
        name="Gophish",
        category=ToolCategory.DISCOVERY,  # Using DISCOVERY as placeholder
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
        category=ToolCategory.DISCOVERY,  # Using DISCOVERY as placeholder
        description="Social Engineering Toolkit for penetration testing",
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
        category=ToolCategory.DISCOVERY,  # Using DISCOVERY as placeholder
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
# COMPLETE LIST OF ALL MISSING TOOLS
# =============================================================================

ALL_MISSING_TOOLS: Dict[str, SecurityTool] = {
    **ADDITIONAL_ENUMERATION_TOOLS,
    **ADDITIONAL_EXPLOITATION_TOOLS,
    **ADDITIONAL_POST_EXPLOITATION_TOOLS,
    **ADDITIONAL_LATERAL_MOVEMENT_TOOLS,
    **ADDITIONAL_API_SECURITY_TOOLS,
    **SOCIAL_ENGINEERING_TOOLS,
}


# Summary of missing tools
MISSING_TOOLS_SUMMARY = {
    "enumeration": 8,
    "exploitation": 10,
    "post_exploitation": 9,
    "lateral_movement": 2,
    "api_security": 1,
    "social_engineering": 3,
    "total": 33,
}
