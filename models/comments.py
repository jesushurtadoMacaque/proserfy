from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from config.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    professional_service_id = Column(
        Integer, ForeignKey("professional_services.id"), nullable=False
    )

    user = relationship("User", back_populates="comments")
    professional_service = relationship(
        "ProfessionalService", back_populates="comments"
    )
