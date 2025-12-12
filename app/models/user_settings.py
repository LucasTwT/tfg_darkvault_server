from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    settings = Column(JSONB, nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )

    # 1 - 1 Respecto al modelo Users
    user = relationship("Users", back_populates="settings")
