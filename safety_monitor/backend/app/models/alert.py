from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    zone_id = Column(Integer, ForeignKey("zones.id"))
    alert_type = Column(String, nullable=False)
    level = Column(String, nullable=False)
    image_url = Column(String)
    is_handled = Column(Boolean, default=False)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    camera = relationship("Camera", back_populates="alerts")
    zone = relationship("Zone", back_populates="alerts")
    handler = relationship("User", back_populates="alerts")
