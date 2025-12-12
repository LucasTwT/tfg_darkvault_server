import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

"""
CREATE TABLE logins (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vault_id uuid NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
  ciphertext bytea NOT NULL,
  nonce bytea NOT NULL,
  cipher text NOT NULL DEFAULT 'xchacha20poly1305',
  version text NOT NULL DEFAULT '1',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
"""

class Logins(Base):
    __tablename__ = "logins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    vault_id = Column(UUID(as_uuid=True), ForeignKey("vaults.id", ondelete="CASCADE"), nullable=False)

    ciphertext = Column(BYTEA, nullable=False)
    nonce = Column(BYTEA, nullable=False)
    
    cipher = Column(String, default="xchacha20poly1305")
    version = Column(String, default="1")

    created_at =  Column(DateTime(timezone=True), server_default=func.now())
    updated_at =  Column(DateTime(timezone=True), server_default=func.now())
    
    vault = relationship("Vaults", back_populates="logins")