from typing import Optional
from pydantic import BaseModel

class ci_builder_request(BaseModel):
    tool: str
    techstack: str
    repo_name: str
    branch_name: str

class cd_builder_request(BaseModel):
    target: str
    techstack: str
    repo_name: str
    resource_group_name: str
    deploy_target_name: str
    tool: str
    branch: str
    artifact_name: str
    workflow_name: str
    ci_file_name: str

class tf_builder_request(BaseModel):
    cloud_provider: str
    resource_group: str
    resources: str
    repo_name: str
    deploy_target_name: str