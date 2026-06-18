from typing import List, Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO
import os

from .base import DetectorBase

class SafetyHelmetDetector(DetectorBase):
    """安全帽检测器"""
    
    def __init__(self, model_path: str = None, conf_threshold: float = 0.5):
        super().__init__('safety_helmet', model_path)
        self.conf_threshold = conf_threshold
        self.helmet_class_id = 0  # 安全帽类别ID
    
    def load_model(self):
        """加载安全帽检测模型"""
        if self.model_path and os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            print("使用预训练的YOLOv8模型进行安全帽检测")
            self.model = YOLO('yolov8n.pt')
            # 在通用模型中，安全帽可能在自定义数据集中，这里我们使用person类别来演示
            # 实际部署时应该使用专门训练的安全帽检测模型
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测安全帽"""
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
                
                # 检测人员
                if class_name == 'person':
                    detections.append({
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'confidence': conf,
                        'class_id': cls,
                        'class_name': class_name,
                        'detector': self.name,
                        'has_helmet': False,  # 默认无安全帽（实际需要专门模型）
                        'alert': not self._check_helmet_presence(box)
                    })
        
        return detections
    
    def _check_helmet_presence(self, box) -> bool:
        """检查是否佩戴安全帽（简化版本）"""
        # 实际应该使用专门训练的安全帽检测模型
        # 这里简化为随机模拟
        return False
    
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """绘制检测结果"""
        output_frame = frame.copy()
        
        for det in results:
            x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
            conf = det['confidence']
            has_helmet = det.get('has_helmet', False)
            
            # 根据是否佩戴安全帽设置颜色
            color = (0, 255, 0) if has_helmet else (0, 0, 255)
            label = f"Person: {conf:.2f} {'(Helmet)' if has_helmet else '(No Helmet!)'}"
            
            # 绘制边界框
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            cv2.putText(output_frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # 如果没有安全帽，添加警告标识
            if not has_helmet:
                cv2.putText(output_frame, "⚠ NO HELMET", (x1, y2 + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return output_frame