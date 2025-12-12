from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

"""
CREATE TABLE audit_logs (
  id bigserial PRIMARY KEY,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  ip text,
  country text,
  city text,
  user_agent text,
  action text NOT NULL,
  result text NOT NULL,
  timestamp timestamptz DEFAULT now()
);
"""

class AuditLogs(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    ip = Column(String)
    country = Column(String)
    city = Column(String)
    user_agent = Column(String)

    action = Column(String, nullable=False)
    result = Column(String, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="audit_logs")
