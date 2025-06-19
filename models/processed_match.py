from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Any
from bson import ObjectId
from datetime import datetime


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class ProcessedMatchModel(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    matchId: str
    processedAt: datetime = Field(default_factory=datetime.utcnow)
    createdAt: datetime | None = None   # populated by MongoDB if you use insert_one
    updatedAt: datetime | None = None   # populated by MongoDB if you use update operators

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 