from fastapi import FastAPI

from app.db.connection import connect_db, close_db, db_client
from app.db.executions import retrieve_executions
from app.algorithms.prioritization import solve_execution

def register_lifecycle_events(app: FastAPI):

    @app.on_event("startup")
    async def startup_event():
      await connect_db()
      # Solve unfinished executions
      pending_executions = await retrieve_executions()
      for execution in pending_executions:
          await solve_execution(execution)
    
    @app.on_event("shutdown")
    async def shutdown_event():
      await close_db()
