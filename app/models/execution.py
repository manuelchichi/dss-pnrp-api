from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List
from .py_object_id import PyObjectId
from .criteria import CriteriaCreateModel, CriteriaRetrieveModel
from .issue import IssueCreateModel, IssueRetrieveModel

class PPExecutionCreateModel(BaseModel):
    prioritization_process_id: int
    pp_execution_id: int
    criterias: List[CriteriaCreateModel] = Field(default_factory=list)
    issues: List[IssueCreateModel] = Field(default_factory=list)

class PPExecutionRetrieveModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    prioritization_process_id: int
    pp_execution_id: int
    criterias: List[CriteriaRetrieveModel] = Field(default_factory=list)
    issues: List[IssueRetrieveModel] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "name": "Time",
                "value": 15
            }
        }
    }
