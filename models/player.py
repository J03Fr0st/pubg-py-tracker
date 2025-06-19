from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Any, Annotated
from bson import ObjectId
from datetime import datetime


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class PlayerModel(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    pubgId: str
    name: Optional[str] = None
    patchVersion: Optional[str] = None
    shardId: Optional[str] = None
    titleId: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    matches: Optional[List] = []

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    } 