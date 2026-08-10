from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime

class AgentTaskDetailsCreateRequest(BaseModel):
    repo_name: Optional[str] = None
    branch_name: Optional[str] = None
    agent_id: int
    task_status: Literal["pending", "running", "success", "failed"] = "pending"
    task_prompt: str
    task_name: str
    issue: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AgentTaskDetailsUpdateRequest(BaseModel):
    repo_name: Optional[str] = None
    branch_name: Optional[str] = None
    agent_id: Optional[int] = None
    task_status: Optional[Literal["pending", "running", "success", "failed"]] = None
    task_prompt: Optional[str] = None
    task_name: Optional[str] = None
    issue: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
