from typing import Optional,Literal
from datetime import datetime
from pydantic import BaseModel


class AgentRunCreateRequest(BaseModel):
    agent_id: int
    task_id: int
    run_prompt: Optional[str]
    run_logs_path: Optional[str]
    run_result: Optional[dict]
    issue: Optional[str]

    run_status: Literal["pending", "running", "success", "failed"] = "pending"
    start_time: datetime
    end_time: Optional[datetime]

class AgentRunUpdateRequest(BaseModel):
    agent_id: Optional[int]
    task_id: Optional[int]
    run_prompt: Optional[str]
    run_logs_path: Optional[str]
    run_result: Optional[dict]
    issue: Optional[str]

    run_status: Optional[Literal["pending", "running", "success", "failed"]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
