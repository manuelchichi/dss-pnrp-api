import os
import numpy as np

from fastapi import FastAPI, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client


# Models used for "execution"
class CriteriaModel(BaseModel):
    name: str
    value: float


class IssueModel(BaseModel):
    id: int
    eval: [CriteriaModel]


class ExecutionModel(BaseModel):
    prp_process_id: int
    prp_execution_id: int
    criteria: [CriteriaModel]
    issues: [IssueModel]


@app.get("/health")
def health():
    return {"status": "OK"}


def construct_comparison_matrix(criterion, issues):
    # function to make pairwise comparisons from utility function - 100 is maximum utility
    comparison_mu = lambda x, y: 1. if x >= y else 1. + (x - y) / 100

    # Comparison matrix
    comparison_matrix = np.array(
        [[comparison_mu(issue_i["eval"][criterion], issue_j["eval"][criterion]) for j, issue_j in enumerate(issues)] for
         i, issue_i in enumerate(issues)])

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
            [{"issue_id": issues[position]["id"], "position": actual_position} for position in position_list])
        actual_position += len(position_list)
    return solution


# Data processing background task
def solve_execution(execution_dict):
    criteria = execution_dict["criteria"]
    issues = execution_dict["issues"]

    # check criteria maps to numeric

    # check every issue has all required evaluations and are numeric

    # normalize criteria weights
    max_weight = max(criteria.values())
    normalized_criteria = {name: (weight / max_weight) for name, weight in criteria.items()}

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
        print(non_dominance_vector)
        non_dominated = np.where(non_dominance_vector == max(non_dominance_vector))
        # get non dominated requirements
        order.append(list(indexes[non_dominated]))
        # remove non_dominated from matrix and indexes
        indexes = np.delete(indexes, non_dominated)
        strict_relation = np.delete(np.delete(strict_relation, non_dominated, 0), non_dominated, 1)

    # Building solution with the obtained order
    solution = build_solution(order, issues)


## TO DO: Update execution with the obtained solution #


@app.post("/execution/")
async def create_execution(execution: ExecutionModel, background_tasks: BackgroundTasks):
    execution = jsonable_encoder(execution)

    ####Validating input
    # Saving instead of calculating it multiple times
    criteria_len = len(execution["criteria"])
    for issue in execution["issues"]:
        if len(issue["eval"]) == criteria_len:
            # Cardinality matched, checking if all keys match as well
            for criterion in execution["criteria"]:
                if not (criterion in issue["eval"]):
                    # A key is missing
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=execution)
        else:
            # Cardinality of criteria and eval didn't match
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=execution)
    # JSON validated; Solving execution on background task
    background_tasks.add_task(solve_execution, execution)
    ##TO DO: Insert execution with empty solution#
    # new_execution = await db["executions"].insert_one(solution)
    # created_execution = await db["executions"].find_one({"_id": new_execution.inserted_id})
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get('/execution/{prp_execution_id}')
def execution(prp_execution_id: int):
    data = {
        "id": 1,
        "prp_process_id": 1,
        "prp_execution_id": 1,
        "solution":
            [
                {
                    "issue_id": 1,
                    "position": 1
                },
                {
                    "issue_id": 2,
                    "position": 2
                },
                {
                    "issue_id": 3,
                    "position": 1
                },
                {
                    "issue_id": 4,
                    "position": 3
                },
                {
                    "issue_id": 5,
                    "position": 4
                }
            ]
    }
    json_compatible_execution_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_execution_data)


@app.get('/algorithms')
def algorithms():
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
