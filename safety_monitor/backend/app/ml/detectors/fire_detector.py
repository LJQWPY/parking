from typing import List, Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO
import os

from .base import DetectorBase

class FireSmokeDetector(DetectorBase):
    """烟火/烟雾检测器"""
    
    def __init__(self, model_path: str = None, conf_threshold: float = 0.5):
        super().__init__('fire_smoke', model_path)
        self.conf_threshold = conf_threshold
    
    def load_model(self):
        """加载烟火检测模型"""
        if self.model_path and os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            print("使用预训练的YOLOv8模型进行烟火检测")
            self.model = YOLO('yolov8n.pt')
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测烟火和烟雾"""
        if self.model is None:
            self.load_model()
        
        results = self.model(frame, conf=self.conf_threshold)
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names.get(cls, 'unknown')
                
                # 检测火焰和烟雾相关类别
                if class_name in ['fire', 'smoke', 'flame']:
                    detections.append({
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'confidence': conf,
                        'class_id': cls,
                        'class_name': class_name,
                        'detector': self.name,
                        'alert': True
                    })
        
        # 基于颜色的烟火检测（辅助）
        color_based_detections = self._detect_by_color(frame)
        detections.extend(color_based_detections)
        
        return detections
    
    def _detect_by_color(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """基于颜色的烟火检测"""
        detections = []
        
        # 转换为HSV色彩空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 红色/橙色区域（火焰颜色范围）
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        fire_mask = cv2.bitwise_or(mask1, mask2)
        
        # 找到轮廓
        contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # 过滤小区域
                x, y, w, h = cv2.boundingRect(contour)
                detections.append({
                    'x1': x,
                    'y1': y,
                    'x2': x + w,
                    'y2': y + h,
                    'confidence': 0.7,
                    'class_id': -1,
                    'class_name': 'fire',
                    'detector': self.name,
                    'alert': True,
                    'detection_method': 'color_based'
                })
        
        return detections
    
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """绘制检测结果"""
        output_frame = frame.copy()
        
        for det in results:
            x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
            conf = det['confidence']
            class_name = det['class_name']
            
            # 绘制边界框（红色表示危险）
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # 绘制标签
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(output_frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # 添加危险标识
            cv2.putText(output_frame, "⚠ DANGER", (x1, y2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return output_frame