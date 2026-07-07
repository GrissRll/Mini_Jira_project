from .base import Base
from sqlalchemy import Integer, String, Boolean, DateTime, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(90), nullable=False)
    user_name: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    tasks: Mapped[List['Task']] = relationship("Task", back_populates="worker")
    projects: Mapped[List['Project']] = relationship("Project", back_populates="owner")

    __table_args__ = (
        UniqueConstraint("email", name="un_users_email"),
        UniqueConstraint("user_name", name="un_users_user_name")
    )
