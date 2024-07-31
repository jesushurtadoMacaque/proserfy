from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from config.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    professional_service_id = Column(
        Integer, ForeignKey("professional_services.id"), nullable=False
    )

    user = relationship("User", back_populates="ratings")
    professional_service = relationship("ProfessionalService", back_populates="ratings")
