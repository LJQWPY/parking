from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.utils.response import success_response, error_response
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.core.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/")
def list_alerts(
    camera_id: int = None,
    level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    
    if camera_id is not None:
        query = query.filter(Alert.camera_id == camera_id)
    
    if level is not None:
        query = query.filter(Alert.level == level)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return success_response([AlertResponse.model_validate(a).model_dump() for a in alerts])


@router.get("/stats")
def get_alert_stats(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats = alert_service.get_alert_stats(db, hours)
    return success_response(stats)


@router.get("/unhandled")
def get_unhandled_alerts(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = alert_service.get_unhandled_alerts(db, limit)
    return success_response([AlertResponse.model_validate(a).model_dump() for a in alerts])


@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return error_response(404, "Alert not found")
    return success_response(AlertResponse.model_validate(alert).model_dump())


@router.post("/")
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return success_response(AlertResponse.model_validate(db_alert).model_dump(), "Alert created successfully")


@router.put("/{alert_id}")
def update_alert(
    alert_id: int,
    alert: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        return error_response(404, "Alert not found")
    for key, value in alert.model_dump(exclude_unset=True).items():
        setattr(db_alert, key, value)
    db.commit()
    db.refresh(db_alert)
    return success_response(AlertResponse.model_validate(db_alert).model_dump(), "Alert updated successfully")


@router.put("/{alert_id}/handle")
def handle_alert(
    alert_id: int,
    handled_by: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if alert_service.handle_alert(db, alert_id, handled_by):
        return success_response(None, "Alert handled successfully")
    return error_response(404, "Alert not found")