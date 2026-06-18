"""数据库初始化脚本"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, get_db
from app.models.user import User
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.alert import Alert
from sqlalchemy.orm import Session

def init_db():
    # 创建所有表
    User.__table__.create(bind=engine, checkfirst=True)
    Camera.__table__.create(bind=engine, checkfirst=True)
    Zone.__table__.create(bind=engine, checkfirst=True)
    Alert.__table__.create(bind=engine, checkfirst=True)
    print("数据库表创建成功")

    # 添加默认管理员用户（如果不存在）
    db: Session = next(get_db())
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        from app.core.security import get_password_hash
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("默认管理员用户创建成功: admin/admin123")
    db.close()

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")