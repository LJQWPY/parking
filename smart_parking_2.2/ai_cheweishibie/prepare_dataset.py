#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集准备和预处理脚本
用于准备停车场车位和车辆检测的训练数据
"""

import os
import cv2
import json
import shutil
import random
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetPreparer:
    def __init__(self, source_dir='raw_data', target_dir='datasets/parking_dataset'):
        """
        初始化数据集准备器
        
        Args:
            source_dir (str): 原始数据目录
            target_dir (str): 目标数据集目录
        """
        self.project_root = Path(__file__).parent
        self.source_dir = self.project_root / source_dir
        self.target_dir = self.project_root / target_dir
        
        # 创建目标目录结构
        self.create_dataset_structure()
    
    def create_dataset_structure(self):
        """创建YOLO格式的数据集目录结构"""
        directories = [
            'images/train',
            'images/val',
            'images/test',
            'labels/train',
            'labels/val',
            'labels/test'
        ]
        
        for directory in directories:
            dir_path = self.target_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def convert_coco_to_yolo(self, coco_annotation_file: str):
        """
        将COCO格式的标注转换为YOLO格式
        
        Args:
            coco_annotation_file (str): COCO标注文件路径
        """
        with open(coco_annotation_file, 'r') as f:
            coco_data = json.load(f)
        
        # 创建类别映射
        category_mapping = {}
        for category in coco_data['categories']:
            if category['name'] in ['car', 'truck', 'bus', 'motorcycle']:
                category_mapping[category['id']] = 0  # vehicle
            elif 'parking' in category['name'].lower():
                category_mapping[category['id']] = 1  # parking_spot
        
        # 处理每个图像的标注
        for image_info in tqdm(coco_data['images'], desc="转换标注"):
            image_id = image_info['id']
            image_width = image_info['width']
            image_height = image_info['height']
            image_filename = image_info['file_name']
            
            # 获取该图像的所有标注
            annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]
            
            # 转换为YOLO格式
            yolo_annotations = []
            for ann in annotations:
                category_id = ann['category_id']
                if category_id not in category_mapping:
                    continue
                
                bbox = ann['bbox']  # [x, y, width, height]
                x_center = (bbox[0] + bbox[2] / 2) / image_width
                y_center = (bbox[1] + bbox[3] / 2) / image_height
                width = bbox[2] / image_width
                height = bbox[3] / image_height
                
                yolo_class = category_mapping[category_id]
                yolo_annotations.append(f"{yolo_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
            # 保存YOLO格式标注文件
            if yolo_annotations:
                label_filename = Path(image_filename).stem + '.txt'
                # 这里需要根据实际的数据分割来决定保存到train/val/test
                # 暂时保存到train目录
                label_path = self.target_dir / 'labels' / 'train' / label_filename
                with open(label_path, 'w') as f:
                    f.write('\n'.join(yolo_annotations))
    
    def split_dataset(self, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """
        分割数据集为训练集、验证集和测试集
        
        Args:
            train_ratio (float): 训练集比例
            val_ratio (float): 验证集比例
            test_ratio (float): 测试集比例
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "比例之和必须等于1"
        
        # 获取所有图像文件
        image_files = list((self.target_dir / 'images').glob('*.jpg')) + \
                      list((self.target_dir / 'images').glob('*.png')) + \
                      list((self.target_dir / 'images').glob('*.jpeg'))
        
        # 随机打乱
        random.shuffle(image_files)
        
        # 计算分割点
        total_images = len(image_files)
        train_end = int(total_images * train_ratio)
        val_end = train_end + int(total_images * val_ratio)
        
        # 分割文件列表
        train_files = image_files[:train_end]
        val_files = image_files[train_end:val_end]
        test_files = image_files[val_end:]
        
        # 移动文件到对应目录
        self._move_files_to_split(train_files, 'train')
        self._move_files_to_split(val_files, 'val')
        self._move_files_to_split(test_files, 'test')
        
        logger.info(f"数据集分割完成:")
        logger.info(f"训练集: {len(train_files)} 张图像")
        logger.info(f"验证集: {len(val_files)} 张图像")
        logger.info(f"测试集: {len(test_files)} 张图像")
    
    def _move_files_to_split(self, file_list: List[Path], split: str):
        """将文件移动到指定的数据集分割目录"""
        for image_file in tqdm(file_list, desc=f"移动{split}集文件"):
            # 移动图像文件
            target_image_path = self.target_dir / 'images' / split / image_file.name
            shutil.move(str(image_file), str(target_image_path))
            
            # 移动对应的标注文件
            label_file = image_file.with_suffix('.txt')
            if label_file.exists():
                target_label_path = self.target_dir / 'labels' / split / label_file.name
                shutil.move(str(label_file), str(target_label_path))
    
    def augment_dataset(self, augmentation_factor=2):
        """
        数据增强
        
        Args:
            augmentation_factor (int): 增强倍数
        """
        train_images_dir = self.target_dir / 'images' / 'train'
        train_labels_dir = self.target_dir / 'labels' / 'train'
        
        image_files = list(train_images_dir.glob('*.jpg')) + \
                     list(train_images_dir.glob('*.png')) + \
                     list(train_images_dir.glob('*.jpeg'))
        
        for image_file in tqdm(image_files, desc="数据增强"):
            image = cv2.imread(str(image_file))
            if image is None:
                continue
            
            # 读取对应的标注文件
            label_file = train_labels_dir / (image_file.stem + '.txt')
            annotations = []
            if label_file.exists():
                with open(label_file, 'r') as f:
                    annotations = f.read().strip().split('\n')
            
            # 生成增强图像
            for i in range(augmentation_factor):
                augmented_image, augmented_annotations = self._apply_augmentation(image, annotations)
                
                # 保存增强后的图像和标注
                aug_image_name = f"{image_file.stem}_aug_{i}{image_file.suffix}"
                aug_image_path = train_images_dir / aug_image_name
                cv2.imwrite(str(aug_image_path), augmented_image)
                
                if augmented_annotations:
                    aug_label_path = train_labels_dir / f"{image_file.stem}_aug_{i}.txt"
                    with open(aug_label_path, 'w') as f:
                        f.write('\n'.join(augmented_annotations))
    
    def _apply_augmentation(self, image: np.ndarray, annotations: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        应用数据增强
        
        Args:
            image: 输入图像
            annotations: YOLO格式的标注列表
        
        Returns:
            增强后的图像和标注
        """
        h, w = image.shape[:2]
        
        # 随机选择增强方法
        augmentation_type = random.choice(['flip', 'brightness', 'noise', 'blur'])
        
        if augmentation_type == 'flip' and random.random() > 0.5:
            # 水平翻转
            image = cv2.flip(image, 1)
            # 更新标注中的x坐标
            new_annotations = []
            for ann in annotations:
                if ann.strip():
                    parts = ann.split()
                    class_id = parts[0]
                    x_center = 1.0 - float(parts[1])  # 翻转x坐标
                    y_center = parts[2]
                    width = parts[3]
                    height = parts[4]
                    new_annotations.append(f"{class_id} {x_center:.6f} {y_center} {width} {height}")
            annotations = new_annotations
        
        elif augmentation_type == 'brightness':
            # 亮度调整
            factor = random.uniform(0.7, 1.3)
            image = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        
        elif augmentation_type == 'noise':
            # 添加噪声
            noise = np.random.normal(0, 25, image.shape).astype(np.uint8)
            image = cv2.add(image, noise)
        
        elif augmentation_type == 'blur':
            # 模糊
            kernel_size = random.choice([3, 5])
            image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        return image, annotations
    
    def validate_dataset(self):
        """验证数据集的完整性"""
        splits = ['train', 'val', 'test']
        total_images = 0
        total_labels = 0
        
        for split in splits:
            images_dir = self.target_dir / 'images' / split
            labels_dir = self.target_dir / 'labels' / split
            
            image_files = list(images_dir.glob('*.jpg')) + \
                         list(images_dir.glob('*.png')) + \
                         list(images_dir.glob('*.jpeg'))
            
            label_files = list(labels_dir.glob('*.txt'))
            
            logger.info(f"{split}集: {len(image_files)} 张图像, {len(label_files)} 个标注文件")
            total_images += len(image_files)
            total_labels += len(label_files)
            
            # 检查图像和标注文件是否匹配
            for image_file in image_files:
                label_file = labels_dir / (image_file.stem + '.txt')
                if not label_file.exists():
                    logger.warning(f"缺少标注文件: {label_file}")
        
        logger.info(f"数据集验证完成: 总计 {total_images} 张图像, {total_labels} 个标注文件")

def main():
    """主函数"""
    preparer = DatasetPreparer()
    
    # 如果有COCO格式的标注文件，先转换
    # preparer.convert_coco_to_yolo('path/to/coco/annotations.json')
    
    # 分割数据集
    # preparer.split_dataset()
    
    # 数据增强
    # preparer.augment_dataset(augmentation_factor=2)
    
    # 验证数据集
    preparer.validate_dataset()
    
    logger.info("数据集准备完成！")
    logger.info("请将您的图像和标注文件放入相应的目录中")
    logger.info("然后运行 train_yolov8.py 开始训练")

if __name__ == '__main__':
    main()