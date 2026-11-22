from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductionLineBase(BaseModel):
    name: str
    factory_zone: Optional[str] = None
    description: Optional[str] = None


class ProductionLineCreate(ProductionLineBase):
    pass


class ProductionLineUpdate(BaseModel):
    name: Optional[str] = None
    factory_zone: Optional[str] = None
    description: Optional[str] = None


class ProductionLineResponse(ProductionLineBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

