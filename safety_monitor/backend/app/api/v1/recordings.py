from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.api.v1.deps import get_db, get_current_user
from app.models import Recording, Camera
from app.schemas import RecordingCreate, RecordingUpdate, RecordingResponse, RecordingListResponse
from app.models.user import User

router = APIRouter(prefix="/recordings", tags=["录像管理"])


def recording_to_response(recording: Recording, camera_name: str = None) -> dict:
    return {
        "id": recording.id,
        "camera_id": recording.camera_id,
        "camera_name": camera_name,
        "file_path": recording.file_path,
        "start_time": recording.start_time,
        "end_time": recording.end_time,
        "duration": recording.duration,
        "file_size": recording.file_size,
        "status": recording.status,
        "created_at": recording.created_at
    }


@router.get("", response_model=List[RecordingListResponse])
def list_recordings(
    camera_id: Optional[int] = Query(None, description="摄像头ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    status: Optional[str] = Query(None, description="状态"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取录像列表"""
    query = db.query(Recording).join(Camera)

    if camera_id:
        query = query.filter(Recording.camera_id == camera_id)
    if start_date:
        query = query.filter(Recording.start_time >= start_date)
    if end_date:
        query = query.filter(Recording.start_time <= end_date)
    if status:
        query = query.filter(Recording.status == status)

    recordings = query.order_by(desc(Recording.created_at)).offset(skip).limit(limit).all()

    result = []
    for r in recordings:
        camera_name = r.camera.name if r.camera else None
        result.append(recording_to_response(r, camera_name))

    return result


@router.get("/{recording_id}", response_model=RecordingListResponse)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取录像详情"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="录像不存在")

    camera_name = recording.camera.name if recording.camera else None
    return recording_to_response(recording, camera_name)


@router.post("", response_model=RecordingResponse)
def create_recording(
    recording: RecordingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建录像记录"""
    db_recording = Recording(**recording.model_dump())
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


@router.put("/{recording_id}", response_model=RecordingResponse)
def update_recording(
    recording_id: int,
    recording_update: RecordingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新录像记录"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="录像不存在")

    for key, value in recording_update.model_dump(exclude_unset=True).items():
        setattr(recording, key, value)

    db.commit()
    db.refresh(recording)
    return recording


@router.delete("/{recording_id}")
def delete_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除录像记录"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="录像不存在")

    db.delete(recording)
    db.commit()
    return {"message": "删除成功"}


@router.get("/cameras/{camera_id}/recordings")
def get_camera_recordings(
    camera_id: int,
    date: Optional[str] = Query(None, description="日期，格式YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定摄像头的录像列表"""
    query = db.query(Recording).filter(Recording.camera_id == camera_id)

    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            next_date = datetime.strptime(date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Recording.start_time >= target_date, Recording.start_time <= next_date)
        except ValueError:
            pass

    recordings = query.order_by(desc(Recording.start_time)).all()

    result = []
    for r in recordings:
        camera_name = r.camera.name if r.camera else None
        result.append(recording_to_response(r, camera_name))

    return result
