from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

"""
CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  username text UNIQUE NOT NULL,
  auth_hash text NOT NULL,
  auth_salt text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
"""

class Users(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Zero-knowledge auth
    auth_verifier = Column(String, nullable=False)   # base64(HMAC(auth_key, "verifier"))
    kdf_salt = Column(String, nullable=False)        # base64
    kdf_params = Column(JSON, nullable=False)        # Argon2 params

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # --- Relaciones (bidireccionales)
    challenges = relationship(
        "LoginChallenges",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete")
    sessions = relationship("Sessions", back_populates="user", cascade="all, delete")
    vaults = relationship("Vaults", back_populates="user", cascade="all, delete")
    ip_blocks = relationship("IPBlockList", back_populates="user", cascade="all, delete")
    audit_logs = relationship("AuditLogs", back_populates="user", cascade="all, delete")
    
    logins = relationship("Logins", back_populates="user", cascade="all, delete")
