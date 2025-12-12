import uuid
from sqlalchemy import Column, DateTime, String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

"""
CREATE TABLE vault_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vault_id uuid NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
  upload_id uuid UNIQUE,                     -- para uploads resumibles
  cipher_metadata bytea NOT NULL,            -- (filename, mimetype, notes, tags) cifrado
  metadata_nonce bytea NOT NULL,             -- nonce de los metadatos
  size bigint,                               -- tamaño original del archivo
  status text NOT NULL DEFAULT 'uploading',  -- uploading | complete | failed
  created_at timestamptz DEFAULT now(),
  completed_at timestamptz
);
"""

class VaultFiles(Base):
    __tablename__ = "vault_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    vault_id = Column(UUID(as_uuid=True), ForeignKey("vaults.id", ondelete="CASCADE"), nullable=False)

    upload_id = Column(UUID(as_uuid=True), unique=True)

    cipher_metadata = Column(BYTEA, nullable=False)
    metadata_nonce = Column(BYTEA, nullable=False)

    size = Column(BigInteger)
    status = Column(String, default="uploading")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime)

    vault = relationship("Vaults", back_populates="files")
    chunks = relationship("FileChunks", back_populates="file", cascade="all, delete")
