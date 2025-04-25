# model.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Annotated
from datetime import datetime
from bson import ObjectId


# Updated PyObjectId class compatible with Pydantic v2
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: Any) -> None:
        schema.update(type="string")


# Create type annotation for ObjectId fields
PyObjectIdAnnotated = Annotated[str, PyObjectId]


class MovieBase(BaseModel):
    title: str
    director: str
    release_year: int
    watched: bool = False


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MovieInDB(MovieBase):
    id: PyObjectIdAnnotated = Field(
        default_factory=lambda: str(ObjectId()), alias="_id"
    )
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Updated from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MovieResponse(MovieBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode
