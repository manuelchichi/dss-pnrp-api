import os
import numpy as np
import asyncio
from aiostream import stream

from fastapi import FastAPI, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List
import motor.motor_asyncio

app = FastAPI(title="DSS_PNRP_API",
              version="0.0.1")

db_client: motor.motor_asyncio.AsyncIOMotorClient = None

async def get_db_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    """Return database client instance."""
    return db_client

async def connect_db():
    """Create database connection."""
    global db_client
    db_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])

async def close_db():
    """Close database connection."""
    db_client.close()

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Models used for "execution"
class CriteriaRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    criteria_id: int = Field(...)
    value: float = Field(...)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "criteria_id": 1 ,
                "value": 15.3
            }
        }

class CriteriaCreateModel(BaseModel):
    criteria_id: int = Field(...)
    value: float = Field(...)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "criteria_id": 1 ,
                "value": 15.3
            }
        }

class IssueRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    issue_id: int = Field(...)
    eval: List[CriteriaRetrieveModel] = []
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "issue_id": 5,
                "eval": 15
            }
        }

class IssueCreateModel(BaseModel):
    issue_id: int = Field(...)
    eval: List[CriteriaCreateModel] = []
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "issue_id": 5,
                "eval": 15
            }
        }
class PPExecutionCreateModel(BaseModel):
    prioritization_process_id: int = Field(...)
    pp_execution_id: int = Field(...)
    criterias: List[CriteriaCreateModel] = []
    issues: List[IssueCreateModel] = []
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Time",
                "value": 15
            }
        }

class PPExecutionRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    prioritization_process_id: int = Field(...)
    pp_execution_id: int = Field(...)
    criterias: List[CriteriaRetrieveModel] = []
    issues: List[IssueRetrieveModel] = []
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Time",
                "value": 15
            }
        }


@app.get("/health")
def health():
    return {"status": "OK"}


def construct_comparison_matrix(criterion, issues):
    # function to make pairwise comparisons from utility function - 100 is maximum utility
    comparison_mu = lambda x, y: 1. if x >= y else 1. + (x - y) / 100

    # Comparison matrix
    comparison_matrix = np.array(
        [[comparison_mu(criteria_i["value"], criteria_j["value"])
            for issue_j in issues
                for criteria_j in issue_j["eval"]
                    if criteria_j["criteria_id"] == criterion]
                        for issue_i in issues
                            for criteria_i in issue_i["eval"]
                                if criteria_i["criteria_id"] == criterion])

    return comparison_matrix


def ponderate(matrix, weight):
    # return np.maximum(matrix, 1 - weight)
    return matrix ** weight


def build_solution(order, issues):
    initial_position = 1
    actual_position = initial_position
    solution = []
    for position_list in order:
        solution.extend(
            [{"issue_id": issues[position]["issue_id"], "position": actual_position} for position in position_list])
        actual_position += len(position_list)
    return solution


# Data processing background task
async def solve_execution(execution_dict):
    criterias = execution_dict["criterias"]
    issues = execution_dict["issues"]
    
    criterias_values = [c["value"] for c in criterias if "value" in c]
    # check criteria maps to numeric
    # check every issue has all required evaluations and are numeric

    # normalize criteria weights
    max_weight = max(criterias_values)
    normalized_criteria = {c["criteria_id"]: (c["value"] / max_weight) for c in criterias}

    indexes = np.array([i for i, _ in enumerate(issues)])
    global_comparison_matrix = []
    order = []

    for criterion in normalized_criteria:
        # Comparison matrix
        comparison_matrix = construct_comparison_matrix(criterion, issues)
        # Ponderate according to dimension
        comparison_matrix = ponderate(comparison_matrix, normalized_criteria[criterion])

        # Global comparison matrix (T-norm min)
        if len(global_comparison_matrix) == 0:
            global_comparison_matrix = comparison_matrix
        else:
            global_comparison_matrix = np.minimum(global_comparison_matrix, comparison_matrix)

    # Strict relation
    strict_relation = global_comparison_matrix - global_comparison_matrix.T
    strict_relation[strict_relation < 0] = 0

    # Non dominance vector
    while len(indexes) > 0:
        non_dominance_vector = 1 - np.amax(strict_relation, 0)
        non_dominated = np.where(non_dominance_vector == max(non_dominance_vector))
        # get non dominated requirements
        order.append(list(indexes[non_dominated]))
        # remove non_dominated from matrix and indexes
        indexes = np.delete(indexes, non_dominated)
        strict_relation = np.delete(np.delete(strict_relation, non_dominated, 0), non_dominated, 1)

    # Building solution with the obtained order
    new_execution = {
        "prioritization_process_id": execution_dict["prioritization_process_id"],
        "pp_execution_id": execution_dict["pp_execution_id"],
        "solution": build_solution(order, issues)
    }
    # Update execution with the obtained solution
    await db_client["api"]["executions"].update_one({"pp_execution_id": new_execution["pp_execution_id"]}, {"$set": new_execution})


