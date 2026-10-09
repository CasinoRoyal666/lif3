from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import DbSession
from app.models import Action, Effect
from app.schemas.action import ActionCreate, ActionRead, ActionUpdate

router = APIRouter(prefix="/actions", tags=["actions"])


def get_action_or_404(db: DbSession, action_id: int) -> Action:
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Action not found")
    return action


@router.get("", response_model=list[ActionRead])
def list_actions(db: DbSession, effect: Effect | None = None):
    """Список действий; `?effect=negative` — фильтр по эффекту."""
    stmt = select(Action).order_by(Action.name)
    if effect is not None:
        stmt = stmt.where(Action.effect == effect)
    return db.scalars(stmt).all()


@router.get("/{action_id}", response_model=ActionRead)
def get_action(action_id: int, db: DbSession):
    return get_action_or_404(db, action_id)


@router.post("", response_model=ActionRead, status_code=status.HTTP_201_CREATED)
def create_action(payload: ActionCreate, db: DbSession):
    action = Action(**payload.model_dump())
    db.add(action)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Action with this name already exists")
    db.refresh(action)
    return action


@router.patch("/{action_id}", response_model=ActionRead)
def update_action(action_id: int, payload: ActionUpdate, db: DbSession):
    action = get_action_or_404(db, action_id)
    # exclude_unset: только поля, которые клиент реально прислал
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Action with this name already exists")
    db.refresh(action)
    return action


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(action_id: int, db: DbSession):
    action = get_action_or_404(db, action_id)
    db.delete(action)
    try:
        db.commit()
    except IntegrityError:
        # FK ... ON DELETE RESTRICT: действие уже отмечено хотя бы в одном дне
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Action is used in days and cannot be deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
