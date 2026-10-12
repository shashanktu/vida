import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session, selectinload, joinedload
from vida.database.database import sessionlocal
from vida.models.tables.config_details import ConfigDetails
from vida.models.tables.Agents import Agents, AgentMetrics, AgentRunLogs, AgentTaskDetails
from vida.models.tables.workflows import Workflow, WorkflowDetails

from vida.models.requests.workflow_table_requests import workflow_table_requests, workflow_details_table_requests
from vida.models.requests.Agents_table_requests import AgentCreateRequest, AgentUpdateRequest
from vida.models.requests.Agent_Task_requests import AgentTaskDetailsCreateRequest, AgentTaskDetailsUpdateRequest
from vida.models.requests.Agent_Run_request import AgentRunCreateRequest, AgentRunUpdateRequest
from vida.models.requests.Agent_Metrics_requests import AgentMetricsCreateRequest, AgentMetricsUpdateRequest

from vida.models.responses.Agents_table_responses import AgentResponse
from vida.models.responses.config_details_response import ConfigDetailsRequest
from typing import Union


def get_all_triggered_records(db: Session) :
    result = db.query(ConfigDetails).all()
    if not result:
        return None
    return [item for item in result]


def get_triggered_record_by_id(db: Session, record_id: int) -> Union[ConfigDetails, None]:
    return db.query(ConfigDetails).filter(ConfigDetails.id == record_id).first()

class AgentsOps:
    def get_agents(self, db: Session):
        return db.query(Agents).all()

    def add_agent(self, db:Session, details:AgentCreateRequest) -> Agents:
        new_agent = Agents(**details.model_dump())
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return new_agent

    def update_agent(self, db:Session, agent_id:int, details:AgentUpdateRequest) -> Union[Agents, None]:
        agent = db.query(Agents).filter(Agents.id == agent_id).first()
        if not agent:
            return None
        for key, value in details.model_dump(exclude_unset=True).items():
            setattr(agent, key, value)
        db.commit()
        db.refresh(agent)
        return agent

    def get_agent_with_metrics(self, db: Session, agent_id: int):
        return (
            db.query(Agents)
            .options(joinedload(Agents.metrics))
            .filter(Agents.id == agent_id)
            .first()
        )

    def get_all_agents_with_metrics(self, db: Session):
        return (
            db.query(Agents)
            .options(joinedload(Agents.metrics))
            .all()
        )

class WorkflowOps:
    def get_workflows(self, db: Session):
        return (
            db.query(Workflow)
            .options(selectinload(Workflow.details))
            .all()
        )

    def push_workflow_record(self, db: Session, workflow: workflow_table_requests):
        details = Workflow(**workflow.model_dump())
        db.add(details)
        db.commit()
        db.refresh(details)
        return details

    def push_workflow_details_record(self, db: Session,workflow_details:workflow_details_table_requests):
        details = WorkflowDetails(**workflow_details.model_dump())
        db.add(details)
        db.commit()
        db.refresh(details)
        return details

