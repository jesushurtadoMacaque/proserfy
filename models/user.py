from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import date
from config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=True)
    receive_promotions = Column(Boolean, default=False)
    apple_id = Column(String(255), unique=True, nullable=True)
    facebook_id = Column(String(255), unique=True, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    birth_date = Column(Date, nullable=True)  
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Role', back_populates='users')
    professional_services = relationship('ProfessionalService', back_populates='professional')
    comments = relationship('Comment', back_populates='user')
    ratings = relationship('Rating', back_populates='user')

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship('User', back_populates='role')
