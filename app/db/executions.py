from bson import ObjectId
from .connection import get_db_client

async def retrieve_executions():
    executions = []
    client = get_db_client()
    execution_collection = client["api"]["executions"]
    cursor = execution_collection.find()

    async for execution in cursor:
        if len(execution.get("solution", [])) == 0:
            executions.append(execution)

    return executions
