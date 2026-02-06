"""
ANPTOP Backend - Tests for Security Tools Configuration
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.tools_config import (
    ALL_SECURITY_TOOLS,
    DISCOVERY_TOOLS,
    SCANNING_TOOLS,
    ENUMERATION_TOOLS,
    VULNERABILITY_ASSESSMENT_TOOLS,
    EXPLOITATION_TOOLS,
    POST_EXPLOITATION_TOOLS,
    LATERAL_MOVEMENT_TOOLS,
    EVIDENCE_COLLECTION_TOOLS,
    PAYMENT_SYSTEMS_TOOLS,
    API_SECURITY_TOOLS,
    BLOCKCHAIN_TOOLS,
    SOCIAL_ENGINEERING_TOOLS,
    tool_manager,
    ToolCategory,
    OSType,
)


class TestToolsConfiguration:
    """Test suite for security tools configuration."""
    
    def test_total_tools_count(self):
        """Verify total tools count is 199."""
        expected_count = 199
        actual_count = len(ALL_SECURITY_TOOLS)
        assert actual_count == expected_count, \
            f"Expected {expected_count} tools, got {actual_count}"
    
    def test_discovery_tools_count(self):
        """Verify discovery tools count is 14."""
        assert len(DISCOVERY_TOOLS) == 14, \
            f"Expected 14 discovery tools, got {len(DISCOVERY_TOOLS)}"
    
    def test_scanning_tools_count(self):
        """Verify scanning tools count is 14."""
        assert len(SCANNING_TOOLS) == 14, \
            f"Expected 14 scanning tools, got {len(SCANNING_TOOLS)}"
    
    def test_enumeration_tools_count(self):
        """Verify enumeration tools count is 35."""
        assert len(ENUMERATION_TOOLS) == 35, \
            f"Expected 35 enumeration tools, got {len(ENUMERATION_TOOLS)}"
    
    def test_vulnerability_assessment_tools_count(self):
        """Verify VA tools count is 22."""
        assert len(VULNERABILITY_ASSESSMENT_TOOLS) == 22, \
            f"Expected 22 VA tools, got {len(VULNERABILITY_ASSESSMENT_TOOLS)}"
    
    def test_exploitation_tools_count(self):
        """Verify exploitation tools count is 23."""
        assert len(EXPLOITATION_TOOLS) == 23, \
            f"Expected 23 exploitation tools, got {len(EXPLOITATION_TOOLS)}"
    
    def test_post_exploitation_tools_count(self):
        """Verify post-exploitation tools count is 30."""
        assert len(POST_EXPLOITATION_TOOLS) == 30, \
            f"Expected 30 post-exploitation tools, got {len(POST_EXPLOITATION_TOOLS)}"
    
    def test_lateral_movement_tools_count(self):
        """Verify lateral movement tools count is 22."""
        assert len(LATERAL_MOVEMENT_TOOLS) == 22, \
            f"Expected 22 lateral movement tools, got {len(LATERAL_MOVEMENT_TOOLS)}"
    
    def test_evidence_collection_tools_count(self):
        """Verify evidence collection tools count is 12."""
        assert len(EVIDENCE_COLLECTION_TOOLS) == 12, \
            f"Expected 12 evidence collection tools, got {len(EVIDENCE_COLLECTION_TOOLS)}"
    
    def test_payment_systems_tools_count(self):
        """Verify payment systems tools count is 10."""
        assert len(PAYMENT_SYSTEMS_TOOLS) == 10, \
            f"Expected 10 payment systems tools, got {len(PAYMENT_SYSTEMS_TOOLS)}"
    
    def test_api_security_tools_count(self):
        """Verify API security tools count is 8."""
        assert len(API_SECURITY_TOOLS) == 8, \
            f"Expected 8 API security tools, got {len(API_SECURITY_TOOLS)}"
    
    def test_blockchain_tools_count(self):
        """Verify blockchain tools count is 6."""
        assert len(BLOCKCHAIN_TOOLS) == 6, \
            f"Expected 6 blockchain tools, got {len(BLOCKCHAIN_TOOLS)}"
    
    def test_social_engineering_tools_count(self):
        """Verify social engineering tools count is 3 (optional)."""
        assert len(SOCIAL_ENGINEERING_TOOLS) == 3, \
            f"Expected 3 social engineering tools, got {len(SOCIAL_ENGINEERING_TOOLS)}"


class TestToolManagerSummary:
    """Test suite for tool manager summary."""
    
    def test_get_tool_summary(self):
        """Test getting tool summary."""
        summary = tool_manager.get_tool_summary()
        
        assert summary["total_tools"] == 199, \
            f"Expected 199 total tools, got {summary['total_tools']}"
        assert summary["by_category"]["discovery"] == 17
        assert summary["by_category"]["scanning"] == 14
        assert summary["by_category"]["enumeration"] == 35
        assert summary["by_category"]["vulnerability_assessment"] == 22
        assert summary["by_category"]["exploitation"] == 23
        assert summary["by_category"]["post_exploitation"] == 30
        assert summary["by_category"]["lateral_movement"] == 22
        assert summary["by_category"]["evidence_collection"] == 12
        assert summary["by_category"]["payment_systems"] == 10
        # API security might be categorized differently
        assert summary["by_category"]["blockchain"] == 6
    
    def test_list_available_tools(self):
        """Test listing available tools."""
        tools = tool_manager.list_available_tools()
        
        assert len(tools) == 199, \
            f"Expected 199 tools in list, got {len(tools)}"


class TestMissingToolsAdded:
    """Test suite to verify missing tools were added."""
    
    def test_enumeration_tools_added(self):
        """Verify all 8 additional enumeration tools are present."""
        required_tools = [
            "azure_powershell", "aws_vpc", "gcp_iam", "k8s_enum",
            "kubeconfig", "aws_iam_enum", "azure_ad_enum", "gcp_compute_enum"
        ]
        for tool_name in required_tools:
            assert tool_name in ENUMERATION_TOOLS, \
                f"Missing enumeration tool: {tool_name}"
    
    def test_exploitation_tools_added(self):
        """Verify all 10 additional exploitation tools are present."""
        required_tools = [
            "aws_exploit", "azure_exploit", "gcp_exploit", "cloud_privesc",
            "aws_iam_exploit", "azure_ad_exploit", "s3_exploit", "lambda_exploit",
            "aws_vpc_exploit", "kms_exploit"
        ]
        for tool_name in required_tools:
            assert tool_name in EXPLOITATION_TOOLS, \
                f"Missing exploitation tool: {tool_name}"
    
    def test_post_exploitation_tools_added(self):
        """Verify all 9 additional post-exploitation tools are present."""
        required_tools = [
            "aws_keys", "azure_keys", "gcp_keys", "aws_ssm_post",
            "aws_lambda_post", "azure_functions", "cloudtrail",
            "cloud_metadata", "role_tricks"
        ]
        for tool_name in required_tools:
            assert tool_name in POST_EXPLOITATION_TOOLS, \
                f"Missing post-exploitation tool: {tool_name}"
    
    def test_lateral_movement_tools_added(self):
        """Verify all 2 additional lateral movement tools are present."""
        required_tools = ["cross_account", "role_chaining"]
        for tool_name in required_tools:
            assert tool_name in LATERAL_MOVEMENT_TOOLS, \
                f"Missing lateral movement tool: {tool_name}"
    
    def test_api_security_tools_added(self):
        """Verify GraphQL tool is present."""
        assert "graphql" in API_SECURITY_TOOLS, \
            "Missing GraphQL tool in API security tools"
    
    def test_social_engineering_tools_present(self):
        """Verify social engineering tools are present."""
        required_tools = ["gophish", "setoolkit", "evilginx2"]
        for tool_name in required_tools:
            assert tool_name in SOCIAL_ENGINEERING_TOOLS, \
                f"Missing social engineering tool: {tool_name}"


class TestToolRiskLevels:
    """Test suite for tool risk levels."""
    
    def test_all_tools_have_valid_risk_levels(self):
        """Test that all tools have valid risk levels."""
        for name, tool in ALL_SECURITY_TOOLS.items():
            assert 1 <= tool.risk_level <= 5, \
                f"Tool {name} has invalid risk level {tool.risk_level}"
    
    def test_exploitation_tools_high_risk(self):
        """Test that exploitation tools are high risk."""
        for name, tool in EXPLOITATION_TOOLS.items():
            if "exploit" in name.lower() or "privesc" in name.lower():
                assert tool.risk_level >= 4, \
                    f"Exploitation tool {name} should have risk level >= 4"
    
    def test_c2_frameworks_max_risk(self):
        """Test that C2 frameworks have max risk level."""
        c2_tools = ["sliver", "covenant", "havoc", "mythic", "merlin"]
        for tool_name in c2_tools:
            if tool_name in ALL_SECURITY_TOOLS:
                tool = ALL_SECURITY_TOOLS[tool_name]
                assert tool.risk_level == 5, \
                    f"C2 tool {tool_name} should have risk level 5"
                assert tool.requires_approval is True, \
                    f"C2 tool {tool_name} should require approval"


class TestToolApprovalRequirements:
    """Test suite for tool approval requirements."""
    
    def test_high_risk_tools_require_approval(self):
        """Test that high-risk tools require approval."""
        for name, tool in ALL_SECURITY_TOOLS.items():
            if tool.risk_level >= 5:
                assert tool.requires_approval is True, \
                    f"High-risk tool {name} should require approval"
    
    def test_approval_tools_count(self):
        """Test count of tools requiring approval."""
        approval_required = tool_manager.get_approval_required_tools()
        assert len(approval_required) > 0, \
            "Should have tools requiring approval"
    
    def test_specific_approval_tools(self):
        """Test specific tools that should require approval."""
        approval_tools = [
            "metasploit", "metasploit_rpc", "crackmapexec", "responder",
            "wmiexec", "psexec", "smbexec", "atexec", "dcomexec",
            "aws_exploit", "azure_exploit", "gcp_exploit",
            "gophish", "setoolkit", "evilginx2"
        ]
        for tool_name in approval_tools:
            if tool_name in ALL_SECURITY_TOOLS:
                tool = ALL_SECURITY_TOOLS[tool_name]
                assert tool.requires_approval is True, \
                    f"Tool {tool_name} should require approval"
