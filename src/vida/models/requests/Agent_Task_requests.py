from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime

class AgentTaskDetailsCreateRequest(BaseModel):
    repo_name: Optional[str]
    branch_name: Optional[str]
    agent_id: int
    task_status: Literal["pending", "running", "success", "failed"] = "pending"
    task_prompt: str
    task_name: str
    issue: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class AgentTaskDetailsUpdateRequest(BaseModel):
    repo_name: Optional[str]
    branch_name: Optional[str]
    agent_id: Optional[int]
    task_status: Optional[Literal["pending", "running", "success", "failed"]]
    task_prompt: Optional[str]
    task_name: Optional[str]
    issue: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
