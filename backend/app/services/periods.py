import calendar
import datetime as dt

from app.models.enums import ReportKind


def period_bounds(kind: ReportKind, anchor: dt.date) -> tuple[dt.date, dt.date]:
    """Границы (начало, конец) периода, в который попадает дата `anchor`; обе включительно.

    Неделя — по ISO: с понедельника по воскресенье. Месяц — календарный.
    """
    if kind is ReportKind.WEEK:
        start = anchor - dt.timedelta(days=anchor.weekday())
        return start, start + dt.timedelta(days=6)
    start = anchor.replace(day=1)
    last_day = calendar.monthrange(anchor.year, anchor.month)[1]
    return start, anchor.replace(day=last_day)
