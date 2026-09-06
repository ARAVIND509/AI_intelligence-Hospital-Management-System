from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    appointments = relationship("Appointment", back_populates="doctor")