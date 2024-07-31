from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base


class ServiceImage(Base):
    __tablename__ = "service_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    service_id = Column(Integer, ForeignKey("professional_services.id"), nullable=False)

    professional_service = relationship("ProfessionalService", back_populates="images")
