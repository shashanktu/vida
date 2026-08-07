from .tables.config_details import ConfigDetails
from .tables.Agents import Agents, AgentMetrics, AgentTaskDetails, AgentRunLogs
from .tables.workflows import Workflow, WorkflowDetails
from .tables.app_configs import AgentDetails, GithubDetails, OtherDetails

from database.database import Base


