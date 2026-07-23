from pydantic import BaseModel
from typing import Optional

class github_agent_request(BaseModel):
    prompt: str
    pat_token: Optional[str]
    session: Optional[str] = None

class yaml_agent_request(BaseModel):
    prompt: str
    session: Optional[str] = None

class terraform_agent_request(BaseModel):
    prompt: str
    session: Optional[str] = None

class failure_agent_request(BaseModel):
    prompt: str
    pat_token: Optional[str]
    session: Optional[str] = None

class co_ordinator_agent_request(BaseModel):
    prompt: str
    pat_token: Optional[str]
    session: Optional[str] = None
