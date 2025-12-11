from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List
from .py_object_id import PyObjectId
from .criteria import CriteriaCreateModel, CriteriaRetrieveModel

class IssueRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    issue_id: int
    eval: List[CriteriaRetrieveModel] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "issue_id": 5,
                "eval": 15
            }
        }
    }

class IssueCreateModel(BaseModel):
    issue_id: int
    eval: List[CriteriaCreateModel] = Field(default_factory=list)
