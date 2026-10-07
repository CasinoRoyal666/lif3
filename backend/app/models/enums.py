import enum

from sqlalchemy import Enum


class Satisfaction(enum.StrEnum):
    GOOD = "good"
    NEUTRAL = "neutral"
    BAD = "bad"


class Effect(enum.StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ReportKind(enum.StrEnum):
    WEEK = "week"
    MONTH = "month"


def string_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    """Enum, хранимый как VARCHAR + CHECK (а не нативный тип Postgres).

    Так проще менять набор значений миграциями. В БД лежат value ("good"),
    а не имена членов ("GOOD").
    """
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=16,
        values_callable=lambda e: [m.value for m in e],
    )
