from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base


class ProfileImage(Base):
    __tablename__ = "profile_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="profile_image")
