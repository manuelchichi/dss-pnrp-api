from fastapi import FastAPI
from app.db.connection import connect_db, close_db
from app.routes.health import router as health_router
from app.routes.execution import router as execution_router
from app.routes.algorithms import router as algorithms_router
from app.core.lifecycle import register_lifecycle_events

app = FastAPI(title="DSS_PNRP_API",
              version="0.0.1")

register_lifecycle_events(app)

app.include_router(health_router)
app.include_router(execution_router)
app.include_router(algorithms_router)
