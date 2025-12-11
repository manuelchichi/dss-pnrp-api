from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List
from .py_object_id import PyObjectId

class CriteriaRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    criteria_id: int
    value: float

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "criteria_id": 1,
                "value": 15.3
            }
        }
    }

class CriteriaCreateModel(BaseModel):
    criteria_id: int
    value: float
