"""
ANPTOP Backend - Security Tools API Endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import get_current_user, check_permission, audit_log
from app.core.tool_executor import tool_executor, ToolExecutor
from app.core.tools_config import ToolCategory, OSType, ALL_SECURITY_TOOLS


router = APIRouter()


# Pydantic Schemas
class ToolExecuteRequest(BaseModel):
    """Tool execution request schema."""
    tool_name: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    timeout: Optional[int] = None


class ToolResponse(BaseModel):
    """Tool information response schema."""
    name: str
    key: str
    category: str
    os_type: str
    status: str
    risk_level: int
    requires_approval: bool
    description: str


class ToolCategoryResponse(BaseModel):
    """Tool category response schema."""
    category: str
    tool_count: int
    tools: List[Dict[str, Any]]


class ToolsSummaryResponse(BaseModel):
    """Tools summary response schema."""
    total_tools: int
    by_category: Dict[str, int]
    by_os: Dict[str, int]
    high_risk_count: int
    approval_required_count: int


class ToolExecutionResponse(BaseModel):
    """Tool execution response schema."""
    execution_id: str
    tool_name: str
    command: str
    status: str
    return_code: int
    duration_seconds: float
    output_file: Optional[str] = None
    hash_sha256: Optional[str] = None
    timestamp: datetime


@router.get("/", response_model=List[ToolResponse])
async def list_tools(
    category: Optional[ToolCategory] = None,
    os_type: Optional[OSType] = None,
    risk_level: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
):
    """
    List all available security tools.
    
    Optional filters:
    - category: Filter by tool category
    - os_type: Filter by operating system type
    - risk_level: Filter by risk level (1-5)
    """
    tools = tool_executor.list_available_tools()
    
    # Apply filters
    if category:
        tools = [t for t in tools if t["category"] == category.value]
    if os_type:
        tools = [t for t in tools if t["os_type"] == os_type.value]
    if risk_level is not None:
        tools = [t for t in tools if t["risk_level"] == risk_level]
    
    return tools


@router.get("/summary", response_model=ToolsSummaryResponse)
async def get_tools_summary(
    current_user: User = Depends(get_current_user),
):
    """
    Get summary statistics of all tools.
    """
    return tool_executor.get_tools_summary()


@router.get("/categories", response_model=List[ToolCategoryResponse])
async def get_tools_by_category(
    current_user: User = Depends(get_current_user),
):
    """
    Get tools grouped by category.
    """
    categories = []
    for category in ToolCategory:
        tools = tool_executor.get_tools_by_category(category)
        categories.append({
            "category": category.value,
            "tool_count": len(tools),
            "tools": [
                {
                    "name": t.name,
                    "key": name,
                    "risk_level": t.risk_level,
                    "requires_approval": t.requires_approval,
                }
                for name, t in tools.items()
            ],
        })
    return categories


@router.get("/high-risk", response_model=List[Dict[str, Any]])
async def get_high_risk_tools(
    current_user: User = Depends(get_current_user),
):
    """
    Get all high-risk tools (risk level >= 4).
    
    Requires: admin or lead role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LEAD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and leads can view high-risk tools",
        )
    
    return tool_executor.get_high_risk_tools()


@router.get("/approval-required", response_model=List[Dict[str, Any]])
async def get_approval_required_tools(
    current_user: User = Depends(get_current_user),
):
    """
    Get all tools requiring approval before execution.
    
    Requires: admin or lead role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LEAD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and leads can view approval-required tools",
        )
    
    return tool_executor.get_approval_required_tools()


@router.get("/{tool_name}", response_model=ToolResponse)
async def get_tool_info(
    tool_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific tool.
    """
    tool = tool_executor.get_tool(tool_name)
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found",
        )
    
    return {
        "name": tool.name,
        "key": tool_name,
        "category": tool.category.value,
        "os_type": tool.os_type.value,
        "status": tool.status.value,
        "risk_level": tool.risk_level,
        "requires_approval": tool.requires_approval,
        "description": tool.description,
        "command_template": tool.command_template,
        "parameters": tool.parameters,
        "dependencies": tool.dependencies,
        "timeout_seconds": tool.timeout_seconds,
        "output_format": tool.output_format,
    }


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a security tool.
    
    Requires appropriate permissions based on tool risk level.
    High-risk tools require admin or lead approval.
    """
    tool = tool_executor.get_tool(request.tool_name)
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{request.tool_name}' not found",
        )
    
    # Check if tool requires approval
    if tool.requires_approval:
        if current_user.role not in [UserRole.ADMIN, UserRole.LEAD]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tool '{request.tool_name}' requires approval before execution. "
                       "Contact an admin or lead.",
            )
    
    # Check risk level
    if tool.risk_level >= 4:
        if not check_permission(current_user, "workflows:approve"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tool '{request.tool_name}' has high risk level ({tool.risk_level}). "
                       "Approver role required.",
            )
    
    # Check if kill switch is active
    from app.core.security import kill_switch_active
    if kill_switch_active():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kill switch is active. All operations are paused.",
        )
    
    # Execute tool
    result = await tool_executor.execute_tool(
        tool_name=request.tool_name,
        parameters=request.parameters,
        timeout=request.timeout,
    )
    
    # Audit log
    await audit_log(
        action="tool:execute",
        user_id=current_user.id,
        resource="tool_execution",
        details={
            "tool_name": request.tool_name,
            "command": result.command,
            "status": result.status,
            "return_code": result.return_code,
            "risk_level": tool.risk_level,
        },
        db=db,
    )
    
    return {
        "execution_id": str(uuid.uuid4()),
        "tool_name": result.tool_name,
        "command": result.command,
        "status": result.status,
        "return_code": result.return_code,
        "duration_seconds": result.duration_seconds,
        "output_file": result.output_file,
        "hash_sha256": result.hash_sha256,
        "timestamp": result.timestamp,
    }


# Import uuid for execution_id
import uuid
