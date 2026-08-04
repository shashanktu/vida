from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from typing import Optional

from database.database import Base

class Agents(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    wrapper_prompt_path: Mapped[str] = mapped_column (Text, nullable=True)
    required_fields : Mapped[dict] = mapped_column(JSON, nullable = True)
    total_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_success_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_fail_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class AgentTaskDetails(Base):
    __tablename__ = "agent_task_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    branch_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_prompt: Mapped[str] = mapped_column(Text, nullable=True)   
    agents_called: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    task_logs_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    task_result : Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    task_status: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class AgentRunLogs(Base):
    __tablename__ = "agent_run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, nullable=False)
    run_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_logs_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    run_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    run_status: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
