from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from config.database import Base


class SubscriptionType(Base):
    __tablename__ = "subscription_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_type_id = Column(
        Integer, ForeignKey("subscription_types.id"), nullable=False
    )

    users = relationship("User", back_populates="subscription")
    subscription_type = relationship("SubscriptionType")
