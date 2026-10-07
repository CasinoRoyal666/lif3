from fastapi import FastAPI

from app.api.routers import actions, events

app = FastAPI(title="lif3 API")

app.include_router(actions.router)
app.include_router(events.router)
