from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db.connection import get_db_client
from app.models.execution import PPExecutionCreateModel
from app.algorithms.prioritization import solve_execution

router = APIRouter(prefix="/execution", tags=["execution"])


# ----------------------------------------------------
# POST /execution — Create execution
# ----------------------------------------------------
@router.post("")
async def create_execution(
    execution: PPExecutionCreateModel,
    background_tasks: BackgroundTasks,
):

    client = await get_db_client()
    execution_data = jsonable_encoder(execution)

    # -----------------------------
    # Validation logic
    # -----------------------------
    criterias_len = len(execution_data["criterias"])

    for issue in execution_data["issues"]:
        if len(issue["eval"]) != criterias_len:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Criteria count mismatch", "data": execution_data}
            )

        issue_criteria_ids = {c["criteria_id"] for c in issue["eval"]}
        exec_criteria_ids = {c["criteria_id"] for c in execution_data["criterias"]}

        if issue_criteria_ids != exec_criteria_ids:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Missing criteria_id in issue eval", "data": execution_data}
            )

    # -----------------------------
    # Run solution in background
    # -----------------------------
    background_tasks.add_task(solve_execution, execution_data)

    # -----------------------------
    # Insert execution (solution empty)
    # -----------------------------
    new_execution = {
        "prioritization_process_id": execution_data["prioritization_process_id"],
        "pp_execution_id": execution_data["pp_execution_id"],
        "solution": []
    }

    result = await client["api"]["executions"].insert_one(new_execution)

    created = await client["api"]["executions"].find_one(
        {"_id": result.inserted_id},
        {"_id": 0}
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


# ----------------------------------------------------
# GET /execution/{pp_execution_id}
# ----------------------------------------------------
@router.get("/{pp_execution_id}")
async def get_execution(
    pp_execution_id: int,
):
    client = await get_db_client()
    
    execution = await client["api"]["executions"].find_one(
        {"pp_execution_id": pp_execution_id},
        {"_id": 0}
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return JSONResponse(content=jsonable_encoder(execution))


# ----------------------------------------------------
# GET /execution/process/{prioritization_process_id}
# ----------------------------------------------------
@router.get("/process/{prioritization_process_id}")
async def get_executions(
    prioritization_process_id: int,
):
    client = await get_db_client()
    executions = await client["api"]["executions"].find_one(
        {"prioritization_process_id": prioritization_process_id},
        {"_id": 0}
    )

    if not executions:
        raise HTTPException(status_code=404, detail="Executions not found")

    return JSONResponse(content=jsonable_encoder(executions))


# ----------------------------------------------------
# DELETE /execution/{pp_execution_id}
# ----------------------------------------------------
@router.delete("/{pp_execution_id}")
async def delete_execution(
    pp_execution_id: int,
):
    client = await get_db_client()
    result = await client["api"]["executions"].delete_one(
        {"pp_execution_id": pp_execution_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Execution not found")

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------
# DELETE /execution/process/{prioritization_process_id}
# ----------------------------------------------------
@router.delete("/process/{prioritization_process_id}")
async def delete_executions(
    prioritization_process_id: int,
):
    client = await get_db_client()
    result = await client["api"]["executions"].delete_many(
        {"prioritization_process_id": prioritization_process_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No executions found for process {prioritization_process_id}"
        )

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
