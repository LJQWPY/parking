from flask import Flask, Response, send_file, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required
from dotenv import load_dotenv
import os
import atexit
import logging
import eventlet
import cv2
from flask_cors import CORS
from auth import auth_bp
from database import get_parking_db_connection, init_users_db, init_parking_db
from detector import ParkingSpotDetector
from camera_manager import CameraManager

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8', mode='w')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/static')

app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'JWT_ACCESS_TOKEN_EXPIRES': 3600,
    'JWT_TOKEN_LOCATION': ['headers', 'query_string'],
    'JWT_QUERY_STRING_NAME': 'token',
    'JWT_COOKIE_SECURE': True,
    'JWT_COOKIE_SAMESITE': 'Strict',
    'JWT_HEADER_NAME': 'Authorization',
})

jwt = JWTManager(app)
CORS(app, supports_credentials=True)
app.register_blueprint(auth_bp)

camera_manager = None
detector = None

try:
    camera_manager = CameraManager()
    app.config['camera_manager'] = camera_manager
    detector = ParkingSpotDetector()
    logger.info("核心组件初始化成功")
except Exception as e:
    logger.critical(f"致命错误 - 初始化失败: {str(e)}", exc_info=True)
    exit(1)

def cleanup():
    try:
        if camera_manager:
            camera_manager.release_all()
            logger.info("所有摄像头资源已释放")
    except Exception as e:
        logger.error(f"资源清理异常: {str(e)}", exc_info=True)
    finally:
        logger.info("系统资源清理完成")

atexit.register(cleanup)

@app.route('/')
def index():
    return send_file('../frontend/index.html')

@app.route('/video_feed/<int:cam_id>')
@jwt_required()
def video_feed(cam_id):
    try:
        if cam_id not in camera_manager.cameras:
            if camera_manager.test_camera(cam_id):
                camera_manager.initialize_single_camera(cam_id)
            else:
                logger.warning(f"非法摄像头访问请求: {cam_id}")
                return jsonify({"error": "无效的摄像头ID"}), 404

        detector.set_camera_id(cam_id)

        def generate():
            try:
                while True:
                    frame = camera_manager.get_frame(cam_id)
                    if frame is None:
                        logger.error(f"摄像头 {cam_id} 无法获取有效帧，可能是设备断开连接")
                        break
                    
                    detected_objects = detector.detect_objects(frame)
                    
                    _, buffer = cv2.imencode('.jpg', frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    eventlet.sleep(camera_manager.FRAME_INTERVAL)
            except GeneratorExit:
                logger.info(f"客户端断开连接（摄像头 {cam_id}）")
            except Exception as e:
                logger.error(f"视频流生成异常: {str(e)}", exc_info=True)

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except Exception as e:
        logger.error(f"视频流服务异常: {str(e)}", exc_info=True)
        return jsonify({"error": "视频流服务暂时不可用"}), 500

@app.route('/parking_spots/status/<int:camera_id>', methods=['GET'])
@jwt_required()
def get_parking_status(camera_id):
    try:
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        c.execute('''
        SELECT 
            COUNT(*) as total_spots,
            SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_spots,
            SUM(CASE WHEN status = 'empty' THEN 1 ELSE 0 END) as empty_spots
        FROM parking_spots 
        WHERE camera_id = ?
        ''', (camera_id,))
        
        stats = c.fetchone()
        
        c.execute('''
        SELECT id, name, status, last_updated 
        FROM parking_spots 
        WHERE camera_id = ?
        ORDER BY name
        ''', (camera_id,))
        
        spots_detail = c.fetchall()
        conn.close()
        
        return jsonify({
            'camera_id': camera_id,
            'total_spots': stats[0] or 0,
            'occupied_spots': stats[1] or 0,
            'empty_spots': stats[2] or 0,
            'spots': [{
                'id': spot[0],
                'name': spot[1],
                'status': spot[2],
                'last_updated': spot[3]
            } for spot in spots_detail]
        })
        
    except Exception as e:
        logging.error(f"获取车位状态失败: {str(e)}")
        return jsonify({"error": "获取车位状态失败"}), 500

@app.route('/available_cameras')
@jwt_required()
def available_cameras():
    active_cameras = []
    current_cameras = set(camera_manager.cameras.keys())
    
    for cam_id in range(3):
        if cam_id in current_cameras:
            if camera_manager.check_camera_status(cam_id):
                active_cameras.append(cam_id)
        else:
            cap = cv2.VideoCapture(cam_id, camera_manager.backend)
            if cap.isOpened():
                active_cameras.append(cam_id)
                cap.release()
                camera_manager.initialize_single_camera(cam_id)
    
    return jsonify({
        "available_cameras": active_cameras,
        "current_camera": min(active_cameras) if active_cameras else 0
    })

@app.route('/toggle_camera/<int:cam_id>', methods=['POST'])
@jwt_required()
def toggle_camera(cam_id):
    try:
        camera_manager.toggle_camera(cam_id)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"摄像头切换失败: {str(e)}")
        return jsonify({"error": "摄像头操作失败"}), 500

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        current_camera_id = request.json.get('camera_id', None)
        if current_camera_id is not None:
            if camera_manager.release_camera(current_camera_id):
                return jsonify({"msg": "登出成功，资源已释放"}), 200
            else:
                return jsonify({"msg": "摄像头资源释放失败"}), 500
        return jsonify({"msg": "登出成功"}), 200
    except Exception as e:
        logger.error(f"登出释放资源失败: {str(e)}")
        return jsonify({"msg": "登出过程中出现错误"}), 500

