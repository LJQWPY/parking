# database.py
import sqlite3
import logging
import os

# 用户数据库路径
USERS_DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
# 车位数据库路径
PARKING_DB_PATH = os.path.join(os.path.dirname(__file__), 'parking.db')

def get_users_db_connection():
    """获取用户数据库连接"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        conn.row_factory = sqlite3.Row  # 启用字典行工厂
        return conn
    except Exception as e:
        logging.error(f"用户数据库连接失败: {str(e)}", exc_info=True)
        raise

def get_parking_db_connection():
    """获取车位数据库连接"""
    try:
        conn = sqlite3.connect(PARKING_DB_PATH)
        conn.row_factory = sqlite3.Row  # 启用字典行工厂
        return conn
    except Exception as e:
        logging.error(f"车位数据库连接失败: {str(e)}", exc_info=True)
        raise

def init_users_db():
    """初始化用户数据库表结构"""
    conn = None
    try:
        conn = get_users_db_connection()
        c = conn.cursor()
        
        # 创建用户表
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logging.info("用户数据库初始化成功")
        
    except Exception as e:
        logging.error(f"用户数据库初始化失败: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_parking_db():
    """初始化车位数据库表结构"""
    conn = None
    try:
        conn = get_parking_db_connection()
        c = conn.cursor()
        
        # 创建车位表
        c.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,                    -- 车位编号/名称
            x1 INTEGER NOT NULL,                   -- 左上角x坐标
            y1 INTEGER NOT NULL,                   -- 左上角y坐标
            x2 INTEGER NOT NULL,                   -- 右上角x坐标
            y2 INTEGER NOT NULL,                   -- 右上角y坐标
            x3 INTEGER NOT NULL,                   -- 右下角x坐标
            y3 INTEGER NOT NULL,                   -- 右下角y坐标
            x4 INTEGER NOT NULL,                   -- 左下角x坐标
            y4 INTEGER NOT NULL,                   -- 左下角y坐标
            camera_id INTEGER NOT NULL,            -- 关联的摄像头ID
            status TEXT DEFAULT 'empty',           -- 车位状态：empty（空闲）, occupied（占用）
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 最后更新时间
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 创建时间
        )
        ''')
        
        # 创建车位状态历史记录表
        c.execute('''
        CREATE TABLE IF NOT EXISTS parking_spot_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,              -- 关联的车位ID
            status TEXT NOT NULL,                  -- 状态变更：empty（空闲）, occupied（占用）
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 状态变更时间
            FOREIGN KEY (spot_id) REFERENCES parking_spots (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        logging.info("车位数据库初始化成功")
        
    except Exception as e:
        logging.error(f"车位数据库初始化失败: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def update_spot_status(spot_id, status):
    """更新车位状态并记录历史"""
    conn = None
    try:
        conn = get_parking_db_connection() # 使用车位数据库连接
        c = conn.cursor()
        
        # 更新车位状态
        c.execute('''
        UPDATE parking_spots 
        SET status = ?, last_updated = CURRENT_TIMESTAMP 
        WHERE id = ?
        ''', (status, spot_id))
        
        # 记录状态变更历史
        c.execute('''
        INSERT INTO parking_spot_history (spot_id, status)
        VALUES (?, ?)
        ''', (spot_id, status))
        
        conn.commit()
        logging.info(f"车位 {spot_id} 状态更新为 {status}")
        return True
        
    except Exception as e:
        logging.error(f"更新车位状态失败: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# 初始调用，确保两个数据库都已初始化
if __name__ == '__main__':
    init_users_db()
    init_parking_db()