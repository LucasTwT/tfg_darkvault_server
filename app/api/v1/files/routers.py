from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.files import *
from app.utils.get_user_context import get_user_context

from app.repositories.files import (
    init_upload,
    add_chunk,
    complete_upload,
    get_file,
    get_chunks,
    list_files,
    delete_file,
)
from app.repositories.auth import create_challenge, get_user_data, consume_challenge, verify_challenge_signature

router = APIRouter(prefix="/file", tags=["file"])


@router.post('/upload/init', response_model=InitUploadResponse, status_code=status.HTTP_201_CREATED)
def init_file_upload(vault_id: str, payload: InitUploadRequest, ctx=Depends(get_user_context)):
    file = init_upload(
        db=ctx["db"],
        user_id=ctx["user_id"],
        vault_id=vault_id,
        cipher_metadata=payload.cipher_metadata,
        metadata_nonce=payload.metadata_nonce,
        size=payload.size
    )
    return InitUploadResponse(status=True, upload_id=file.id)


@router.post('/upload/{upload_id}/chunk', response_model=ChunkUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_chunk(upload_id: str, payload: ChunkUploadRequest, ctx=Depends(get_user_context)):
    chunk = add_chunk(
        db=ctx["db"],
        file_id=upload_id,
        seq=payload.seq,
        offset=payload.offset,
        length=payload.length,
        nonce=payload.nonce,
        ciphertext=payload.ciphertext
    )
    return ChunkUploadResponse(status=True, seq=chunk.seq)


@router.post('/upload/{upload_id}/complete', response_model=CompleteUploadResponse, status_code=status.HTTP_200_OK)
def complete_file_upload(upload_id: str, ctx=Depends(get_user_context)):
    file = complete_upload(db=ctx["db"], file_id=upload_id)
    return CompleteUploadResponse(status=True, file_id=file.id)


@router.get('/vault/{vault_id}', response_model=FileListResponse, status_code=status.HTTP_200_OK)
def list_vault_files(vault_id: str, ctx=Depends(get_user_context)):
    files = list_files(db=ctx["db"], vault_id=vault_id, user_id=ctx["user_id"])
    return FileListResponse(status=True, files=files)


@router.get('/{file_id}', response_model=FileMetadata, status_code=status.HTTP_200_OK)
def get_file_metadata(file_id: str, ctx=Depends(get_user_context)):
    return get_file(db=ctx["db"], file_id=file_id, user_id=ctx["user_id"])


@router.get('/{file_id}/chunks', response_model=FileChunksResponse, status_code=status.HTTP_200_OK)
def get_file_chunks(file_id: str, ctx=Depends(get_user_context)):
    chunks = get_chunks(db=ctx["db"], file_id=file_id, user_id=ctx["user_id"])
    return FileChunksResponse(status=True, chunks=chunks)


@router.delete('/start', response_model=DeleteFileStartResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_file_start(ctx=Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = create_challenge(ctx["db"], user=user)
    return DeleteFileStartResponse(
        salt=user.kdf_salt,
        kdf_params=user.kdf_params,
        challenge=challenge.challenge
    )


@router.delete('/{file_id}/finish', response_model=DeleteFileResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_file_finish(file_id: str, payload: DeleteFileFinishRequest, ctx=Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = consume_challenge(db=ctx["db"], user_id=user.id)

    if not verify_challenge_signature(user.auth_verifier, challenge.challenge, payload.signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    delete_file(db=ctx["db"], file_id=file_id, user_id=user.id)
    return DeleteFileResponse(status=True)
