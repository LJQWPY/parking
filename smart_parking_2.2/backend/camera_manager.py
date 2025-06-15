# camera_manager.py
import cv2
import logging
import os
import time

class CameraManager:
    MAX_CAMERA_ATTEMPTS = 3
    FRAME_RATE = 30
    FRAME_INTERVAL = 1 / FRAME_RATE
    RECONNECT_INTERVAL = 2  # 重连间隔时间（秒）
    CONNECT_TIMEOUT = 3000  # 连接超时时间（毫秒）
    FRAME_READ_TIMEOUT = 1000  # 读帧超时时间（毫秒）
    
    def __init__(self):
        self.cameras = {}
        self.backend = self.get_backend()
        self.camera_health = {}  # 记录摄像头健康状态
        self.last_reconnect_time = {}  # 记录上次重连时间
        self.initialize_cameras()
        self.closed_cameras = set()
        logging.info(f"可用摄像头列表: {list(self.cameras.keys())}")

    def release_camera(self, cam_id):
        """正常关闭摄像头"""
        if cam_id in self.cameras:
            try:
                if self.cameras[cam_id].isOpened():
                    self.cameras[cam_id].release()
                    del self.cameras[cam_id]
                    self.closed_cameras.add(cam_id)  # 添加到正常关闭列表
                    logging.info(f"摄像头 {cam_id} 资源已释放")
                    return True
            except Exception as e:
                logging.error(f"释放摄像头 {cam_id} 资源失败: {str(e)}")
        return False

    def get_backend(self):
        # 调整后端优先级：Windows优先使用MSMF
        backends = [
            cv2.CAP_MSMF,       # Windows首选
            cv2.CAP_DSHOW,      # Windows备用
            cv2.CAP_V4L2,       # Linux
            cv2.CAP_ANY
        ]
        for backend in backends:
            if cv2.videoio_registry.hasBackend(backend):
                return backend
        return cv2.CAP_ANY

    def initialize_cameras(self):
        try:
            logging.info(f"正在使用 {self.backend} 后端初始化摄像头...")
            for cam_id in [0, 1, 2]:
                if self.test_camera(cam_id):
                    cap = cv2.VideoCapture(cam_id, self.backend)
                    cap.set(cv2.CAP_PROP_FPS, self.FRAME_RATE)
                    self.cameras[cam_id] = cap
            if not self.cameras:
                raise RuntimeError("未检测到可用摄像头")
        except Exception as e:
            logging.error(f"摄像头初始化失败: {str(e)}", exc_info=True)
            raise

    def test_camera(self, cam_id):
        try:
            cap = cv2.VideoCapture(cam_id, self.backend)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)  # 确保超时设置生效
            if cap.isOpened():
                logging.info(f"摄像头 {cam_id} 检测成功")
                cap.release()
                return True
            return False
        except Exception as e:
            logging.error(f"摄像头 {cam_id} 测试失败: {str(e)}")
            return False

    def check_camera_status(self, cam_id):
        if cam_id not in self.cameras:
            return False
        return self.cameras[cam_id].isOpened()

    def get_frame(self, cam_id):
        if cam_id not in self.cameras:
            if cam_id in self.closed_cameras:
                return None
            if self.reconnect(cam_id):
                return self.get_frame(cam_id)
            return None

        cap = self.cameras[cam_id]
        try:
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, self.FRAME_READ_TIMEOUT)
            ret, frame = cap.read()
            
            if ret and frame is not None:
                self.camera_health[cam_id] = {
                    "last_success": time.time(),
                    "error_count": 0
                }
                return frame
            else:
                self.update_camera_health(cam_id)
                if self.should_reconnect(cam_id):
                    if self.reconnect(cam_id):
                        return self.get_frame(cam_id)
                return None
                
        except Exception as e:
            logging.error(f"摄像头 {cam_id} 读帧失败: {str(e)}")
            self.update_camera_health(cam_id)
            if self.should_reconnect(cam_id):
                if self.reconnect(cam_id):
                    return self.get_frame(cam_id)
            return None
            
    def update_camera_health(self, cam_id):
        if cam_id not in self.camera_health:
            self.camera_health[cam_id] = {"error_count": 0, "last_success": 0}
        self.camera_health[cam_id]["error_count"] += 1
        
    def should_reconnect(self, cam_id):
        if cam_id not in self.camera_health:
            return True
        health = self.camera_health[cam_id]
        error_threshold = 3
        time_threshold = 5  # 秒
        
        return (health["error_count"] >= error_threshold or
                time.time() - health["last_success"] > time_threshold)

    def reconnect(self, cam_id):
        if cam_id in self.closed_cameras:
            return False
            
        current_time = time.time()
        if cam_id in self.last_reconnect_time:
            if current_time - self.last_reconnect_time[cam_id] < self.RECONNECT_INTERVAL:
                return False
        
        self.last_reconnect_time[cam_id] = current_time
        max_attempts = self.MAX_CAMERA_ATTEMPTS
        
        for attempt in range(max_attempts):
            logging.info(f"尝试重新连接摄像头 {cam_id}（第{attempt+1}次）")
            
            if cam_id in self.cameras:
                try:
                    self.cameras[cam_id].release()
                except Exception:
                    pass
                    
            try:
                cap = cv2.VideoCapture(cam_id, self.backend)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.CONNECT_TIMEOUT)
                cap.set(cv2.CAP_PROP_FPS, self.FRAME_RATE)
                
                if cap.isOpened():
                    # 测试是否能正常读取帧
                    cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, self.FRAME_READ_TIMEOUT)
                    ret, _ = cap.read()
                    if ret:
                        self.cameras[cam_id] = cap
                        self.camera_health[cam_id] = {
                            "last_success": time.time(),
                            "error_count": 0
                        }
                        logging.info(f"摄像头 {cam_id} 重连成功")
                        return True
                    else:
                        cap.release()
                        
            except Exception as e:
                logging.error(f"重连摄像头 {cam_id} 时发生错误: {str(e)}")
                
            time.sleep(self.RECONNECT_INTERVAL)
            
        logging.error(f"摄像头 {cam_id} 重连失败")
        return False

    def check_stream_health(self, cam_id):
        test_frames = 5
        error_count = 0
        for _ in range(test_frames):
            frame = self.get_frame(cam_id)
            if frame is None:
                error_count += 1
        return error_count < 2

    def toggle_camera(self, cam_id):
        if cam_id in self.cameras:
            if self.cameras[cam_id].isOpened():
                self.cameras[cam_id].release()
                del self.cameras[cam_id]
                logging.info(f"摄像头 {cam_id} 已关闭")
            else:
                if self.test_camera(cam_id):
                    self.cameras[cam_id] = cv2.VideoCapture(cam_id, self.backend)
        else:
            if self.test_camera(cam_id):
                self.cameras[cam_id] = cv2.VideoCapture(cam_id, self.backend)

    def release_all(self):
        """显式释放所有摄像头资源"""
        for cam_id, cap in self.cameras.items():
            try:
                if cap.isOpened():
                    cap.release()
                    logging.info(f"摄像头 {cam_id} 资源已释放")
            except Exception as e:
                logging.error(f"释放摄像头 {cam_id} 资源失败: {str(e)}")

    def __del__(self):
        # 不再在此处执行释放操作
        pass

    def initialize_single_camera(self, cam_id):
        """初始化单个摄像头"""
        try:
            if self.test_camera(cam_id):
                cap = cv2.VideoCapture(cam_id, self.backend)
                cap.set(cv2.CAP_PROP_FPS, self.FRAME_RATE)
                self.cameras[cam_id] = cap
                if cam_id in self.closed_cameras:
                    self.closed_cameras.remove(cam_id)
                logging.info(f"摄像头 {cam_id} 初始化成功")
                return True
        except Exception as e:
            logging.error(f"摄像头 {cam_id} 初始化失败: {str(e)}")
        return False