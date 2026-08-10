from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from vida.database.database import Base

class AgentDetails(Base):
    __tablename__ = "agent_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    model: Mapped[str] = mapped_column(nullable=False)
    openai_url: Mapped[str] = mapped_column(nullable=False)
    azure_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    cognitive_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(nullable=True)
    version: Mapped[Optional[str]] = mapped_column(nullable=True)


class GithubDetails(Base):
    __tablename__ = "github_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    repository: Mapped[str] = mapped_column(nullable=True)
    branch: Mapped[str] = mapped_column(nullable=True)
    access_token: Mapped[str] = mapped_column(nullable=False)

class OtherDetails(Base):
    __tablename__ = "other_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    value : Mapped[str] = mapped_column(nullable=False)
