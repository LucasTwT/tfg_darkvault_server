from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from app.db.base import Base

"""
CREATE TABLE vaults (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name text NOT NULL,
  settings jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
"""

class Vaults(Base):
    __tablename__ = "vaults"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    settings = Column(JSONB, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="vaults")
    files = relationship("VaultFiles", back_populates="vault", cascade="all, delete")
    logins = relationship("Logins", back_populates="vault", cascade="all, delete")