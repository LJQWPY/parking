from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import threading
import time

from app.models.alert import Alert
from app.models.camera import Camera

class AlertService:
    """告警服务"""
    
    def __init__(self):
        self.alert_queue = []
        self.processing_thread = None
        self.running = False
        self.lock = threading.Lock()
    
    def start(self, db: Session):
        """启动告警处理线程"""
        if not self.running:
            self.running = True
            self.processing_thread = threading.Thread(target=self._process_alerts, args=(db,), daemon=True)
            self.processing_thread.start()
    
    def stop(self):
        """停止告警处理线程"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
    
    def add_alert(self, alert_data: Dict[str, Any]):
        """添加告警到队列"""
        with self.lock:
            self.alert_queue.append(alert_data)
    
    def _process_alerts(self, db: Session):
        """处理告警队列"""
        while self.running:
            while self.alert_queue:
                with self.lock:
                    alert_data = self.alert_queue.pop(0)
                
                try:
                    self._save_alert(db, alert_data)
                except Exception as e:
                    print(f"保存告警失败: {str(e)}")
            
            time.sleep(0.1)
    
    def _save_alert(self, db: Session, alert_data: Dict[str, Any]):
        """保存告警到数据库"""
        alert_type = alert_data.get('class_name', 'unknown')
        level = self._determine_level(alert_type)
        
        alert = Alert(
            camera_id=alert_data.get('camera_id', 0),
            zone_id=alert_data.get('zone_id'),
            alert_type=alert_type,
            level=level,
            image_url=alert_data.get('image_url'),
            video_url=alert_data.get('video_url'),
            description=self._generate_description(alert_data),
            is_handled=False,
            created_at=datetime.now()
        )
        
        db.add(alert)
        db.commit()
        print(f"告警已保存: {alert_type} - 摄像头 {alert.camera_id}")
    
    def _determine_level(self, alert_type: str) -> str:
        """确定告警级别"""
        high_level_types = ['fire', 'smoke', 'flame', 'intrusion']
        medium_level_types = ['no_helmet', 'person']
        
        if alert_type.lower() in high_level_types:
            return 'high'
        elif alert_type.lower() in medium_level_types:
            return 'medium'
        return 'low'
    
    def _generate_description(self, alert_data: Dict[str, Any]) -> str:
        """生成告警描述"""
        descriptions = {
            'fire': '检测到火焰',
            'smoke': '检测到烟雾',
            'flame': '检测到火焰',
            'person': '检测到人员',
            'no_helmet': '检测到未佩戴安全帽',
            'intrusion': '检测到危险区域入侵'
        }
        
        base_desc = descriptions.get(alert_data.get('class_name'), '检测到异常')
        
        if 'zone_name' in alert_data:
            base_desc += f" - {alert_data['zone_name']}"
        
        if 'confidence' in alert_data:
            base_desc += f" (置信度: {alert_data['confidence']:.2f})"
        
        return base_desc
    
    def get_alerts_by_camera(self, db: Session, camera_id: int, limit: int = 100) -> List[Alert]:
        """获取指定摄像头的告警"""
        return db.query(Alert)\
            .filter(Alert.camera_id == camera_id)\
            .order_by(Alert.created_at.desc())\
            .limit(limit)\
            .all()
    
    def get_alerts_by_level(self, db: Session, level: str, limit: int = 100) -> List[Alert]:
        """获取指定级别的告警"""
        return db.query(Alert)\
            .filter(Alert.level == level)\
            .order_by(Alert.created_at.desc())\
            .limit(limit)\
            .all()
    
    def get_unhandled_alerts(self, db: Session, limit: int = 100) -> List[Alert]:
        """获取未处理的告警"""
        return db.query(Alert)\
            .filter(Alert.is_handled == False)\
            .order_by(Alert.created_at.desc())\
            .limit(limit)\
            .all()
    
    def handle_alert(self, db: Session, alert_id: int, handled_by: str = None):
        """处理告警"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_handled = True
            alert.handled_by = handled_by
            alert.handled_at = datetime.now()
            db.commit()
            return True
        return False
    
    def get_alert_stats(self, db: Session, hours: int = 24) -> Dict[str, int]:
        """获取告警统计"""
        from datetime import timedelta
        
        since = datetime.now() - timedelta(hours=hours)
        
        total = db.query(Alert).filter(Alert.created_at >= since).count()
        high = db.query(Alert).filter(Alert.created_at >= since, Alert.level == 'high').count()
        medium = db.query(Alert).filter(Alert.created_at >= since, Alert.level == 'medium').count()
        low = db.query(Alert).filter(Alert.created_at >= since, Alert.level == 'low').count()
        unhandled = db.query(Alert).filter(Alert.created_at >= since, Alert.is_handled == False).count()
        
        return {
            'total': total,
            'high': high,
            'medium': medium,
            'low': low,
            'unhandled': unhandled
        }

# 全局告警服务实例
alert_service = AlertService()