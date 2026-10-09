from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

day_actions = Table(
    "day_actions",
    Base.metadata,
    Column("day_id", ForeignKey("days.id", ondelete="CASCADE"), primary_key=True),
    Column("action_id", ForeignKey("actions.id", ondelete="RESTRICT"), primary_key=True),
)

day_events = Table(
    "day_events",
    Base.metadata,
    Column("day_id", ForeignKey("days.id", ondelete="CASCADE"), primary_key=True),
    Column("event_id", ForeignKey("events.id", ondelete="RESTRICT"), primary_key=True),
)
