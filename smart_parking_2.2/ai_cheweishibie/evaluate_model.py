#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型评估和测试脚本
用于评估训练好的YOLOv8模型性能
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import logging
from tqdm import tqdm
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, model_path, config_path='config/parking_dataset.yaml'):
        """
        初始化模型评估器
        
        Args:
            model_path (str): 训练好的模型路径
            config_path (str): 数据集配置文件路径
        """
        self.model_path = model_path
        self.config_path = config_path
        self.model = None
        self.class_names = ['vehicle', 'parking_spot']
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载训练好的模型"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"模型加载成功: {self.model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
    
    def evaluate_on_test_set(self, test_dir='datasets/parking_dataset/images/test'):
        """在测试集上评估模型"""
        if not self.model:
            logger.error("模型未加载")
            return
        
        test_path = Path(__file__).parent / test_dir
        if not test_path.exists():
            logger.error(f"测试目录不存在: {test_path}")
            return
        
        # 获取测试图像
        image_files = list(test_path.glob('*.jpg')) + \
                     list(test_path.glob('*.png')) + \
                     list(test_path.glob('*.jpeg'))
        
        if not image_files:
            logger.warning("测试目录中没有找到图像文件")
            return
        
        logger.info(f"开始评估 {len(image_files)} 张测试图像")
        
        # 运行推理
        results = self.model(test_path, save=True, conf=0.25, iou=0.45)
        
        # 计算指标
        metrics = self.model.val(data=self.config_path)
        
        logger.info("评估完成")
        logger.info(f"mAP50: {metrics.box.map50:.4f}")
        logger.info(f"mAP50-95: {metrics.box.map:.4f}")
        
        return metrics
    
    def test_single_image(self, image_path, save_result=True):
        """测试单张图像"""
        if not self.model:
            logger.error("模型未加载")
            return None
        
        # 运行推理
        results = self.model(image_path, conf=0.25, iou=0.45)
        
        # 获取结果
        result = results[0]
        
        # 打印检测结果
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            
            logger.info(f"检测到 {len(boxes)} 个目标:")
            for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"
                logger.info(f"  {i+1}. {class_name}: {conf:.3f} - [{box[0]:.1f}, {box[1]:.1f}, {box[2]:.1f}, {box[3]:.1f}]")
        
        # 保存结果图像
        if save_result:
            output_path = Path(image_path).parent / f"result_{Path(image_path).name}"
            annotated_image = result.plot()
            cv2.imwrite(str(output_path), annotated_image)
            logger.info(f"结果保存至: {output_path}")
        
        return result
    
    def benchmark_speed(self, test_images_count=100):
        """性能基准测试"""
        if not self.model:
            logger.error("模型未加载")
            return
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # 预热
        for _ in range(10):
            self.model(test_image, verbose=False)
        
        # 计时测试
        import time
        start_time = time.time()
        
        for _ in tqdm(range(test_images_count), desc="速度测试"):
            self.model(test_image, verbose=False)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        fps = test_images_count / total_time
        avg_time = total_time / test_images_count * 1000  # ms
        
        logger.info(f"性能测试结果:")
        logger.info(f"总时间: {total_time:.2f}s")
        logger.info(f"平均推理时间: {avg_time:.2f}ms")
        logger.info(f"FPS: {fps:.2f}")
        
        return {
            'total_time': total_time,
            'avg_time_ms': avg_time,
            'fps': fps
        }
    
    def export_model_info(self, output_file='model_info.json'):
        """导出模型信息"""
        if not self.model:
            logger.error("模型未加载")
            return
        
        model_info = {
            'model_path': str(self.model_path),
            'model_type': 'YOLOv8n',
            'classes': self.class_names,
            'input_size': [640, 640],
            'parameters': sum(p.numel() for p in self.model.model.parameters()),
            'model_size_mb': Path(self.model_path).stat().st_size / (1024 * 1024)
        }
        
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"模型信息导出至: {output_path}")
        return model_info

def main():
    """主函数"""
    # 模型路径（请根据实际训练结果修改）
    model_path = 'models/trained/parking_yolov8n_final.pt'
    
    # 检查模型文件是否存在
    if not Path(model_path).exists():
        logger.error(f"模型文件不存在: {model_path}")
        logger.info("请先运行 train_yolov8.py 训练模型")
        return
    
    # 创建评估器
    evaluator = ModelEvaluator(model_path)
    
    # 在测试集上评估
    evaluator.evaluate_on_test_set()
    
    # 性能基准测试
    evaluator.benchmark_speed()
    
    # 导出模型信息
    evaluator.export_model_info()
    
    logger.info("模型评估完成")

if __name__ == '__main__':
    main()