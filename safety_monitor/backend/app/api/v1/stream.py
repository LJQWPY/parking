from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import cv2
import io
import threading
import time
import numpy as np

from app.database import get_db
from app.models.camera import Camera
from app.models.user import User
from app.models.zone import Zone
from app.api.v1.deps import get_current_user
from app.utils.response import success_response, error_response
from app.ml import DetectionManager
from app.core.alert_service import alert_service

router = APIRouter(prefix="/stream", tags=["stream"])

camera_streams = {}
stream_locks = {}
detection_manager = DetectionManager()

def get_camera_stream(camera_id: int):
    if camera_id not in camera_streams:
        camera_streams[camera_id] = {"frame": None, "lock": threading.Lock(), "detection_enabled": False}
        stream_locks[camera_id] = threading.Lock()
    return camera_streams[camera_id]

def generate_test_frame(camera_id: int):
    """生成测试帧"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    cv2.putText(frame, f"Camera {camera_id}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(frame, f"Status: ONLINE", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"{timestamp}", (20, 460), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    t = int(time.time() * 10)
    for i in range(5):
        x = int((t + i * 100) % 600)
        y = int(200 + i * 40 + (t % 100) * 0.5)
        cv2.circle(frame, (x, y), 15, (0, 0, 255), -1)
    
    return frame

def capture_frames(camera_id: int, camera_info: Camera, db: Session):
    """后台线程捕获摄像头帧"""
    cap = None
    try:
        if camera_info.ip_address.startswith('rtsp://'):
            cap = cv2.VideoCapture(camera_info.ip_address)
        elif camera_info.ip_address.startswith('http://') or camera_info.ip_address.startswith('https://'):
            cap = cv2.VideoCapture(camera_info.ip_address)
        else:
            try:
                cap = cv2.VideoCapture(int(camera_info.ip_address))
            except (ValueError, TypeError):
                pass
        
        if cap and cap.isOpened():
            while camera_info.status == 'online':
                ret, frame = cap.read()
                if ret:
                    stream = get_camera_stream(camera_id)
                    with stream["lock"]:
                        stream["frame"] = frame.copy()
                time.sleep(0.033)
        else:
            while camera_info.status == 'online':
                frame = generate_test_frame(camera_id)
                stream = get_camera_stream(camera_id)
                with stream["lock"]:
                    stream["frame"] = frame.copy()
                time.sleep(0.033)
                
    except Exception as e:
        print(f"摄像头 {camera_id} 捕获失败: {str(e)}")
        while camera_info.status == 'online':
            frame = generate_test_frame(camera_id)
            stream = get_camera_stream(camera_id)
            with stream["lock"]:
                stream["frame"] = frame.copy()
            time.sleep(0.033)
    finally:
        if cap:
            cap.release()

def process_detection_results(results: list, camera_id: int):
    """处理检测结果并生成告警"""
    for result in results:
        if result.get('alert', False):
            alert_data = {
                'camera_id': camera_id,
                'zone_id': result.get('zone_id'),
                'class_name': result.get('class_name', 'unknown'),
                'confidence': result.get('confidence', 0),
                'x1': result.get('x1'),
                'y1': result.get('y1'),
                'x2': result.get('x2'),
                'y2': result.get('y2'),
                'zone_name': result.get('zone_name')
            }
            alert_service.add_alert(alert_data)

@router.get("/{camera_id}")
def get_video_stream(
    camera_id: int,
    detection: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取摄像头实时视频流"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    stream = get_camera_stream(camera_id)
    stream["detection_enabled"] = detection
    
    if detection:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if camera and camera.zone_id:
            zone = db.query(Zone).filter(Zone.id == camera.zone_id).first()
            if zone:
                zone_list = [{
                    'id': zone.id,
                    'name': zone.name,
                    'coordinates': zone.coordinates if zone.coordinates else []
                }]
                detection_manager.set_zones(zone_list)
    
    def generate():
        while True:
            with stream["lock"]:
                frame = stream["frame"]
            
            if frame is None:
                frame = generate_test_frame(camera_id)
            
            if stream.get("detection_enabled", False):
                results = detection_manager.detect(frame)
                frame = detection_manager.draw_results(frame, results)
                
                process_detection_results(results, camera_id)
            
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/{camera_id}/start")
def start_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """启动摄像头流"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    if camera.status == 'online':
        return success_response(None, "摄像头流已在运行")
    
    with stream_locks.get(camera_id, threading.Lock()):
        camera.status = 'online'
        db.commit()
        
        thread = threading.Thread(target=capture_frames, args=(camera_id, camera, db), daemon=True)
        thread.start()
    
    alert_service.start(db)
    
    return success_response(None, "摄像头流已启动")

@router.post("/{camera_id}/stop")
def stop_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停止摄像头流"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    camera.status = 'offline'
    db.commit()
    
    return success_response(None, "摄像头流已停止")

@router.post("/{camera_id}/detection/toggle")
def toggle_detection(
    camera_id: int,
    enabled: bool = Query(..., alias="enabled"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换AI检测功能"""
    stream = get_camera_stream(camera_id)
    stream["detection_enabled"] = enabled
    
    if enabled:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if camera and camera.zone_id:
            zone = db.query(Zone).filter(Zone.id == camera.zone_id).first()
            if zone:
                zone_list = [{
                    'id': zone.id,
                    'name': zone.name,
                    'coordinates': zone.coordinates if zone.coordinates else []
                }]
                detection_manager.set_zones(zone_list)
    
    return success_response({"detection_enabled": enabled})

@router.get("/detection/status")
def get_detection_status(current_user: User = Depends(get_current_user)):
    """获取检测管理器状态"""
    return success_response(detection_manager.get_detector_status())