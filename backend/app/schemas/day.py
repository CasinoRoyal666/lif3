import datetime as dt
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    model_validator,
)

from app.models.enums import Satisfaction
from app.schemas.action import ActionRead
from app.schemas.event import EventRead


def _dedupe(ids: list[int]) -> list[int]:
    return list(dict.fromkeys(ids))


# Список id без дублей: [1, 2, 2] -> [1, 2]
IdList = Annotated[list[PositiveInt], AfterValidator(_dedupe)]


class DayCreate(BaseModel):
    """Тело POST /days. Действия и события передаются списками id из справочников."""

    date: dt.date
    satisfaction: Satisfaction
    reflection: str | None = None
    action_ids: IdList = Field(default_factory=list)
    event_ids: IdList = Field(default_factory=list)


class DayUpdate(BaseModel):
    """Тело PATCH /days/{date}. Меняются только присланные поля.

    Дату менять нельзя. Если прислан `action_ids` / `event_ids`, он ЗАМЕНЯЕТ весь
    набор целиком (а не дополняет его); `[]` снимает все отметки.
    """

    satisfaction: Satisfaction | None = None
    reflection: str | None = None
    action_ids: IdList | None = None
    event_ids: IdList | None = None

    @model_validator(mode="after")
    def _required_fields_not_null(self):
        # reflection можно обнулить, остальные поля — нет
        for field in ("satisfaction", "action_ids", "event_ids"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class DayRead(BaseModel):
    """Ответ API: день сразу с вложенными действиями и событиями."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt.date
    satisfaction: Satisfaction
    reflection: str | None
    actions: list[ActionRead]
    events: list[EventRead]
    created_at: dt.datetime
    updated_at: dt.datetime
