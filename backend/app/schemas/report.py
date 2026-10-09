import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReportKind


class ReportCreate(BaseModel):
    """Тело POST /reports.

    `date` — любая дата внутри нужного периода. Границы недели (пн-вс) или месяца
    сервер вычисляет сам, поэтому создать отчёт с «кривым» периодом нельзя.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    kind: ReportKind
    date: dt.date
    text: str = Field(min_length=1)


class ReportUpdate(BaseModel):
    """Тело PATCH /reports/{kind}/{date}. Менять можно только текст, период фиксирован."""

    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=1)


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: ReportKind
    period_start: dt.date
    period_end: dt.date
    text: str
    created_at: dt.datetime
    updated_at: dt.datetime
