from pydantic import BaseModel
from typing import Optional, Any


class AlertBase(BaseModel):
    camera_id: int
    zone_id: Optional[int] = None
    alert_type: str
    level: str
    image_url: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    is_handled: bool
    handled_by: Optional[int] = None


class AlertResponse(AlertBase):
    id: int
    is_handled: bool
    handled_by: Optional[int] = None

    class Config:
        from_attributes = True
