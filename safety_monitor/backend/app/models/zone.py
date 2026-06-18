from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    coordinates = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cameras = relationship("Camera", back_populates="zone")
    alerts = relationship("Alert", back_populates="zone")
