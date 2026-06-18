from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.utils.response import success_response
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/", response_model=List[CameraResponse])
def list_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cameras = db.query(Camera).all()
    return success_response([CameraResponse.model_validate(c).model_dump() for c in cameras])


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return success_response(CameraResponse.model_validate(camera).model_dump())


@router.post("/", response_model=CameraResponse)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return success_response(CameraResponse.model_validate(db_camera).model_dump(), "Camera created successfully")


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    for key, value in camera.model_dump(exclude_unset=True).items():
        setattr(db_camera, key, value)
    db.commit()
    db.refresh(db_camera)
    return success_response(CameraResponse.model_validate(db_camera).model_dump(), "Camera updated successfully")


@router.delete("/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(db_camera)
    db.commit()
    return success_response(None, "Camera deleted successfully")
