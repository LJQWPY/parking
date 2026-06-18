from typing import List, Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO
import os

from .base import DetectorBase

class YOLOv8Detector(DetectorBase):
    """YOLOv8检测器"""
    
    def __init__(self, name: str, model_path: str = None, conf_threshold: float = 0.5):
        super().__init__(name, model_path)
        self.conf_threshold = conf_threshold
        self.class_names = []
    
    def load_model(self):
        """加载YOLOv8模型"""
        if self.model_path is None:
            # 使用预训练模型
            self.model = YOLO('yolov8n.pt')
        else:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                print(f"模型文件不存在: {self.model_path}，使用预训练模型")
                self.model = YOLO('yolov8n.pt')
        
        self.class_names = self.model.names
        print(f"YOLOv8模型加载成功，支持 {len(self.class_names)} 个类别")
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """执行检测"""
        if self.model is None:
            self.load_model()
        
        results = self.model(frame, conf=self.conf_threshold)
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.class_names.get(cls, 'unknown')
                
                detections.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'confidence': conf,
                    'class_id': cls,
                    'class_name': class_name,
                    'detector': self.name
                })
        
        return detections
    
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """绘制检测结果"""
        output_frame = frame.copy()
        
        for det in results:
            x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
            conf = det['confidence']
            class_name = det['class_name']
            
            # 绘制边界框
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(output_frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return output_frame