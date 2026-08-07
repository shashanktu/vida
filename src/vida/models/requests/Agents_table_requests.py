from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentCreateRequest(BaseModel):
    agent_name: str
    wrapper_prompt_path: Optional[str]
    required_fields: Optional[dict]

    created_by: str
    created_at: datetime

class AgentUpdateRequest(BaseModel):
    agent_name: Optional[str]
    wrapper_prompt_path: Optional[str]
    required_fields: Optional[dict]

    updated_by: Optional[str]
    updated_at: Optional[datetime]