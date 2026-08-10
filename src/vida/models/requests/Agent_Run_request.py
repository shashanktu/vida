from typing import Optional,Literal
from datetime import datetime
from pydantic import BaseModel


class AgentRunCreateRequest(BaseModel):
    agent_id: int
    task_id: int
    run_prompt: Optional[str] = None
    run_logs_path: Optional[str] = None
    run_result: Optional[dict] = None
    raw_run_result: Optional[dict] = None
    issue: Optional[str] = None

    run_status: Literal["pending", "running", "success", "failed"] = "pending"
    start_time: datetime
    end_time: Optional[datetime] = None

class AgentRunUpdateRequest(BaseModel):
    agent_id: Optional[int] = None
    task_id: Optional[int] = None
    run_prompt: Optional[str] = None
    run_logs_path: Optional[str] = None
    run_result: Optional[dict] = None
    raw_run_result: Optional[dict] = None
    issue: Optional[str] = None

    run_status: Optional[Literal["pending", "running", "success", "failed"]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
