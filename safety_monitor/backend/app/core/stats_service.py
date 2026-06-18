from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random

from app.models.alert import Alert
from app.models.camera import Camera
from app.core.alert_service import alert_service


class StatsService:
    """统计服务"""
    
    @staticmethod
    def get_overview_stats(db: Session) -> Dict[str, Any]:
        """获取概览统计数据"""
        # 摄像头统计
        total_cameras = db.query(Camera).count()
        online_cameras = db.query(Camera).filter(Camera.status == 'online').count()
        
        # 今日告警统计
        today = datetime.now().date()
        today_alerts = db.query(Alert).filter(
            func.date(Alert.created_at) == today
        ).count()
        
        # 紧急告警
        urgent_alerts = db.query(Alert).filter(
            Alert.level == 'high',
            Alert.is_handled == False
        ).count()
        
        # 告警趋势数据（最近7天）
        week_stats = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            count = db.query(Alert).filter(
                func.date(Alert.created_at) == date
            ).count()
            week_stats.append({
                'date': date.strftime('%m-%d'),
                'count': count
            })
        
        return {
            'total_cameras': total_cameras,
            'online_cameras': online_cameras,
            'offline_cameras': total_cameras - online_cameras,
            'today_alerts': today_alerts,
            'urgent_alerts': urgent_alerts,
            'week_stats': week_stats
        }
    
    @staticmethod
    def get_alert_distribution(db: Session) -> Dict[str, Any]:
        """获取告警类型分布"""
        # 按告警类型统计
        alert_by_type = db.query(
            Alert.alert_type,
            func.count(Alert.id).label('count')
        ).group_by(Alert.alert_type).all()
        
        # 按级别统计
        alert_by_level = db.query(
            Alert.level,
            func.count(Alert.id).label('count')
        ).group_by(Alert.level).all()
        
        # 按摄像头统计
        alert_by_camera = db.query(
            Alert.camera_id,
            func.count(Alert.id).label('count')
        ).group_by(Alert.camera_id).all()
        
        return {
            'by_type': [{'type': item[0], 'count': item[1]} for item in alert_by_type],
            'by_level': [{'level': item[0], 'count': item[1]} for item in alert_by_level],
            'by_camera': [{'camera_id': item[0], 'count': item[1]} for item in alert_by_camera]
        }
    
    @staticmethod
    def get_detection_stats(db: Session, days: int = 30) -> Dict[str, Any]:
        """获取检测统计数据"""
        since = datetime.now() - timedelta(days=days)
        
        # 总检测数
        total_detections = db.query(Alert).filter(
            Alert.created_at >= since
        ).count()
        
        # 已处理/未处理
        handled = db.query(Alert).filter(
            Alert.created_at >= since,
            Alert.is_handled == True
        ).count()
        
        # 平均处理时间（模拟）
        avg_handling_time = random.uniform(5, 30)
        
        # 按小时分布
        hour_distribution = []
        for hour in range(24):
            count = db.query(Alert).filter(
                Alert.created_at >= since,
                func.extract('hour', Alert.created_at) == hour
            ).count()
            hour_distribution.append({'hour': hour, 'count': count})
        
        return {
            'total_detections': total_detections,
            'handled': handled,
            'unhandled': total_detections - handled,
            'handling_rate': round(handled / total_detections * 100, 2) if total_detections > 0 else 0,
            'avg_handling_time': round(avg_handling_time, 1),
            'hour_distribution': hour_distribution
        }
    
    @staticmethod
    def get_safety_compliance(db: Session) -> Dict[str, Any]:
        """获取安全合规统计"""
        # 计算安全合规率（模拟数据）
        compliance_rate = random.uniform(85, 99)
        
        # 安全装备佩戴统计
        helmet_wearing = {
            'wearing': random.randint(80, 100),
            'not_wearing': random.randint(0, 20)
        }
        
        # 违规类型分布
        violation_types = [
            {'type': '未佩戴安全帽', 'count': random.randint(10, 50)},
            {'type': '危险区域入侵', 'count': random.randint(5, 30)},
            {'type': '烟火隐患', 'count': random.randint(2, 15)},
            {'type': '其他违规', 'count': random.randint(5, 20)}
        ]
        
        return {
            'compliance_rate': round(compliance_rate, 1),
            'helmet_wearing': helmet_wearing,
            'violation_types': sorted(violation_types, key=lambda x: x['count'], reverse=True)
        }
    
    @staticmethod
    def get_time_series_data(db: Session, metric: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取时间序列数据"""
        since = datetime.now() - timedelta(days=days)
        data = []
        
        for i in range(days):
            date = since + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            if metric == 'alerts':
                count = db.query(Alert).filter(
                    Alert.created_at >= date,
                    Alert.created_at < next_date
                ).count()
            elif metric == 'detections':
                count = random.randint(50, 200)
            else:
                count = 0
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': count
            })
        
        return data