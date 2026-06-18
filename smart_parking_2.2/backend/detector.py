import cv2
import torch
import os
from ultralytics import YOLO
import logging
import ultralytics.nn.tasks
from database import get_parking_db_connection, update_spot_status
import numpy as np
from shapely.geometry import Polygon, Point
import time

class ParkingSpotDetector:
    def __init__(self, model_path=None, camera_id=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'yolov8n.pt')
        self.current_camera_id = camera_id
        self.last_update_time = {}
        self.status_stability_threshold = 3  # 需要连续3次检测结果一致才更新状态
        self.detection_history = {}  # 记录每个车位的检测历史
        
        try:
            torch.serialization._weights_only = False
            logging.info(f"模型文件路径: {os.path.abspath(model_path)}")
            if not os.path.isfile(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")

            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logging.info(f"使用计算设备: {self.device}")
            self.model = YOLO(model_path)
            self.model.to(self.device)

            # 模型预热
            dummy_frame = torch.zeros((1, 3, 640, 640), dtype=torch.float32).to(self.device)
            self.model.predict(dummy_frame, verbose=False)
            logging.info("YOLOv8模型加载成功")

        except Exception as e:
            logging.critical(f"模型初始化失败: {str(e)}", exc_info=True)
            raise

    def is_vehicle_in_spot(self, vehicle_bbox, spot_coords):
        """判断车辆是否在车位内"""
        try:
            # 创建车位多边形
            spot_polygon = Polygon([
                (spot_coords[0], spot_coords[1]),  # 左上
                (spot_coords[2], spot_coords[3]),  # 右上
                (spot_coords[4], spot_coords[5]),  # 右下
                (spot_coords[6], spot_coords[7])   # 左下
            ])
            
            # 车辆边界框中心点
            x1, y1, x2, y2 = vehicle_bbox
            vehicle_center = Point((x1 + x2) / 2, (y1 + y2) / 2)
            
            # 计算重叠面积
            vehicle_polygon = Polygon([
                (x1, y1), (x2, y1), (x2, y2), (x1, y2)
            ])
            
            intersection = spot_polygon.intersection(vehicle_polygon)
            overlap_ratio = intersection.area / vehicle_polygon.area if vehicle_polygon.area > 0 else 0
            
            # 如果重叠面积超过50%或中心点在车位内，认为车位被占用
            return overlap_ratio > 0.5 or spot_polygon.contains(vehicle_center)
            
        except Exception as e:
            logging.error(f"车位占用判断失败: {str(e)}")
            return False

    def update_parking_spot_status(self, spot_id, new_status):
        """更新车位状态（带稳定性检查）"""
        current_time = time.time()
        
        # 初始化检测历史
        if spot_id not in self.detection_history:
            self.detection_history[spot_id] = []
        
        # 添加当前检测结果
        self.detection_history[spot_id].append({
            'status': new_status,
            'timestamp': current_time
        })
        
        # 只保留最近的检测记录
        self.detection_history[spot_id] = [
            record for record in self.detection_history[spot_id]
            if current_time - record['timestamp'] < 10  # 10秒内的记录
        ]
        
        # 检查状态稳定性
        recent_statuses = [record['status'] for record in self.detection_history[spot_id][-self.status_stability_threshold:]]
        
        if len(recent_statuses) >= self.status_stability_threshold and all(status == new_status for status in recent_statuses):
            # 状态稳定，更新数据库
            if spot_id not in self.last_update_time or current_time - self.last_update_time[spot_id] > 5:
                if update_spot_status(spot_id, new_status):
                    self.last_update_time[spot_id] = current_time
                    logging.info(f"车位 {spot_id} 状态更新为: {new_status}")

    def detect_objects(self, frame):
        try:
            if frame is None or frame.size == 0:
                logging.warning("接收到空帧")
                return []

            # 预处理流程
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = torch.from_numpy(rgb_frame).float()
            input_tensor = input_tensor.permute(2, 0, 1).unsqueeze(0) / 255.0

            # 执行推理
            results = self.model.predict(input_tensor, verbose=False)

            # 解析车辆检测结果（class_id 2 通常是汽车）
            detected_vehicles = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # 只处理车辆类别（汽车、卡车、公交车等）
                    if class_id in [2, 3, 5, 7] and confidence > 0.5:  # 车辆类别ID
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        detected_vehicles.append((x1, y1, x2, y2, class_id, confidence))

            # 获取当前摄像头的所有车位
            if self.current_camera_id is not None:
                conn = get_parking_db_connection()
                c = conn.cursor()
                c.execute('SELECT * FROM parking_spots WHERE camera_id = ?', (self.current_camera_id,))
                parking_spots = c.fetchall()
                conn.close()
                
                # 检查每个车位的占用状态
                for spot in parking_spots:
                    spot_id = spot[0]
                    spot_coords = [spot[2], spot[3], spot[4], spot[5], spot[6], spot[7], spot[8], spot[9]]
                    
                    # 检查是否有车辆在此车位
                    is_occupied = False
                    for vehicle in detected_vehicles:
                        if self.is_vehicle_in_spot(vehicle[:4], spot_coords):
                            is_occupied = True
                            break
                    
                    # 更新车位状态
                    new_status = 'occupied' if is_occupied else 'empty'
                    self.update_parking_spot_status(spot_id, new_status)
                    
                    # 在图像上绘制车位
                    points = np.array([
                        [spot[2], spot[3]],  # 左上
                        [spot[4], spot[5]],  # 右上
                        [spot[6], spot[7]],  # 右下
                        [spot[8], spot[9]]   # 左下
                    ], np.int32)
                    
                    # 根据状态选择颜色
                    color = (0, 0, 255) if is_occupied else (0, 255, 0)  # 红色=占用，绿色=空闲
                    cv2.polylines(frame, [points], True, color, 2)
                    
                    # 添加车位编号和状态
                    status_text = f"{spot[1]} - {'占用' if is_occupied else '空闲'}"
                    cv2.putText(frame, status_text, (spot[2], spot[3] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                # 绘制检测到的车辆
                for vehicle in detected_vehicles:
                    x1, y1, x2, y2, class_id, confidence = vehicle
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f'Vehicle: {confidence:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            return detected_vehicles

        except Exception as e:
            logging.error(f"检测失败: {str(e)}", exc_info=True)
            return []

    def set_camera_id(self, camera_id):
        """设置当前摄像头ID"""
        self.current_camera_id = camera_id
        # 清空该摄像头的检测历史
        self.detection_history.clear()
        self.last_update_time.clear()