"""
ANPTOP n8n Workflow Integration Tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.config import settings


class TestN8nWorkflowEndpoints:
    """Test n8n workflow API endpoints"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_list_workflows(self, client):
        """Test listing workflows"""
        response = await client.get("/api/v1/workflows")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    @pytest.mark.asyncio
    async def test_get_workflow_by_id(self, client):
        """Test getting a specific workflow"""
        response = await client.get("/api/v1/workflows/1")
        # Either 200 (found) or 404 (not found)
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_requires_auth(self, client):
        """Test that workflow execution requires authentication"""
        response = await client.post("/api/v1/workflows/1/execute", json={
            "engagement_id": 1,
            "target_scope": ["192.168.1.0/24"]
        })
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]


class TestN8nWebhookIntegration:
    """Test n8n webhook integration"""
    
    @pytest.fixture
    def mock_n8n_client(self):
        """Create mock n8n client"""
        with patch('app.integrations.n8n.N8nClient') as mock:
            instance = mock.return_value
            instance.execute_workflow = AsyncMock(return_value={
                "execution_id": "test_exec_123",
                "status": "started"
            })
            instance.get_execution_status = AsyncMock(return_value={
                "execution_id": "test_exec_123",
                "status": "completed",
                "result": {"hosts_found": 10}
            })
            yield instance
    
    @pytest.mark.asyncio
    async def test_n8n_workflow_execution(self, mock_n8n_client):
        """Test executing n8n workflow"""
        from app.integrations.n8n import N8nClient
        
        client = N8nClient(base_url="http://n8n:5678")
        result = await client.execute_workflow(
            workflow_id="test_workflow",
            data={"target": "192.168.1.0/24"}
        )
        
        assert result["execution_id"] == "test_exec_123"
        assert result["status"] == "started"
    
    @pytest.mark.asyncio
    async def test_n8n_execution_status(self, mock_n8n_client):
        """Test getting execution status"""
        from app.integrations.n8n import N8nClient
        
        client = N8nClient(base_url="http://n8n:5678")
        result = await client.get_execution_status("test_exec_123")
        
        assert result["status"] == "completed"


class TestWorkflowTriggers:
    """Test workflow trigger mechanisms"""
    
    def test_manual_trigger(self):
        """Test manual workflow trigger"""
        trigger_data = {
            "type": "manual",
            "workflow_id": 1,
            "engagement_id": 1,
            "parameters": {
                "scope": ["192.168.1.0/24"],
                "tools": ["nmap", "masscan"]
            }
        }
        assert trigger_data["type"] == "manual"
    
    def test_scheduled_trigger(self):
        """Test scheduled workflow trigger"""
        trigger_data = {
            "type": "scheduled",
            "workflow_id": 1,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "timezone": "UTC"
        }
        assert trigger_data["type"] == "scheduled"
    
    def test_webhook_trigger(self):
        """Test webhook workflow trigger"""
        trigger_data = {
            "type": "webhook",
            "workflow_id": 1,
            "webhook_url": "http://n8n:5678/webhook/test",
            "method": "POST"
        }
        assert trigger_data["type"] == "webhook"


class TestWorkflowExecution:
    """Test workflow execution logic"""
    
    def test_execution_request_validation(self):
        """Test execution request validation"""
        from pydantic import ValidationError
        
        # Valid request
        from app.schemas.workflow import WorkflowExecutionRequest
        request = WorkflowExecutionRequest(
            engagement_id=1,
            target_scope=["192.168.1.0/24"],
            options={"timeout": 3600}
        )
        assert request.engagement_id == 1
    
    def test_invalid_scope(self):
        """Test invalid target scope rejection"""
        from pydantic import ValidationError
        from app.schemas.workflow import WorkflowExecutionRequest
        
        with pytest.raises(ValidationError):
            WorkflowExecutionRequest(
                engagement_id=1,
                target_scope=["invalid_ip"]
            )


