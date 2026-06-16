import re
from typing import List, Set
 
def extract_github_secrets(yaml_content: str) -> List[str]:
    pattern = r'\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}'
 
    secrets: Set[str] = set(re.findall(pattern, yaml_content))
 
    return sorted(list(secrets))