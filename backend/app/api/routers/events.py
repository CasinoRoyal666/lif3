from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import DbSession
from app.models import Effect, Event
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


def get_event_or_404(db: DbSession, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


@router.get("", response_model=list[EventRead])
def list_events(db: DbSession, effect: Effect | None = None):
    """Список событий; `?effect=positive` — фильтр по эффекту."""
    stmt = select(Event).order_by(Event.name)
    if effect is not None:
        stmt = stmt.where(Event.effect == effect)
    return db.scalars(stmt).all()


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: DbSession):
    return get_event_or_404(db, event_id)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: DbSession):
    event = Event(**payload.model_dump())
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Event with this name already exists")
    db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: DbSession):
    event = get_event_or_404(db, event_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Event with this name already exists")
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: DbSession):
    event = get_event_or_404(db, event_id)
    db.delete(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Event is used in days and cannot be deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
