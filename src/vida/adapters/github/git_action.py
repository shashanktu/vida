from typing import Optional
from vida.utils.github_client import get_github_client
from github import Github #type: ignore


def git_dispatch_workflow(repo_full_name, workflow_name,  ref, inputs: Optional[dict] = None,g:Github=None):
    g = g if g else get_github_client()
    repo = g.get_repo(repo_full_name)
    workflow = repo.get_workflow(workflow_name)
    return workflow.create_dispatch( ref=ref, inputs=inputs)