class AgentTaskOps:
    def get_all_tasks(self, db: Session):
        return db.query(AgentTaskDetails).all()

    def get_agent_tasks_by_agent_id(self, db: Session, agent_id: int):
        return db.query(AgentTaskDetails).filter(AgentTaskDetails.agent_id == agent_id).all()

    def get_agent_tasks(self, db: Session, from_task_id: int, to_task_id: int):
        return db.query(AgentTaskDetails).filter(AgentTaskDetails.id.between(from_task_id, to_task_id)).all()

    def get_task_by_id(self, db: Session, task_id: int):
        return db.query(AgentTaskDetails).filter(AgentTaskDetails.id == task_id).first()

    def add_task(self, db: Session, task: AgentTaskDetailsCreateRequest) -> int:
        new_task = AgentTaskDetails(**task.model_dump())
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return int(new_task.id)

    def update_task(self, db: Session, task_id: int, task: AgentTaskDetailsUpdateRequest):
        existing_task = db.query(AgentTaskDetails).filter(AgentTaskDetails.id == task_id).first()
        if not existing_task:
            return None
        for key, value in task.model_dump(exclude_unset=True).items():
            setattr(existing_task, key, value)
        db.commit()
        db.refresh(existing_task)
        return existing_task

    def delete_task(self, db: Session, task_id: int):
        existing_task = db.query(AgentTaskDetails).filter(AgentTaskDetails.id == task_id).first()
        if not existing_task:
            return None
        db.delete(existing_task)
        db.commit()
        return existing_task

    def get_tasks_by_status(self, db: Session, status: str):
        return db.query(AgentTaskDetails).filter(AgentTaskDetails.task_status == status).all()

    def get_running_tasks(self, db: Session):
        return db.query(AgentTaskDetails).filter(AgentTaskDetails.task_status == "running").all()

    def get_failed_tasks(self, db: Session):
        return (
            db.query(AgentTaskDetails)
            .filter(AgentTaskDetails.task_status == "failed", AgentTaskDetails.issue.isnot(None))
            .all()
        )

    def get_tasks_paginated(self, db: Session, offset: int = 0, limit: int = 50):
        return db.query(AgentTaskDetails).order_by(AgentTaskDetails.start_time.desc()).offset(offset).limit(limit).all()

class AgentRunOps:
    def get_all_runs(self, db: Session):
        return db.query(AgentRunLogs).all()

    def get_run_by_id(self, db: Session, run_id: int):
        return db.query(AgentRunLogs).filter(AgentRunLogs.id == run_id).first()
    
    def get_runs(self, db: Session, from_run_id: int, to_run_id: int):
        return db.query(AgentRunLogs).filter(AgentRunLogs.id.between(from_run_id, to_run_id)).all()

    def get_run_by_task_id(self, db: Session, task_id: int):
        return db.query(AgentRunLogs).filter(AgentRunLogs.task_id == task_id).all()
    
    def get_run_by_agent_id(self, db: Session, agent_id: int):
        return db.query(AgentRunLogs).filter(AgentRunLogs.agent_id == agent_id).all()

    def add_run(self, db: Session, run: AgentRunCreateRequest):
        new_run = AgentRunLogs(**run.model_dump())
        db.add(new_run)
        db.commit()
        db.refresh(new_run)
        return new_run

    def delete_run(self, db: Session, run_id: int):
        existing_run = db.query(AgentRunLogs).filter(AgentRunLogs.id == run_id).first()
        if not existing_run:
            return None
        db.delete(existing_run)
        db.commit()
        return existing_run
    
    def update_run(self, db: Session, run_id: int, run: AgentRunUpdateRequest):
        existing_run = db.query(AgentRunLogs).filter(AgentRunLogs.id == run_id).first()
        if not existing_run:
            return None
        for key, value in run.model_dump(exclude_unset=True).items():
            setattr(existing_run, key, value)
        db.commit()
        db.refresh(existing_run)
        return existing_run

    def get_runs_by_status(self, db: Session, status: str):
        return db.query(AgentRunLogs).filter(AgentRunLogs.run_status == status).all()

    def get_running_runs(self, db: Session):
        return db.query(AgentRunLogs).filter(AgentRunLogs.run_status == "running").all()

    def get_failed_runs(self, db: Session):
        return (
            db.query(AgentRunLogs)
            .filter(AgentRunLogs.run_status == "failed", AgentRunLogs.issue.isnot(None))
            .all()
        )

    def get_recent_runs(self, db: Session, limit: int = 20):
        return (
            db.query(AgentRunLogs)
            .order_by(AgentRunLogs.start_time.desc())
            .limit(limit)
            .all()
        )

    def get_runs_paginated(self, db: Session, offset: int = 0, limit: int = 50):
        return db.query(AgentRunLogs).order_by(AgentRunLogs.start_time.desc()).offset(offset).limit(limit).all()

    def get_run_duration_stats(self, db: Session, agent_id: int):
        from sqlalchemy import func
        result = (
            db.query(
                func.avg(func.extract("epoch", AgentRunLogs.end_time - AgentRunLogs.start_time)).label("avg_duration_sec"),
                func.min(func.extract("epoch", AgentRunLogs.end_time - AgentRunLogs.start_time)).label("min_duration_sec"),
                func.max(func.extract("epoch", AgentRunLogs.end_time - AgentRunLogs.start_time)).label("max_duration_sec"),
            )
            .filter(AgentRunLogs.agent_id == agent_id, AgentRunLogs.end_time.isnot(None))
            .first()
        )
        return {"avg_duration_sec": result.avg_duration_sec, "min_duration_sec": result.min_duration_sec, "max_duration_sec": result.max_duration_sec}

