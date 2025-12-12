from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

"""
CREATE TABLE ip_blocklist (
  id bigserial PRIMARY KEY,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  ip text NOT NULL,
  reason text,
  created_at timestamptz DEFAULT now()
);
"""

class IPBlockList(Base):
    __tablename__ = "ip_blocklist"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    ip = Column(String, nullable=False)
    reason = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="ip_blocks")
