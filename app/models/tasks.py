from .base import Base
from sqlalchemy import (
    Boolean,
    Enum,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum as EnumClass


class TaskStatus(EnumClass):
    COMPLETED = "completed"
    WAITED = "waited"
    IN_WORK = "in_work"
    ON_PAUSE = "on_pause"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    worker_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.WAITED
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    worker: Mapped["User | None"] = relationship("User", back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("project_id", "title", name="un_tasks_project_title"),
    )
