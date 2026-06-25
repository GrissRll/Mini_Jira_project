from .base import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)

    tasks: Mapped[List['Task']] = relationship("Task", back_populates="worker")
    projects: Mapped[List['Project']] = relationship("Project", back_populates="members")
