from sqlalchemy import Column, Integer, String, DateTime
from config.database import Base
from datetime import datetime, timezone

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(1024), index=True, unique=True)
    revoked_at = Column(DateTime, default=datetime.now(timezone.utc))