@app.post("/execution")
async def create_execution(execution: PPExecutionCreateModel, background_tasks: BackgroundTasks):
    execution = jsonable_encoder(execution)

    ####Validating input
    # Saving instead of calculating it multiple times
    criterias_len = len(execution["criterias"])
    for issue in execution["issues"]:
        if len(issue["eval"]) == criterias_len:
            # Cardinality matched, checking if all keys match as well
            for criteria in execution["criterias"]:
               if not (criteria['criteria_id'] in [criteria_issue["criteria_id"]
                   for criteria_issue in issue["eval"]]):
                   # A key is missing
                   return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=execution)
        else:
            # Cardinality of criteria and eval didn't match
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=execution)
    # JSON validated; Solving execution on background task
    background_tasks.add_task(solve_execution, execution)
    # Inserting with an empty solution in db
    new_execution = {
        "prioritization_process_id": execution["prioritization_process_id"],
        "pp_execution_id": execution["pp_execution_id"],
        "solution": []
    }
    inserted_execution = await db_client["api"]["executions"].insert_one(new_execution)
    created_execution = await db_client["api"]["executions"].find_one({"id": inserted_execution.inserted_id})
    return JSONResponse(status_code=status.HTTP_200_OK, content=created_execution)


@app.get('/execution/{pp_execution_id}')
async def execution(pp_execution_id: int):
    execution = await db_client["api"]["executions"].find_one({"pp_execution_id": pp_execution_id},{'_id': 0})
    if execution is not None:
        json_compatible_execution_data = jsonable_encoder(execution)
        return JSONResponse(content=json_compatible_execution_data)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

@app.get('/executions/{prioritization_process_id}')
async def executions(prioritization_process_id: int):
    executions = await db_client["api"]["executions"].find_one({"prioritization_process_id": prioritization_process_id},{'_id': 0})
    if executions is not None:
        json_compatible_execution_data = jsonable_encoder(executions)
        return JSONResponse(content=json_compatible_execution_data)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.delete('/execution/{pp_execution_id}')
async def clean_execution(pp_execution_id: int):
    delete_result = await db_client["api"]["executions"].delete_one({"pp_execution_id": pp_execution_id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Execution {pp_execution_id} not found")


@app.delete('/executions/{prioritization_process_id}')
async def clean_executions(prioritization_process_id: int):
    delete_result = await db_client["api"]["executions"].delete({"prioritization_process_id": prioritization_process_id})
    if delete_result.deleted_count != 0:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Executions from process {prioritization_process_id} not found")


@app.get('/algorithms/pp')
def algorithmspp():
    data = {
        "algorithms":
            []
    }
    json_compatible_algorithm_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_algorithm_data)

@app.get('/algorithms/nrp')
def algorithmsnrp():
    data = {
        "algorithms":
            [
                {
                    "id": 1,
                    "name": "NSGA-II",
                    "version": "1.0",
                    "parameters":
                        [
                            {"id": 1,
                             "name": "Poblacion",
                             "defaultValue": 100},
                            {"id": 2,
                             "name": "Generaciones",
                             "defaultValue": 50},
                            {"id": 3,
                             "name": "Probabilidad de mutacion",
                             "defaultValue": 0.2},
                            {"id": 4,
                             "name": "Ratio de Cruce",
                             "defaultValue": 0.8}
                        ]
                },
                {
                    "id": 2,
                    "name": "MOPSO",
                    "version": "1.0",
                    "parameters":
                        [
                            {"id": 1,
                             "name": "Poblacion",
                             "defaultValue": 100},
                            {"id": 2,
                             "name": "Generaciones",
                             "defaultValue": 70},
                            {"id": 3,
                             "name": "Probabilidad de mutacion",
                             "defaultValue": 0.4},
                            {"id": 4,
                             "name": "Ratio de Cruce",
                             "defaultValue": 0.8},
                            {"id": 5,
                             "name": "Ratio de deterioro",
                             "defaultValue": 2}
                        ]
                }
            ]
    }
    json_compatible_algorithm_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_algorithm_data)


# Obtain unfinished executions
async def retrieve_executions():
    executions = []
    execution_collection = db_client["api"].get_collection("executions")
    cursor = execution_collection.find()
    async for execution in cursor:
        if len(execution["solution"]) == 0:
            executions.append(execution)
    return executions


# On startup solve all unfinished executions
@app.on_event("startup")
async def startup_event():
    pending_executions = await retrieve_executions()
    for execution in pending_executions:
        solve_execution(execution)
