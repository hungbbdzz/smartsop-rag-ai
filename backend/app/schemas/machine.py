from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.machine import MachineStatus


class MachineBase(BaseModel):
    machine_code: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    status: MachineStatus = MachineStatus.OPERATIONAL
    line_id: str


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    status: Optional[MachineStatus] = None
    line_id: Optional[str] = None


class MachineResponse(MachineBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

