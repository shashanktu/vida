from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, ForeignKey
from typing import Optional, Literal

from database.database import Base

class Agents(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    wrapper_prompt_path: Mapped[str] = mapped_column (Text, nullable=True)
    required_fields : Mapped[dict] = mapped_column(JSON, nullable = True)

    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    metrics: Mapped["AgentMetrics"] = relationship("AgentMetrics", uselist=False, back_populates="agent", cascade="all, delete-orphan")

class AgentMetrics(Base):
    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), unique=True, nullable=False)
    total_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_success_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_fail_runs : Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    agent_status: Mapped[Literal["active", "idle"]] = mapped_column(String(20), nullable=False, default="idle")

    agent: Mapped["Agents"] = relationship("Agents", back_populates="metrics")

class AgentTaskDetails(Base):
    __tablename__ = "agent_task_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    branch_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agent_id: Mapped[int] = mapped_column(Integer,ForeignKey("agents.id"),index=True, nullable=False)
    task_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    task_status: Mapped[Literal["pending", "running", "success", "failed"]] = mapped_column(String(20),nullable=False, default="pending")
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    runs: Mapped[list["AgentRunLogs"]] = relationship(
        "AgentRunLogs",
        cascade="all, delete-orphan",
        back_populates="task"
    )

class AgentRunLogs(Base):
    __tablename__ = "agent_run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer,ForeignKey("agents.id"),index=True, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer,ForeignKey("agent_task_details.id"),index=True, nullable=False)
    run_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_logs_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    run_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    issue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    run_status: Mapped[Literal["pending", "running", "success", "failed"]] = mapped_column(String(20), nullable=False, default="pending")
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    task: Mapped["AgentTaskDetails"] = relationship(
        "AgentTaskDetails",
        back_populates="runs"
    )

