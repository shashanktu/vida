# from utils.config import hari_github_token as github_token
from dotenv import load_dotenv
load_dotenv()
from vida.utils.config import hari_github_token as github_token
from github import Github, Auth #type: ignore
from vida.utils.request_context import github_pat_ctx



def get_github_client(git_token=None):
    
    git_token = git_token or github_pat_ctx.get(None) or github_token
    print(git_token)
    auth = Auth.Token(git_token)
    return Github(auth=auth)