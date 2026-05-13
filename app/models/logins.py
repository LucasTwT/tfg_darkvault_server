import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Logins(Base):
    __tablename__ = "logins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vault_id = Column(UUID(as_uuid=True), ForeignKey("vaults.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False, default="")
    ciphertext = Column(BYTEA, nullable=False)
    nonce = Column(BYTEA, nullable=False)
    
    cipher = Column(String, default="xchacha20poly1305")
    version = Column(String, default="1")

    created_at =  Column(DateTime(timezone=True), server_default=func.now())
    updated_at =  Column(DateTime(timezone=True), server_default=func.now())
    
    vault = relationship("Vaults", back_populates="logins")
    user = relationship("Users")
