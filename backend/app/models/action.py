from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import day_actions
from app.models.enums import Effect, string_enum
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.day import Day


class Action(TimestampMixin, Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    effect: Mapped[Effect] = mapped_column(string_enum(Effect, "effect"))
    description: Mapped[str | None] = mapped_column(Text)

    days: Mapped[list["Day"]] = relationship(
        secondary=day_actions, back_populates="actions", passive_deletes="all"
    )
