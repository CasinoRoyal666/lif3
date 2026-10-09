import datetime as dt

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ReportKind, string_enum
from app.models.mixins import TimestampMixin


class PeriodReport(TimestampMixin, Base):
    """Недельный или месячный отчёт — саморефлексия за период."""

    __tablename__ = "period_reports"
    __table_args__ = (
        UniqueConstraint("kind", "period_start", name="uq_period_reports_kind_period_start"),
        CheckConstraint("period_end >= period_start", name="period_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[ReportKind] = mapped_column(string_enum(ReportKind, "report_kind"))
    period_start: Mapped[dt.date]
    period_end: Mapped[dt.date]
    text: Mapped[str] = mapped_column(Text)
