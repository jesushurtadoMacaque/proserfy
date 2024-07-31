from sqlalchemy import Column, Date, Integer, String
from config.database import Base


class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(50), nullable=False)
    release_date = Column(Date, nullable=False, index=True)
