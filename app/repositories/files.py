import base64
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.vault_files import VaultFiles
from app.models.file_chunks import FileChunks
from app.models.vaults import Vaults


def _verify_vault_ownership(db: Session, user_id: str, vault_id: str) -> Vaults:
    vault = db.query(Vaults).filter(
        and_(Vaults.id == vault_id, Vaults.user_id == user_id)
    ).first()
    if not vault:
        raise HTTPException(
            detail="Vault not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return vault


def _verify_file_ownership(db: Session, user_id: str, file_id: str) -> VaultFiles:
    file = db.query(VaultFiles).filter(VaultFiles.id == file_id).first()
    if not file:
        raise HTTPException(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    vault = db.query(Vaults).filter(
        and_(Vaults.id == file.vault_id, Vaults.user_id == user_id)
    ).first()
    if not vault:
        raise HTTPException(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return file


def init_upload(db: Session, user_id: str, vault_id: str, cipher_metadata: str, metadata_nonce: str, size: int) -> VaultFiles:
    _verify_vault_ownership(db, user_id, vault_id)

    if size > 104857600:
        raise HTTPException(
            detail="File exceeds 100MB limit",
            status_code=status.HTTP_413_CONTENT_TOO_LARGE
        )

    file = VaultFiles(
        vault_id=vault_id,
        cipher_metadata=base64.b64decode(cipher_metadata),
        metadata_nonce=base64.b64decode(metadata_nonce),
        size=size,
        status="uploading"
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def add_chunk(db: Session, file_id: str, seq: int, offset: int, length: int, nonce: str, ciphertext: str) -> FileChunks:
    file = db.query(VaultFiles).filter(VaultFiles.id == file_id).first()
    if not file:
        raise HTTPException(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    if file.status != "uploading":
        raise HTTPException(
            detail="Upload already completed",
            status_code=status.HTTP_409_CONFLICT
        )

    existing = db.query(FileChunks).filter(
        and_(FileChunks.file_id == file_id, FileChunks.seq == seq)
    ).first()
    if existing:
        raise HTTPException(
            detail="Chunk seq already exists",
            status_code=status.HTTP_409_CONFLICT
        )

    chunk = FileChunks(
        file_id=file_id,
        seq=seq,
        offset=offset,
        length=length,
        nonce=base64.b64decode(nonce),
        ciphertext=base64.b64decode(ciphertext)
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def complete_upload(db: Session, file_id: str) -> VaultFiles:
    file = db.query(VaultFiles).filter(VaultFiles.id == file_id).first()
    if not file:
        raise HTTPException(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    chunk_count = db.query(FileChunks).filter(FileChunks.file_id == file_id).count()
    if chunk_count == 0:
        raise HTTPException(
            detail="No chunks uploaded",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    from datetime import datetime, UTC
    file.status = "complete"
    file.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(file)
    return file


def get_file(db: Session, file_id: str, user_id: str) -> dict:
    file = _verify_file_ownership(db, user_id, file_id)

    chunk_count = db.query(FileChunks).filter(FileChunks.file_id == file_id).count()

    return {
        "id": file.id,
        "vault_id": file.vault_id,
        "cipher_metadata": base64.b64encode(file.cipher_metadata).decode("utf-8") if file.cipher_metadata else "",
        "metadata_nonce": base64.b64encode(file.metadata_nonce).decode("utf-8") if file.metadata_nonce else "",
        "size": file.size,
        "status": file.status,
        "created_at": file.created_at,
        "completed_at": file.completed_at,
        "chunk_count": chunk_count
    }


def get_chunks(db: Session, file_id: str, user_id: str) -> list[dict]:
    _verify_file_ownership(db, user_id, file_id)

    chunks = db.query(FileChunks).filter(FileChunks.file_id == file_id).order_by(FileChunks.seq).all()

    result = []
    for chunk in chunks:
        result.append({
            "seq": chunk.seq,
            "offset": chunk.offset,
            "length": chunk.length,
            "nonce": base64.b64encode(chunk.nonce).decode("utf-8") if chunk.nonce else "",
            "ciphertext": base64.b64encode(chunk.ciphertext).decode("utf-8") if chunk.ciphertext else ""
        })
    return result


def list_files(db: Session, vault_id: str, user_id: str) -> list[dict]:
    _verify_vault_ownership(db, user_id, vault_id)

    files = db.query(VaultFiles).filter(VaultFiles.vault_id == vault_id).all()

    result = []
    for file in files:
        chunk_count = db.query(FileChunks).filter(FileChunks.file_id == file.id).count()
        result.append({
            "id": file.id,
            "vault_id": file.vault_id,
            "cipher_metadata": base64.b64encode(file.cipher_metadata).decode("utf-8") if file.cipher_metadata else "",
            "metadata_nonce": base64.b64encode(file.metadata_nonce).decode("utf-8") if file.metadata_nonce else "",
            "size": file.size,
            "status": file.status,
            "created_at": file.created_at,
            "completed_at": file.completed_at,
            "chunk_count": chunk_count
        })
    return result


def delete_file(db: Session, file_id: str, user_id: str):
    file = _verify_file_ownership(db, user_id, file_id)
    db.delete(file)
    db.commit()
