from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class InitUploadRequest(BaseModel):
    cipher_metadata: str
    metadata_nonce: str
    size: int


class InitUploadResponse(BaseModel):
    status: bool
    upload_id: UUID4


class ChunkUploadRequest(BaseModel):
    seq: int
    offset: int
    length: int
    nonce: str
    ciphertext: str


class ChunkUploadResponse(BaseModel):
    status: bool
    seq: int


class CompleteUploadResponse(BaseModel):
    status: bool
    file_id: UUID4


class FileMetadata(BaseModel):
    id: UUID4
    vault_id: UUID4
    cipher_metadata: str
    metadata_nonce: str
    size: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    chunk_count: int


class FileListResponse(BaseModel):
    status: bool
    files: list[FileMetadata]


class FileChunkData(BaseModel):
    seq: int
    offset: int
    length: int
    nonce: str
    ciphertext: str


class FileChunksResponse(BaseModel):
    status: bool
    chunks: list[FileChunkData]


class DeleteFileStartResponse(BaseModel):
    salt: str
    kdf_params: dict
    challenge: str


class DeleteFileFinishRequest(BaseModel):
    signature: str


class DeleteFileResponse(BaseModel):
    status: bool
