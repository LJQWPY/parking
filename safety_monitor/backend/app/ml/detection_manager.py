from typing import List, Dict, Any
import cv2
import numpy as np
import threading
import time

from .detectors.base import DetectorBase
from .detectors.yolov8_detector import YOLOv8Detector
from .detectors.helmet_detector import SafetyHelmetDetector
from .detectors.fire_detector import FireSmokeDetector
from .detectors.zone_detector import ZoneInvasionDetector

class DetectionManager:
    """检测管理器"""
    
    def __init__(self):
        self.detectors: Dict[str, DetectorBase] = {}
        self.detection_enabled = True
        self.lock = threading.Lock()
        
        # 初始化所有检测器
        self._init_detectors()
    
    def _init_detectors(self):
        """初始化检测器"""
        self.detectors['yolov8'] = YOLOv8Detector('general')
        self.detectors['helmet'] = SafetyHelmetDetector()
        self.detectors['fire'] = FireSmokeDetector()
        self.detectors['zone'] = ZoneInvasionDetector()
        
        # 延迟加载模型
        for name, detector in self.detectors.items():
            threading.Thread(target=detector.load_model, daemon=True).start()
    
    def set_zones(self, zones: List[Dict[str, Any]]):
        """设置危险区域"""
        if 'zone' in self.detectors:
            self.detectors['zone'].set_zones(zones)
    
    def detect(self, frame: np.ndarray, detector_names: List[str] = None) -> List[Dict[str, Any]]:
        """执行检测"""
        if not self.detection_enabled:
            return []
        
        if detector_names is None:
            detector_names = list(self.detectors.keys())
        
        all_results = []
        
        with self.lock:
            for name in detector_names:
                if name in self.detectors and self.detectors[name].is_enabled():
                    try:
                        results = self.detectors[name].detect(frame)
                        all_results.extend(results)
                    except Exception as e:
                        print(f"检测器 {name} 执行失败: {str(e)}")
        
        return all_results
    
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """绘制所有检测结果"""
        output_frame = frame.copy()
        
        # 按检测器分组绘制
        detectors_used = set()
        for result in results:
            detector_name = result.get('detector', '')
            if detector_name not in detectors_used:
                detector_name = result.get('detector', 'yolov8')
                if detector_name in self.detectors:
                    output_frame = self.detectors[detector_name].draw_results(output_frame, results)
                    detectors_used.add(detector_name)
        
        return output_frame
    
    def enable_detector(self, detector_name: str):
        """启用检测器"""
        if detector_name in self.detectors:
            self.detectors[detector_name].set_enabled(True)
    
    def disable_detector(self, detector_name: str):
        """禁用检测器"""
        if detector_name in self.detectors:
            self.detectors[detector_name].set_enabled(False)
    
    def toggle_detection(self, enabled: bool):
        """切换检测功能"""
        self.detection_enabled = enabled
    
    def get_detector_status(self) -> Dict[str, bool]:
        """获取所有检测器状态"""
        status = {}
        for name, detector in self.detectors.items():
            status[name] = detector.is_enabled()
        return status