@app.route('/verify_token')
@jwt_required()
def verify_token():
    return jsonify({"status": "valid"}), 200

@app.route('/parking_spots', methods=['GET'])
@jwt_required()
def get_parking_spots():
    try:
        camera_id = request.args.get('camera_id', type=int)
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        if camera_id is not None:
            c.execute('SELECT * FROM parking_spots WHERE camera_id = ?', (camera_id,))
        else:
            c.execute('SELECT * FROM parking_spots')
            
        spots = c.fetchall()
        conn.close()
        
        return jsonify([{
            'id': spot[0],
            'name': spot[1],
            'coordinates': [
                {'x': spot[2], 'y': spot[3]},
                {'x': spot[4], 'y': spot[5]},
                {'x': spot[6], 'y': spot[7]},
                {'x': spot[8], 'y': spot[9]}
            ],
            'camera_id': spot[10],
            'created_at': spot[11]
        } for spot in spots])
    except Exception as e:
        logging.error(f"获取车位信息失败: {str(e)}")
        return jsonify({"error": "获取车位信息失败"}), 500

@app.route('/parking_spots', methods=['POST'])
@jwt_required()
def add_parking_spot():
    try:
        data = request.get_json()
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        c.execute('''
        INSERT INTO parking_spots 
        (name, x1, y1, x2, y2, x3, y3, x4, y4, camera_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['coordinates'][0]['x'], data['coordinates'][0]['y'],
            data['coordinates'][1]['x'], data['coordinates'][1]['y'],
            data['coordinates'][2]['x'], data['coordinates'][2]['y'],
            data['coordinates'][3]['x'], data['coordinates'][3]['y'],
            data['camera_id']
        ))
        
        conn.commit()
        spot_id = c.lastrowid
        conn.close()
        
        return jsonify({"id": spot_id, "message": "车位添加成功"}), 201
    except Exception as e:
        logging.error(f"添加车位失败: {str(e)}")
        return jsonify({"error": "添加车位失败"}), 500

@app.route('/parking_spots/<int:spot_id>', methods=['DELETE'])
@jwt_required()
def delete_parking_spot(spot_id):
    try:
        conn = get_parking_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM parking_spots WHERE id = ?', (spot_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "车位删除成功"})
    except Exception as e:
        logging.error(f"删除车位失败: {str(e)}")
        return jsonify({"error": "删除车位失败"}), 500

@app.route('/parking_spots/<int:spot_id>/status', methods=['PUT'])
@jwt_required()
def update_parking_spot_status(spot_id):
    data = request.get_json()
    status = data.get('status')
    if status is None:
        return jsonify({'error': 'Status is required'}), 400

    conn = get_parking_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE parking_spots SET status = ? WHERE id = ?', (status, spot_id))
        conn.commit()
        return jsonify({'message': f'Parking spot {spot_id} status updated to {status}'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        init_users_db()
        init_parking_db()

    eventlet.monkey_patch(
        os=True,
        select=True,
        socket=True,
        thread=True,
        time=True
    )

    from eventlet import wsgi

    logger.info("启动 Eventlet WSGI 服务器")
    print("Server running on http://localhost:5000")

    wsgi.server(
        eventlet.listen(('0.0.0.0', 5000)),
        app,
        log_output=False
    )