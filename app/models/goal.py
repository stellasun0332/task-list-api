from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from flask import abort, make_response
from typing import Optional


class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    def to_dict(self):
        return dict(id=self.id, title=self.title)

    @classmethod
    def from_dict(cls, data):
        return cls(title=data["title"])
