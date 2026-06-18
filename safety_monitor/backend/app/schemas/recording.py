from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecordingBase(BaseModel):
    camera_id: int
    file_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    status: str = "recording"


class RecordingCreate(RecordingBase):
    pass


class RecordingUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    status: Optional[str] = None


class RecordingResponse(RecordingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecordingListResponse(BaseModel):
    id: int
    camera_id: int
    camera_name: Optional[str] = None
    file_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