class AgentMetricsOps:
    def get_all_metrics(self, db: Session):
         return (
            db.query(AgentMetrics)
            .options(joinedload(AgentMetrics.agent))
            .all()
        )
    
    def get_metrics_by_agent_id(self, db: Session, agent_id: int):
        return db.query(AgentMetrics).filter(AgentMetrics.agent_id == agent_id).first()

    def add_metrics(self, db: Session, details: AgentMetricsCreateRequest):
        new_metrics = AgentMetrics(**details.model_dump())
        db.add(new_metrics)
        db.commit()
        db.refresh(new_metrics)
        return new_metrics

    def update_metrics(self, db: Session, agent_id: int, details: AgentMetricsUpdateRequest):
        existing_metrics = db.query(AgentMetrics).filter(AgentMetrics.agent_id == agent_id).first()
        if not existing_metrics:
            return None
        for key, value in details.model_dump(exclude_unset=True).items():
            setattr(existing_metrics, key, value)
        db.commit()
        db.refresh(existing_metrics)
        return existing_metrics

    def delete_metrics(self, db: Session, agent_id: int):
        existing_metrics = db.query(AgentMetrics).filter(AgentMetrics.agent_id == agent_id).first()
        if not existing_metrics:
            return None
        db.delete(existing_metrics)
        db.commit()
        return existing_metrics
    

# ── additions to AgentTaskOps ─────────────────────────────────────────────────
    

# ── additions to AgentRunOps ──────────────────────────────────────────────────

# ── new class ─────────────────────────────────────────────────────────────────
class DashboardOps:
    def get_summary(self, db: Session):
        from sqlalchemy import func
        total_agents = db.query(func.count(Agents.id)).scalar()
        total_tasks = db.query(func.count(AgentTaskDetails.id)).scalar()
        total_runs = db.query(func.count(AgentRunLogs.id)).scalar()
        success_runs = db.query(func.count(AgentRunLogs.id)).filter(AgentRunLogs.run_status == "success").scalar()
        failed_runs = db.query(func.count(AgentRunLogs.id)).filter(AgentRunLogs.run_status == "failed").scalar()
        running_now = db.query(func.count(AgentRunLogs.id)).filter(AgentRunLogs.run_status == "running").scalar()
        return {
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failed_runs": failed_runs,
            "running_now": running_now,
            "success_rate": round((success_runs / total_runs) * 100, 2) if total_runs else 0.0,
        }

    def get_agent_task_status_breakdown(self, db: Session):
        from sqlalchemy import func
        rows = (
            db.query(
                AgentTaskDetails.agent_id,
                AgentTaskDetails.task_status,
                func.count(AgentTaskDetails.id).label("count")
            )
            .group_by(AgentTaskDetails.agent_id, AgentTaskDetails.task_status)
            .all()
        )
        breakdown: dict = {}
        for agent_id, status, count in rows:
            breakdown.setdefault(agent_id, {})[status] = count
        return breakdown

    def get_agent_run_status_breakdown(self, db: Session):
        from sqlalchemy import func
        rows = (
            db.query(
                AgentRunLogs.agent_id,
                AgentRunLogs.run_status,
                func.count(AgentRunLogs.id).label("count")
            )
            .group_by(AgentRunLogs.agent_id, AgentRunLogs.run_status)
            .all()
        )
        breakdown: dict = {}
        for agent_id, status, count in rows:
            breakdown.setdefault(agent_id, {})[status] = count
        return breakdown


#Agent tasks calls


import asyncio

if __name__ == "__main__":
    pass