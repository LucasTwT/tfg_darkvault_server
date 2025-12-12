from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

"""
CREATE TABLE file_chunks (
  id bigserial PRIMARY KEY,
  file_id uuid NOT NULL REFERENCES vault_files(id) ON DELETE CASCADE,
  seq int NOT NULL,                            -- 0,1,2,...
  offset bigint NOT NULL,                      -- offset original en el archivo
  length int NOT NULL,                         -- tamaño ciphertext
  nonce bytea NOT NULL,                        -- nonce único por chunk
  ciphertext bytea NOT NULL,                   -- datos cifrados del chunk
  received_at timestamptz DEFAULT now(),
  UNIQUE(file_id, seq)
);
"""

class FileChunks(Base):
    __tablename__ = "file_chunks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    file_id = Column(UUID(as_uuid=True), ForeignKey("vault_files.id", ondelete="CASCADE"), nullable=False)

    seq = Column(Integer, nullable=False)
    offset = Column(BigInteger, nullable=False)
    length = Column(Integer, nullable=False)

    nonce = Column(BYTEA, nullable=False)
    ciphertext = Column(BYTEA, nullable=False)

    received_at = Column(DateTime(timezone=True), server_default=func.now())

    file = relationship("VaultFiles", back_populates="chunks")
