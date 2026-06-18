from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from ultralytics import YOLO
import os

from .base import DetectorBase

class ZoneInvasionDetector(DetectorBase):
    """危险区域入侵检测器"""
    
    def __init__(self, model_path: str = None, conf_threshold: float = 0.5):
        super().__init__('zone_invasion', model_path)
        self.conf_threshold = conf_threshold
        self.zones = []  # 危险区域列表
        self.person_detector = None
    
    def load_model(self):
        """加载人员检测模型"""
        if self.model_path and os.path.exists(self.model_path):
            self.person_detector = YOLO(self.model_path)
        else:
            print("使用预训练的YOLOv8模型进行人员检测")
            self.person_detector = YOLO('yolov8n.pt')
    
    def set_zones(self, zones: List[Dict[str, Any]]):
        """设置危险区域"""
        self.zones = zones
    
    def add_zone(self, zone: Dict[str, Any]):
        """添加危险区域"""
        self.zones.append(zone)
    
    def _is_point_in_polygon(self, point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
        """判断点是否在多边形内"""
        x, y = point
        inside = False
        n = len(polygon)
        
        for i in range(n):
            j = (i + 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            
            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
        
        return inside
    
    def _is_box_in_zone(self, box: Tuple[int, int, int, int], zone_polygon: List[Tuple[int, int]]) -> bool:
        """判断检测框是否侵入危险区域"""
        x1, y1, x2, y2 = box
        
        # 检查四个角点是否在区域内
        corners = [
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2),
            ((x1 + x2) // 2, (y1 + y2) // 2)  # 中心点
        ]
        
        for corner in corners:
            if self._is_point_in_polygon(corner, zone_polygon):
                return True
        
        return False
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测危险区域入侵"""
        if self.person_detector is None:
            self.load_model()
        
        if not self.zones:
            return []
        
        results = self.person_detector(frame, conf=self.conf_threshold)
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.person_detector.names.get(cls, 'unknown')
                
                # 只检测人员
                if class_name != 'person':
                    continue
                
                # 检查是否侵入任何危险区域
                for zone in self.zones:
                    zone_polygon = [(p['x'], p['y']) for p in zone.get('coordinates', [])]
                    if len(zone_polygon) >= 3:
                        if self._is_box_in_zone((x1, y1, x2, y2), zone_polygon):
                            detections.append({
                                'x1': x1,
                                'y1': y1,
                                'x2': x2,
                                'y2': y2,
                                'confidence': conf,
                                'class_id': cls,
                                'class_name': class_name,
                                'detector': self.name,
                                'zone_id': zone.get('id'),
                                'zone_name': zone.get('name'),
                                'alert': True
                            })
        
        return detections
    
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """绘制检测结果"""
        output_frame = frame.copy()
        
        # 先绘制危险区域
        for zone in self.zones:
            zone_polygon = [(p['x'], p['y']) for p in zone.get('coordinates', [])]
            if len(zone_polygon) >= 3:
                pts = np.array(zone_polygon, np.int32).reshape((-1, 1, 2))
                cv2.polylines(output_frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                cv2.putText(output_frame, zone.get('name', 'Zone'), 
                            zone_polygon[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 绘制入侵检测结果
        for det in results:
            x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
            conf = det['confidence']
            zone_name = det.get('zone_name', 'Unknown Zone')
            
            # 绘制边界框（红色闪烁效果）
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # 绘制标签
            label = f"INTRUSION: {conf:.2f}"
            cv2.putText(output_frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # 添加入侵标识
            cv2.putText(output_frame, f"⚠ {zone_name}", (x1, y2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return output_frame