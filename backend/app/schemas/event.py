import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import Effect


class EventBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    effect: Effect
    description: str | None = None


class EventCreate(EventBase):
    """Тело POST /events."""


class EventUpdate(BaseModel):
    """Тело PATCH /events/{id}: все поля необязательны, меняются только присланные."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    effect: Effect | None = None
    description: str | None = None

    @model_validator(mode="after")
    def _required_fields_not_null(self):
        for field in ("name", "effect"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: dt.datetime
    updated_at: dt.datetime