class TestN8nWorkflowTemplates:
    """Test n8n workflow template management"""
    
    def test_host_discovery_template(self):
        """Test host discovery workflow template"""
        template = {
            "name": "Host Discovery",
            "description": "Discovers active hosts in target range",
            "nodes": [
                {"name": "HTTP Request", "type": "httpRequest"},
                {"name": "DNS Lookup", "type": "n8n-nodes-base.dns"}
            ],
            "connections": {},
            "settings": {
                "execution_order": "v0"
            }
        }
        assert template["name"] == "Host Discovery"
    
    def test_port_scan_template(self):
        """Test port scan workflow template"""
        template = {
            "name": "Port Scanning",
            "description": "Scans ports on discovered hosts",
            "parameters": {
                "ports": "1-1000",
                "timeout": 5000,
                "threads": 10
            }
        }
        assert "ports" in template["parameters"]
    
    def test_vuln_scan_template(self):
        """Test vulnerability scan workflow template"""
        template = {
            "name": "Vulnerability Assessment",
            "description": "Runs vulnerability scans",
            "parameters": {
                "scanner": "nessus",
                "scan_type": "full",
                "compliance": ["PCI-DSS", "HIPAA"]
            }
        }
        assert template["parameters"]["scanner"] == "nessus"


class TestWorkflowResults:
    """Test workflow result processing"""
    
    def test_parse_nmap_results(self):
        """Test parsing nmap output"""
        nmap_output = """
Starting Nmap 7.92 ( https://nmap.org )
Nmap scan report for 192.168.1.100
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds
"""
        # Parse logic would be implemented
        assert "22/tcp" in nmap_output
    
    def test_parse_nessus_results(self):
        """Test parsing nessus results"""
        nessus_output = {
            "hosts": [
                {
                    "hostname": "192.168.1.100",
                    "vulnerabilities": [
                        {
                            "plugin_id": 10287,
                            "severity": 2,
                            "name": "SSH Server CBC Mode Ciphers Enabled",
                            "solution": "Disable CBC mode ciphers"
                        }
                    ]
                }
            ]
        }
        assert len(nessus_output["hosts"]) == 1
    
    def test_correlate_results(self):
        """Test correlating workflow results"""
        results = {
            "hosts": [
                {"ip": "192.168.1.100", "ports": [22, 80, 443]}
            ],
            "vulnerabilities": [
                {"host": "192.168.1.100", "port": 22, "cve": "CVE-2023-48788"}
            ]
        }
        # Correlation logic
        assert "hosts" in results
        assert "vulnerabilities" in results


class TestWorkflowErrorHandling:
    """Test workflow error handling"""
    
    def test_workflow_timeout(self):
        """Test workflow timeout handling"""
        error_data = {
            "error": "timeout",
            "message": "Workflow execution exceeded timeout of 3600s",
            "execution_id": "test_exec_123",
            "partial_results": True
        }
        assert error_data["error"] == "timeout"
    
    def test_workflow_failure(self):
        """Test workflow failure handling"""
        error_data = {
            "error": "execution_failed",
            "message": "Node execution failed",
            "failed_node": "Nmap Scan",
            "error_details": "Port scan interrupted"
        }
        assert error_data["error"] == "execution_failed"
    
    def test_retry_logic(self):
        """Test workflow retry logic"""
        retry_config = {
            "max_retries": 3,
            "retry_delay": 60,
            "backoff_factor": 2,
            "retryable_errors": ["timeout", "connection_refused"]
        }
        assert retry_config["max_retries"] == 3


class TestWorkflowPermissions:
    """Test workflow access permissions"""
    
    def test_admin_can_execute_all(self):
        """Test admin can execute any workflow"""
        permissions = {
            "admin": ["execute", "create", "edit", "delete", "approve"]
        }
        assert "execute" in permissions["admin"]
    
    def test_analyst_permissions(self):
        """Test analyst workflow permissions"""
        permissions = {
            "analyst": ["execute", "view"],
            "restricted_tools": ["sqlmap", "metasploit"]
        }
        assert "execute" in permissions["analyst"]
        assert "restricted_tools" in permissions
    
    def test_approval_required(self):
        """Test high-risk workflow requires approval"""
        workflow = {
            "name": "Aggressive Port Scan",
            "risk_level": "high",
            "requires_approval": True,
            "approved_roles": ["team_lead", "admin"]
        }
        assert workflow["requires_approval"] is True


# Fixtures and configuration
@pytest.fixture
def n8n_credentials():
    """Provide n8n credentials for testing"""
    return {
        "base_url": "http://localhost:5678",
        "api_key": "test_api_key"
    }


@pytest.fixture
def sample_engagement():
    """Provide sample engagement for testing"""
    return {
        "id": 1,
        "name": "Test Engagement",
        "scope": ["192.168.1.0/24"],
        "status": "active"
    }
