from .base import Base
from sqlalchemy import Integer, String, Boolean, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tasks: Mapped[List['Task']] = relationship("Task", back_populates="worker")
    projects: Mapped[List['Project']] = relationship("Project", back_populates="members")
