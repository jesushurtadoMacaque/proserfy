from sqlalchemy import ARRAY, Boolean, Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from datetime import date
from config.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    subcategories = relationship('SubCategory', back_populates='category')

class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Category', back_populates='subcategories')
    professional_services = relationship('ProfessionalService', back_populates='subcategory')

class ServiceImage(Base):
    __tablename__ = "service_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    service_id = Column(Integer, ForeignKey('professional_services.id'), nullable=False)

    professional_service = relationship('ProfessionalService', back_populates='images')

class ProfessionalService(Base):
    __tablename__ = "professional_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    #image_urls = Column(ARRAY(String), nullable=True)  
    location = Column(String(100), nullable=False)
    average_rating = Column(Float, default=0.0)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)

    professional = relationship('User', back_populates='professional_services')
    subcategory = relationship('SubCategory', back_populates='professional_services')
    comments = relationship('Comment', back_populates='professional_service')
    ratings = relationship('Rating', back_populates='professional_service')
    images = relationship('ServiceImage', back_populates='professional_service')  

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    professional_service_id = Column(Integer, ForeignKey('professional_services.id'), nullable=False)

    user = relationship('User', back_populates='comments')
    professional_service = relationship('ProfessionalService', back_populates='comments')

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    professional_service_id = Column(Integer, ForeignKey('professional_services.id'), nullable=False)

    user = relationship('User', back_populates='ratings')
    professional_service = relationship('ProfessionalService', back_populates='ratings')