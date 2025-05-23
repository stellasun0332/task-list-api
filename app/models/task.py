from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import Optional


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]]
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            description=data["description"],
        )

    def to_dict(self, include_goal_id=False):
        task_dict = dict(
            id=self.id,
            title=self.title,
            description=self.description,
            is_complete=self.completed_at is not None,
        )
        if include_goal_id:
            task_dict["goal_id"] = self.goal_id

        return task_dict

    def update_from_dict(self, data):
        self.title = data["title"]
        self.description = data["description"]
