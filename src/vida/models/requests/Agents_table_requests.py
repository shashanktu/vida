from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentCreateRequest(BaseModel):
    agent_name: str
    wrapper_prompt_path: Optional[str] = None
    required_fields: Optional[dict] = None

    created_by: str
    created_at: datetime

class AgentUpdateRequest(BaseModel):
    agent_name: Optional[str] = None
    wrapper_prompt_path: Optional[str] = None
    required_fields: Optional[dict] = None

    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None   