import datetime as dt

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession
from app.models import Action, Day, Event, Satisfaction
from app.schemas.day import DayCreate, DayRead, DayUpdate

router = APIRouter(prefix="/days", tags=["days"])


def _day_query():
    # selectinload: действия и события всех дней подгружаются двумя дополнительными
    # запросами, а не отдельным запросом на каждый день (проблема N+1).
    return select(Day).options(selectinload(Day.actions), selectinload(Day.events))


def get_day_or_404(db: DbSession, day_date: dt.date) -> Day:
    # populate_existing: после commit возвращаем свежие данные, а не кэш сессии
    stmt = _day_query().where(Day.date == day_date).execution_options(populate_existing=True)
    day = db.scalars(stmt).one_or_none()
    if day is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Day not found")
    return day


def _load_by_ids(db: DbSession, model: type[Action] | type[Event], ids: list[int]) -> list:
    """Находит объекты справочника по id; если какого-то нет — 422."""
    if not ids:
        return []
    items = list(db.scalars(select(model).where(model.id.in_(ids))))
    missing = set(ids) - {item.id for item in items}
    if missing:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Unknown {model.__tablename__} ids: {sorted(missing)}",
        )
    return items


@router.get("", response_model=list[DayRead])
def list_days(
    db: DbSession,
    date_from: dt.date | None = Query(default=None, alias="from"),
    date_to: dt.date | None = Query(default=None, alias="to"),
    satisfaction: Satisfaction | None = None,
):
    """Дни от новых к старым. `?from=2026-01-01&to=2026-01-31&satisfaction=bad` — фильтры."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "'from' must not be after 'to'")
    stmt = _day_query().order_by(Day.date.desc())
    if date_from is not None:
        stmt = stmt.where(Day.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Day.date <= date_to)
    if satisfaction is not None:
        stmt = stmt.where(Day.satisfaction == satisfaction)
    return db.scalars(stmt).all()


@router.get("/{day_date}", response_model=DayRead)
def get_day(day_date: dt.date, db: DbSession):
    return get_day_or_404(db, day_date)


@router.post("", response_model=DayRead, status_code=status.HTTP_201_CREATED)
def create_day(payload: DayCreate, db: DbSession):
    day = Day(
        date=payload.date,
        satisfaction=payload.satisfaction,
        reflection=payload.reflection,
        actions=_load_by_ids(db, Action, payload.action_ids),
        events=_load_by_ids(db, Event, payload.event_ids),
    )
    db.add(day)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Day for this date already exists")
    return get_day_or_404(db, payload.date)


@router.patch("/{day_date}", response_model=DayRead)
def update_day(day_date: dt.date, payload: DayUpdate, db: DbSession):
    day = get_day_or_404(db, day_date)
    data = payload.model_dump(exclude_unset=True)

    links_changed = False
    if (action_ids := data.pop("action_ids", None)) is not None:
        day.actions = _load_by_ids(db, Action, action_ids)
        links_changed = True
    if (event_ids := data.pop("event_ids", None)) is not None:
        day.events = _load_by_ids(db, Event, event_ids)
        links_changed = True
    for field, value in data.items():
        setattr(day, field, value)
    if links_changed:
        # смена только связей не трогает строку days, поэтому updated_at обновляем сами
        day.updated_at = func.now()

    db.commit()
    return get_day_or_404(db, day_date)


@router.delete("/{day_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(day_date: dt.date, db: DbSession):
    day = get_day_or_404(db, day_date)
    db.delete(day)  # связи в day_actions / day_events удаляются каскадом
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
