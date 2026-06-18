from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.utils.response import success_response
from app.core.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def get_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取概览统计数据"""
    stats = StatsService.get_overview_stats(db)
    return success_response(stats)


@router.get("/distribution")
def get_alert_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取告警分布统计"""
    distribution = StatsService.get_alert_distribution(db)
    return success_response(distribution)


@router.get("/detections")
def get_detection_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取检测统计数据"""
    stats = StatsService.get_detection_stats(db, days)
    return success_response(stats)


@router.get("/compliance")
def get_safety_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取安全合规统计"""
    compliance = StatsService.get_safety_compliance(db)
    return success_response(compliance)


@router.get("/time-series")
def get_time_series(
    metric: str = Query(..., description="指标类型: alerts, detections"),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取时间序列数据"""
    data = StatsService.get_time_series_data(db, metric, days)
    return success_response(data)


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取综合统计摘要"""
    overview = StatsService.get_overview_stats(db)
    distribution = StatsService.get_alert_distribution(db)
    compliance = StatsService.get_safety_compliance(db)
    
    return success_response({
        'overview': overview,
        'distribution': distribution,
        'compliance': compliance
    })