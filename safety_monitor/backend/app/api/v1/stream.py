from fastapi import APIRouter, Depends, HTTPException, Response, status
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
from app.api.v1.deps import get_current_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/stream", tags=["stream"])

camera_streams = {}
stream_locks = {}

def get_camera_stream(camera_id: int):
    if camera_id not in camera_streams:
        camera_streams[camera_id] = {"frame": None, "lock": threading.Lock()}
        stream_locks[camera_id] = threading.Lock()
    return camera_streams[camera_id]

def generate_test_frame(camera_id: int):
    """生成测试帧"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 添加一些模拟内容
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    cv2.putText(frame, f"Camera {camera_id}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(frame, f"Status: ONLINE", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"{timestamp}", (20, 460), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # 添加一些模拟运动效果
    t = int(time.time() * 10)
    for i in range(5):
        x = int((t + i * 100) % 600)
        y = int(200 + i * 40 + (t % 100) * 0.5)
        cv2.circle(frame, (x, y), 15, (0, 0, 255), -1)
    
    return frame

def capture_frames(camera_id: int, camera_info: Camera):
    try:
        cap = None
        
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

@router.get("/{camera_id}")
def get_video_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    stream = get_camera_stream(camera_id)
    
    def generate():
        while True:
            with stream["lock"]:
                frame = stream["frame"]
            
            if frame is None:
                frame = generate_test_frame(camera_id)
            
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
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    if camera.status == 'online':
        return success_response(None, "摄像头流已在运行")
    
    with stream_locks.get(camera_id, threading.Lock()):
        camera.status = 'online'
        db.commit()
        
        thread = threading.Thread(target=capture_frames, args=(camera_id, camera), daemon=True)
        thread.start()
    
    return success_response(None, "摄像头流已启动")

@router.post("/{camera_id}/stop")
def stop_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return error_response(404, "摄像头不存在")
    
    camera.status = 'offline'
    db.commit()
    
    return success_response(None, "摄像头流已停止")