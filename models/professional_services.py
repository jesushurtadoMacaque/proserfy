from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from config.database import Base

class ProfessionalService(Base):
    __tablename__ = "professional_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False) 
    average_rating = Column(Float, default=0.0)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)

    professional = relationship('User', back_populates='professional_services')
    subcategory = relationship('SubCategory', back_populates='professional_services')
    comments = relationship('Comment', back_populates='professional_service')
    ratings = relationship('Rating', back_populates='professional_service')
    images = relationship('ServiceImage', back_populates='professional_service')  


