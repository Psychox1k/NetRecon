from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TargetBase(BaseModel):
    name: str


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    name: str | None = None

class TargetResponse(TargetBase):
    id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
