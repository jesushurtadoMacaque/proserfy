from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, Time
from sqlalchemy.orm import relationship
from config.database import Base

class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String(9), nullable=False)  # e.g., 'Monday', 'Tuesday', etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    professional_service_id = Column(Integer, ForeignKey("professional_services.id"), nullable=False)

    professional_service = relationship("ProfessionalService", back_populates="work_schedules")



class ProfessionalService(Base):
    __tablename__ = "professional_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    range_from = Column(Integer, nullable=False)
    range_to = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    average_rating = Column(Float, default=0.0)
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)

    work_schedules = relationship("WorkSchedule", back_populates="professional_service")
    professional = relationship("User", back_populates="professional_services")
    subcategory = relationship("SubCategory", back_populates="professional_services")
    comments = relationship("Comment", back_populates="professional_service")
    ratings = relationship("Rating", back_populates="professional_service")
    images = relationship("ServiceImage", back_populates="professional_service")
