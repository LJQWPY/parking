# app.py
from flask import Flask, Response, send_file, jsonify, request  # 添加 request
from flask_jwt_extended import JWTManager, jwt_required
from dotenv import load_dotenv
import os  # 确保也导入了os模块
import atexit  # 用于注册退出函数
import logging  # 用于日志记录
import eventlet  # 添加这一行
import cv2  # 添加这一行
from flask_cors import CORS
from auth import auth_bp # 移除对 init_db 的导入
from database import get_parking_db_connection, init_users_db, init_parking_db
from detector import ParkingSpotDetector
from camera_manager import CameraManager

# 加载环境变量
load_dotenv()

# 增强日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8', mode='w')  # 清空旧日志
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/static')

# JWT 配置
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'JWT_ACCESS_TOKEN_EXPIRES': 3600,
    'JWT_TOKEN_LOCATION': ['headers', 'query_string']
    ,
    'JWT_QUERY_STRING_NAME': 'token',
    'JWT_COOKIE_SECURE': True,
    'JWT_COOKIE_SAMESITE': 'Strict',
    'JWT_HEADER_NAME': 'Authorization',
})

# 初始化扩展
jwt = JWTManager(app)
CORS(app, supports_credentials=True)
app.register_blueprint(auth_bp)

# 全局组件初始化
try:
    # 在初始化camera_manager的地方修改为
    camera_manager = CameraManager()
    app.config['camera_manager'] = camera_manager
    detector = ParkingSpotDetector()
    logger.info("核心组件初始化成功")
except Exception as e:
    logger.critical(f"致命错误 - 初始化失败: {str(e)}", exc_info=True)
    exit(1)


# 增强退出清理逻辑
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


# 路由定义
@app.route('/')
def index():
    """主页面路由"""
    return send_file('../frontend/index.html')


# 在video_feed函数中添加摄像头ID设置
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

        # 为当前摄像头设置检测器
        detector.set_camera_id(cam_id)

        def generate():
            try:
                while True:
                    frame = camera_manager.get_frame(cam_id)
                    if frame is None:
                        logger.error(f"摄像头 {cam_id} 无法获取有效帧，可能是设备断开连接")
                        break
                    
                    # 执行检测并自动更新车位状态
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

# 添加车位状态统计API
@app.route('/parking_spots/status/<int:camera_id>', methods=['GET'])
@jwt_required()
def get_parking_status(camera_id):
    """获取指定摄像头的车位状态统计"""
    try:
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        # 获取车位状态统计
        c.execute('''
        SELECT 
            COUNT(*) as total_spots,
            SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_spots,
            SUM(CASE WHEN status = 'empty' THEN 1 ELSE 0 END) as empty_spots
        FROM parking_spots 
        WHERE camera_id = ?
        ''', (camera_id,))
        
        stats = c.fetchone()
        
        # 获取详细车位信息
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
    """可用摄像头列表"""
    active_cameras = []
    current_cameras = set(camera_manager.cameras.keys())
    
    # 检查所有可能的摄像头
    for cam_id in range(3):  # 通常检查前3个摄像头索引
        if cam_id in current_cameras:
            if camera_manager.check_camera_status(cam_id):
                active_cameras.append(cam_id)
        else:
            # 检测新插入的摄像头
            cap = cv2.VideoCapture(cam_id, camera_manager.backend)
            if cap.isOpened():
                active_cameras.append(cam_id)
                cap.release()
                # 自动初始化新检测到的摄像头
                camera_manager.initialize_single_camera(cam_id)
    
    return jsonify({
        "available_cameras": active_cameras,
        "current_camera": min(active_cameras) if active_cameras else 0
    })


@app.route('/toggle_camera/<int:cam_id>', methods=['POST'])
@jwt_required()
def toggle_camera(cam_id):
    """切换摄像头"""
    try:
        camera_manager.toggle_camera(cam_id)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"摄像头切换失败: {str(e)}")
        return jsonify({"error": "摄像头操作失败"}), 500

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出时释放摄像头资源"""
    try:
        current_camera_id = request.json.get('camera_id', None)
        if current_camera_id is not None:
            # 使用新的release_camera方法
            if camera_manager.release_camera(current_camera_id):
                return jsonify({"msg": "登出成功，资源已释放"}), 200
            else:
                return jsonify({"msg": "摄像头资源释放失败"}), 500
        return jsonify({"msg": "登出成功"}), 200
    except Exception as e:
        logger.error(f"登出释放资源失败: {str(e)}")
        return jsonify({"msg": "登出过程中出现错误"}), 500

# 启动配置
if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        init_users_db() # 调用用户数据库初始化
        init_parking_db() # 调用车位数据库初始化

    # Eventlet 配置
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

    # 生产环境配置
    wsgi.server(
        eventlet.listen(('0.0.0.0', 5000)),
        app,
        log_output=False  # 禁用eventlet自带日志
    )

@app.route('/verify_token')
@jwt_required()
def verify_token():
    # 如果能通过jwt_required装饰器，说明token有效
    return jsonify({"status": "valid"}), 200

# 在现有导入语句中添加
from database import get_db_connection

# 添加新的路由
@app.route('/parking_spots', methods=['GET'])
@jwt_required()
def get_parking_spots():
    """获取所有车位信息"""
    try:
        camera_id = request.args.get('camera_id', type=int)
        conn = get_parking_db_connection() # 修改函数调用
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
                {'x': spot[2], 'y': spot[3]},  # 左上
                {'x': spot[4], 'y': spot[5]},  # 右上
                {'x': spot[6], 'y': spot[7]},  # 右下
                {'x': spot[8], 'y': spot[9]}   # 左下
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
    """添加新车位"""
    try:
        data = request.get_json()
        conn = get_parking_db_connection() # 修改函数调用
        c = conn.cursor()
        
        c.execute('''
        INSERT INTO parking_spots 
        (name, x1, y1, x2, y2, x3, y3, x4, y4, camera_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['coordinates'][0]['x'], data['coordinates'][0]['y'],  # 左上
            data['coordinates'][1]['x'], data['coordinates'][1]['y'],  # 右上
            data['coordinates'][2]['x'], data['coordinates'][2]['y'],  # 右下
            data['coordinates'][3]['x'], data['coordinates'][3]['y'],  # 左下
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
    """删除车位"""
    try:
        conn = get_parking_db_connection() # 修改函数调用
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

    conn = get_parking_db_connection() # 使用新的车位数据库连接
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

@app.route('/parking_spots/status/<int:camera_id>', methods=['GET'])
@jwt_required()
def get_parking_status(camera_id):
    """获取指定摄像头的车位状态统计"""
    try:
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        # 获取车位状态统计
        c.execute('''
        SELECT 
            COUNT(*) as total_spots,
            SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_spots,
            SUM(CASE WHEN status = 'empty' THEN 1 ELSE 0 END) as empty_spots
        FROM parking_spots 
        WHERE camera_id = ?
        ''', (camera_id,))
        
        stats = c.fetchone()
        
        # 获取详细车位信息
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