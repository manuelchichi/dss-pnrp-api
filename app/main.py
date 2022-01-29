import os

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.college

class ExecutionModel(BaseModel):
    name: str
    price: float

@app.get("/health")
def health():
    return {"status": "OK"}

@app.post("/execution/")
async def create_execution(execution: ExecutionModel = Body(...)):
    execution = jsonable_encoder(execution)
    new_execution = await db["executions"].insert_one(executions)
    created_execution = await db["executions"].find_one({"_id": new_execution.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED,content=created_execution)

@app.get('/execution/{prp_execution_id}')
def execution(prp_execution_id: int):
    data = {
            "id":1,
            "prp_process_id":1,
            "prp_execution_id":1,
            "solution":
            [
                  {
                      "issue_id":1,
                      "position": 1
                  },
                  {
                      "issue_id":2,
                      "position": 2
                  },
                  {
                      "issue_id":3,
                      "position": 1
                  },
                  {
                      "issue_id":4,
                      "position": 3
                  },
                  {
                      "issue_id":5,
                      "position": 4
                  }
            ]
          }
    return jsonify(data)

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
    return jsonify(data)
