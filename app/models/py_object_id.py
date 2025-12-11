from bson import ObjectId
from typing import Any, Callable
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

class PyObjectId(ObjectId):

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: Any, handler: Callable[[Any], JsonSchemaValue]
    ) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.update(type="string")  # representación JSON
        return schema
