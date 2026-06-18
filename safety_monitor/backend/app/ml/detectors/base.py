from abc import ABC, abstractmethod
from typing import List, Dict, Any
import cv2
import numpy as np

class DetectorBase(ABC):
    """检测器基类"""
    
    def __init__(self, name: str, model_path: str = None):
        self.name = name
        self.model_path = model_path
        self.model = None
        self.enabled = True
    
    @abstractmethod
    def load_model(self):
        """加载模型"""
        pass
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测方法，返回检测结果列表"""
        pass
    
    @abstractmethod
    def draw_results(self, frame: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
        """在帧上绘制检测结果"""
        pass
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled