from contextvars import ContextVar

github_pat_ctx: ContextVar[str] = ContextVar("github_pat")
task_id_ctx: ContextVar[int] = ContextVar("task_id")