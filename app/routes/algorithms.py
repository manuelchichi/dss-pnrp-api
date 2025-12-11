from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/algorithms", tags=["algorithms"])

# ----------------------------------------------------
# GET /algorithms/pp
# ----------------------------------------------------
@router.get("/pp")
def get_algorithms_pp():
    data = {"algorithms": []}
    return JSONResponse(content=jsonable_encoder(data))


# ----------------------------------------------------
# GET /algorithms/nrp
# ----------------------------------------------------
@router.get("/nrp")
def get_algorithms_nrp():
    data = {
        "algorithms": [
            {
                "id": 1,
                "name": "NSGA-II",
                "version": "1.0",
                "parameters": [
                    {"id": 1, "name": "Poblacion", "defaultValue": 100},
                    {"id": 2, "name": "Generaciones", "defaultValue": 50},
                    {"id": 3, "name": "Probabilidad de mutacion", "defaultValue": 0.2},
                    {"id": 4, "name": "Ratio de Cruce", "defaultValue": 0.8},
                ],
            },
            {
                "id": 2,
                "name": "MOPSO",
                "version": "1.0",
                "parameters": [
                    {"id": 1, "name": "Poblacion", "defaultValue": 100},
                    {"id": 2, "name": "Generaciones", "defaultValue": 70},
                    {"id": 3, "name": "Probabilidad de mutacion", "defaultValue": 0.4},
                    {"id": 4, "name": "Ratio de Cruce", "defaultValue": 0.8},
                    {"id": 5, "name": "Ratio de deterioro", "defaultValue": 2},
                ],
            },
        ]
    }

    return JSONResponse(content=jsonable_encoder(data))
