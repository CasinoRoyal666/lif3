import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import day_actions, day_events
from app.models.enums import Satisfaction, string_enum
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.event import Event


class Day(TimestampMixin, Base):
    __tablename__ = "days"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(unique=True)
    satisfaction: Mapped[Satisfaction] = mapped_column(
        string_enum(Satisfaction, "satisfaction")
    )
    reflection: Mapped[str | None] = mapped_column(Text)

    # order_by — чтобы порядок в ответе API был стабильным
    actions: Mapped[list["Action"]] = relationship(
        secondary=day_actions, back_populates="days", order_by="Action.name"
    )
    events: Mapped[list["Event"]] = relationship(
        secondary=day_events, back_populates="days", order_by="Event.name"
    )
