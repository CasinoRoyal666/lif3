from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

# Короткий алиас: `db: DbSession` в сигнатуре эндпойнта равносильно
# `db: Session = Depends(get_db)` — FastAPI сам создаёт сессию и закрывает её после ответа.
DbSession = Annotated[Session, Depends(get_db)]
