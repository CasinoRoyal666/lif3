from fastapi import FastAPI

from app.api.routers import actions, days, events, reports

app = FastAPI(title="lif3 API")

app.include_router(actions.router)
app.include_router(events.router)
app.include_router(days.router)
app.include_router(reports.router)
