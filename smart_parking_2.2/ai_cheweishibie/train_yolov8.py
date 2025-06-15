#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8n 停车场车位和车辆检测训练程序
作者: AI Assistant
日期: 2024
描述: 用于训练YOLOv8n模型检测停车场中的车位和车辆
"""

import os
import sys
import yaml
import torch
from pathlib import Path
from ultralytics import YOLO
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ParkingYOLOTrainer:
    def __init__(self, config_path='config/parking_dataset.yaml'):
        """
        初始化训练器
        
        Args:
            config_path (str): 数据集配置文件路径
        """
        self.config_path = config_path
        self.model = None
        self.config = None
        self.project_root = Path(__file__).parent
        
        # 创建必要的目录
        self.create_directories()
        
        # 加载配置
        self.load_config()
        
    def create_directories(self):
        """创建训练所需的目录结构"""
        directories = [
            'datasets/parking_dataset/images/train',
            'datasets/parking_dataset/images/val', 
            'datasets/parking_dataset/images/test',
            'datasets/parking_dataset/labels/train',
            'datasets/parking_dataset/labels/val',
            'datasets/parking_dataset/labels/test',
            'runs/detect',
            'models/trained'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {dir_path}")
    
    def load_config(self):
        """加载数据集配置"""
        config_file = self.project_root / self.config_path
        if not config_file.exists():
            logger.error(f"配置文件不存在: {config_file}")
            return False
            
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        logger.info(f"加载配置文件: {config_file}")
        logger.info(f"类别数量: {self.config['nc']}")
        logger.info(f"类别名称: {self.config['names']}")
        return True
    
    def initialize_model(self, model_size='yolov8n.pt'):
        """初始化YOLO模型"""
        try:
            # 检查是否有预训练模型
            pretrained_path = self.project_root.parent / 'models' / model_size
            if pretrained_path.exists():
                logger.info(f"加载预训练模型: {pretrained_path}")
                self.model = YOLO(str(pretrained_path))
            else:
                logger.info(f"下载预训练模型: {model_size}")
                self.model = YOLO(model_size)
            
            return True
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            return False
    
    def train(self, epochs=100, imgsz=640, batch=16, workers=8, device='auto'):
        """
        开始训练模型
        
        Args:
            epochs (int): 训练轮数
            imgsz (int): 输入图像尺寸
            batch (int): 批次大小
            workers (int): 数据加载器工作进程数
            device (str): 训练设备 ('auto', 'cpu', 'cuda', '0', '1', etc.)
        """
        if not self.model:
            logger.error("模型未初始化")
            return False
        
        if not self.config:
            logger.error("配置未加载")
            return False
        
        # 检查数据集是否存在
        dataset_path = self.project_root / self.config['path']
        if not dataset_path.exists():
            logger.error(f"数据集路径不存在: {dataset_path}")
            logger.info("请先准备数据集，运行 prepare_dataset.py")
            return False
        
        # 训练参数
        train_args = {
            'data': str(self.project_root / self.config_path),
            'epochs': epochs,
            'imgsz': imgsz,
            'batch': batch,
            'workers': workers,
            'device': device,
            'project': str(self.project_root / 'runs' / 'detect'),
            'name': f'parking_yolov8n_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'save': True,
            'save_period': 10,  # 每10个epoch保存一次
            'cache': True,
            'optimizer': 'AdamW',
            'lr0': 0.01,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'pose': 12.0,
            'kobj': 2.0,
            'label_smoothing': 0.0,
            'nbs': 64,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 0.0,
            'perspective': 0.0,
            'flipud': 0.0,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.0,
            'copy_paste': 0.0
        }
        
        logger.info("开始训练...")
        logger.info(f"训练参数: {train_args}")
        
        try:
            # 开始训练
            results = self.model.train(**train_args)
            
            # 保存最终模型
            final_model_path = self.project_root / 'models' / 'trained' / 'parking_yolov8n_final.pt'
            self.model.save(str(final_model_path))
            logger.info(f"训练完成，模型保存至: {final_model_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"训练过程中出现错误: {e}")
            return False
    
    def validate(self, model_path=None):
        """验证模型性能"""
        if model_path:
            model = YOLO(model_path)
        else:
            model = self.model
        
        if not model:
            logger.error("没有可用的模型进行验证")
            return False
        
        try:
            results = model.val(data=str(self.project_root / self.config_path))
            logger.info(f"验证结果: {results}")
            return results
        except Exception as e:
            logger.error(f"验证过程中出现错误: {e}")
            return False
    
    def export_model(self, model_path=None, format='onnx'):
        """导出模型为其他格式"""
        if model_path:
            model = YOLO(model_path)
        else:
            model = self.model
        
        if not model:
            logger.error("没有可用的模型进行导出")
            return False
        
        try:
            export_path = model.export(format=format)
            logger.info(f"模型导出成功: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"模型导出失败: {e}")
            return False

def main():
    """主函数"""
    # 检查CUDA是否可用
    if torch.cuda.is_available():
        logger.info(f"CUDA可用，GPU数量: {torch.cuda.device_count()}")
        device = '0'  # 使用第一个GPU
    else:
        logger.info("CUDA不可用，使用CPU训练")
        device = 'cpu'
    
    # 创建训练器
    trainer = ParkingYOLOTrainer()
    
    # 初始化模型
    if not trainer.initialize_model('yolov8n.pt'):
        logger.error("模型初始化失败")
        return
    
    # 开始训练
    results = trainer.train(
        epochs=100,
        imgsz=640,
        batch=16 if device != 'cpu' else 8,
        workers=8 if device != 'cpu' else 4,
        device=device
    )
    
    if results:
        logger.info("训练成功完成")
        
        # 验证模型
        trainer.validate()
        
        # 导出模型
        trainer.export_model(format='onnx')
    else:
        logger.error("训练失败")

if __name__ == '__main__':
    main()