import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

"""
CREATE TABLE sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  refresh_token_hash bytea NOT NULL,  -- si usas refresh tokens
  ip text,
  country text,
  city text,
  user_agent text,

  created_at timestamptz DEFAULT now(),
  last_used timestamptz DEFAULT now(),
  expires_at timestamptz,             -- opcional, TTL de la sesión

  expired boolean DEFAULT false        -- logout o revocación manual
);
"""

class Sessions(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False)

    refresh_token_hash = Column(BYTEA, nullable=False)

    ip = Column(String)
    country = Column(String)
    city = Column(String)
    user_agent = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    expired = Column(Boolean, default=False)

    # relación con User
    user = relationship("Users", back_populates="sessions")
