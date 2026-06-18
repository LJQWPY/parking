from pydantic import BaseModel
from typing import Optional


class CameraBase(BaseModel):
    name: str
    ip_address: str
    location: Optional[str] = None
    status: str = "offline"
    zone_id: Optional[int] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    zone_id: Optional[int] = None


class CameraResponse(CameraBase):
    id: int

    class Config:
        from_attributes = True
