"""
ANPTOP - Security Tool Executor Service
Executes security tools based on configuration and captures results
"""

import asyncio
import subprocess
import json
import os
import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import aiofiles
import pydantic
from loguru import logger

from app.core.config import settings
from app.core.tools_config import (
    ALL_SECURITY_TOOLS,
    SecurityTool,
    ToolCategory,
    OSType,
    ToolStatus,
    tool_manager,
)


class ToolExecutionResult(pydantic.BaseModel):
    """Result of tool execution."""
    tool_name: str
    command: str
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    status: str
    output_file: Optional[str] = None
    hash_sha256: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class ToolExecutor:
    """Executes security tools with proper isolation and logging."""
    
    def __init__(self):
        self.tools = ALL_SECURITY_TOOLS
        self.execution_history: List[ToolExecutionResult] = []
        self.base_output_dir = Path(settings.EVIDENCE_STORAGE_PATH)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, str],
        timeout: Optional[int] = None,
        capture_output: bool = True,
    ) -> ToolExecutionResult:
        """
        Execute a security tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Dictionary of parameters for command substitution
            timeout: Optional timeout in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            ToolExecutionResult with execution details
        """
        tool = tool_manager.get_tool(tool_name)
        
        if not tool:
            return ToolExecutionResult(
                tool_name=tool_name,
                command="",
                return_code=-1,
                stdout="",
                stderr=f"Tool '{tool_name}' not found",
                duration_seconds=0,
                status="failed",
            )
        
        # Build command
        command = tool_manager.build_command(tool_name, parameters)
        
        if not command:
            return ToolExecutionResult(
                tool_name=tool_name,
                command="",
                return_code=-1,
                stdout="",
                stderr=f"Cannot build command for tool '{tool_name}'",
                duration_seconds=0,
                status="failed",
            )
        
        # Create output directory for this execution
        execution_id = str(uuid.uuid4())
        output_dir = self.base_output_dir / execution_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default timeout
        if timeout is None:
            timeout = tool.timeout_seconds
        
        logger.info(f"Executing tool: {tool_name}")
        logger.debug(f"Command: {command}")
        
        start_time = datetime.utcnow()
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE if capture_output else asyncio.subprocess.DEVNULL,
                cwd=str(output_dir),
                limit=10 * 1024 * 1024,  # 10MB output limit
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return_code = -1
                stdout = b"Command timed out"
                stderr = b"Process killed due to timeout"
                logger.warning(f"Tool {tool_name} timed out after {timeout}s")
            else:
                return_code = process.returncode
                stdout = stdout.decode("utf-8", errors="replace")
                stderr = stderr.decode("utf-8", errors="replace")
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Save output to file
            output_file = None
            hash_sha256 = None
            if capture_output and (stdout or stderr):
                output_file = str(output_dir / f"{tool_name}_output.txt")
                content = f"# Command: {command}\n"
                content += f"# Return Code: {return_code}\n"
                content += f"# Duration: {duration:.2f}s\n"
                content += f"# Timestamp: {start_time.isoformat()}\n"
                content += f"# STDOUT:\n{stdout}\n"
                content += f"# STDERR:\n{stderr}\n"
                
                async with aiofiles.open(output_file, "w") as f:
                    await f.write(content)
                
                # Calculate hash
                hash_sha256 = hashlib.sha256(content.encode()).hexdigest()
            
            result = ToolExecutionResult(
                tool_name=tool_name,
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
                status="success" if return_code == 0 else "failed",
                output_file=output_file,
                hash_sha256=hash_sha256,
            )
            
            self.execution_history.append(result)
            
            logger.info(
                f"Tool {tool_name} completed with status={result.status}, "
                f"duration={duration:.2f}s, return_code={return_code}"
            )
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Tool {tool_name} execution failed: {str(e)}")
            
            result = ToolExecutionResult(
                tool_name=tool_name,
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                duration_seconds=duration,
                status="error",
            )
            
            self.execution_history.append(result)
            return result
    
    async def execute_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, str],
        callback=None,
    ) -> str:
        """
        Execute a tool asynchronously and call callback with result.
        
        Returns:
            Execution ID for tracking
        """
        execution_id = str(uuid.uuid4())
        
        async def run_and_callback():
            result = await self.execute_tool(tool_name, parameters)
            if callback:
                callback(result)
            return result
        
        # Schedule execution
        asyncio.create_task(run_and_callback())
        
        return execution_id
    
    def get_tool(self, tool_name: str) -> Optional[SecurityTool]:
        """Get tool configuration."""
        return tool_manager.get_tool(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> Dict[str, SecurityTool]:
        """Get all tools in a category."""
        return tool_manager.get_tools_by_category(category)
    
    def get_tools_summary(self) -> Dict[str, Any]:
        """Get summary of all tools."""
        return tool_manager.get_tool_summary()
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with their status."""
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": tool.name,
                "key": name,
                "category": tool.category.value,
                "os_type": tool.os_type.value,
                "status": tool.status.value,
                "risk_level": tool.risk_level,
                "requires_approval": tool.requires_approval,
                "description": tool.description,
            })
        return tools_list
    
    def get_high_risk_tools(self) -> List[Dict[str, Any]]:
        """Get all high-risk tools."""
        tools = []
        for name, tool in self.tools.items():
            if tool.risk_level >= 4:
                tools.append({
                    "name": tool.name,
                    "key": name,
                    "risk_level": tool.risk_level,
                    "requires_approval": tool.requires_approval,
                })
        return tools
    
    def get_approval_required_tools(self) -> List[Dict[str, Any]]:
        """Get all tools requiring approval."""
        tools = []
        for name, tool in self.tools.items():
            if tool.requires_approval:
                tools.append({
                    "name": tool.name,
                    "key": name,
                    "risk_level": tool.risk_level,
                    "category": tool.category.value,
                })
        return tools


# Global executor instance
tool_executor = ToolExecutor()
