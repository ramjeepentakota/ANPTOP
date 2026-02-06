"""
ANPTOP Backend - Workflow Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.workflow import Workflow, WorkflowType, WorkflowStatus, WorkflowExecution
from app.models.engagement import Engagement
from app.core.security import get_current_user, audit_log, check_permission


router = APIRouter()


# Pydantic schemas
class WorkflowResponse(BaseModel):
    """Workflow response schema."""
    id: int
    n8n_workflow_id: Optional[str]
    name: str
    description: Optional[str]
    workflow_type: WorkflowType
    requires_approval: bool
    approval_role: str
    timeout_minutes: int
    max_retries: int
    is_active: bool
    is_template: bool
    tags: List[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response schema."""
    id: int
    workflow_id: int
    engagement_id: int
    target_id: Optional[int]
    executed_by_id: Optional[int]
    status: WorkflowStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    parameters: dict
    results: dict
    findings: List[dict]
    error_message: Optional[str]
    retry_count: int
    evidence_collected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExecuteWorkflowRequest(BaseModel):
    """Workflow execution request schema."""
    workflow_id: int
    engagement_id: int
    target_ids: Optional[List[int]] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)
    skip_approval: bool = False


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    workflow_type: Optional[WorkflowType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all available workflows.
    """
    if workflow_type:
        workflows = await Workflow.get_by_type(db, workflow_type)
    else:
        workflows = await Workflow.get_all(db, skip=skip, limit=limit)
    
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get workflow by ID.
    """
    workflow = await Workflow.get_by_id(db, workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    return workflow


@router.post("/execute", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_workflow(
    request: ExecuteWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a workflow.
    
    If the workflow requires approval, creates an approval request.
    """
    # Verify workflow exists and is active
    workflow = await Workflow.get_by_id(db, request.workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active",
        )
    
    # Verify engagement exists
    engagement = await Engagement.get_by_id(db, request.engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    # Check permissions
    if not check_permission(current_user, "workflows:execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to execute workflows",
        )
    
    # Create execution record
    execution = WorkflowExecution(
        workflow_id=request.workflow_id,
        engagement_id=request.engagement_id,
        executed_by_id=current_user.id,
        parameters=request.parameters,
        status=WorkflowStatus.PENDING,
    )
    
    await execution.save(db)
    
    # Check if approval is required
    if workflow.requires_approval and not request.skip_approval:
        execution.status = WorkflowStatus.APPROVAL_REQUIRED
        await execution.update(db)
        
        # Create approval request
        from app.models.approval import Approval, ApprovalType, ApprovalStatus
        approval = Approval(
            engagement_id=request.engagement_id,
            approval_type=ApprovalType.WORKFLOW_EXECUTION,
            title=f"Workflow Execution: {workflow.name}",
            description=f"Execute {workflow.name} on engagement {engagement.name}",
            requested_by_id=current_user.id,
            workflow_execution_id=execution.id,
            priority=5,
            request_data={
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "target_ids": request.target_ids,
                "parameters": request.parameters,
            },
        )
        await approval.save(db)
        
        return execution
    
    # Start execution
    if engagement.auto_approve_workflows:
        execution.status = WorkflowStatus.QUEUED
        await execution.update(db)
        
        # Trigger n8n workflow here
        # This would call n8n API to start the workflow
        
    else:
        execution.status = WorkflowStatus.QUEUED
        await execution.update(db)
    
    # Audit log
    await audit_log(
        action="workflow:execute",
        user_id=current_user.id,
        resource="workflow_execution",
        details={
            "execution_id": execution.id,
            "workflow_id": workflow.id,
            "engagement_id": request.engagement_id,
        },
        db=db,
    )
    
    return execution


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get workflow execution by ID.
    """
    execution = await WorkflowExecution.get_by_id(db, execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )
    
    return execution


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
async def list_executions(
    engagement_id: int = Query(..., description="Engagement ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List workflow executions for an engagement.
    """
    if not check_permission(current_user, "workflows:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view executions",
        )
    
    executions = await WorkflowExecution.get_by_engagement(db, engagement_id, skip=skip, limit=limit)
    return executions


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a running workflow execution.
    """
    execution = await WorkflowExecution.get_by_id(db, execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )
    
    if execution.status not in [WorkflowStatus.RUNNING, WorkflowStatus.QUEUED, WorkflowStatus.APPROVAL_REQUIRED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel execution with status: {execution.status}",
        )
    
    # Check permissions
    if not check_permission(current_user, "workflows:execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel executions",
        )
    
    execution.status = WorkflowStatus.CANCELLED
    await execution.update(db)
    
    # Audit log
    await audit_log(
        action="workflow:cancel",
        user_id=current_user.id,
        resource="workflow_execution",
        details={"execution_id": execution_id},
        db=db,
    )
    
    return {"message": "Execution cancelled successfully", "execution": execution}


@router.get("/pending", response_model=List[WorkflowExecutionResponse])
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List workflow executions awaiting approval.
    """
    if not check_permission(current_user, "workflows:approve"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve workflows",
        )
    
    executions = await WorkflowExecution.get_pending_approvals(db, current_user.role.value)
    return executions
