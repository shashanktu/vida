from typing import Optional, Literal
from pydantic import BaseModel


class AgentMetricsCreateRequest(BaseModel):
    agent_id: int
    total_runs: Optional[int] = None
    total_success_runs: Optional[int] = None
    total_fail_runs: Optional[int] = None
    agent_status: Literal["active", "idle"] = "idle"

class AgentMetricsUpdateRequest(BaseModel):
    total_runs: Optional[int] = None
    total_success_runs: Optional[int] = None
    total_fail_runs: Optional[int] = None
    agent_status: Optional[Literal["active", "idle"]] = None
