import base64
import uuid
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.repositories.files import (
    init_upload,
    add_chunk,
    complete_upload,
    get_file,
    get_chunks,
    list_files,
    delete_file,
)


def _b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _mock_db():
    return MagicMock()


def _mock_vault(vault_id=None, user_id=None):
    vault = MagicMock()
    vault.id = vault_id or uuid.uuid4()
    vault.user_id = user_id or uuid.uuid4()
    return vault


def _mock_file(file_id=None, vault_id=None, status="uploading"):
    f = MagicMock()
    f.id = file_id or uuid.uuid4()
    f.vault_id = vault_id or uuid.uuid4()
    f.cipher_metadata = b"encrypted_meta"
    f.metadata_nonce = b"meta_nonce"
    f.size = 1024
    f.status = status
    f.created_at = datetime.now(UTC)
    f.completed_at = None
    return f


def _mock_chunk(seq=0):
    c = MagicMock()
    c.seq = seq
    c.offset = seq * 65536
    c.length = 65536
    c.nonce = b"nonce_bytes"
    c.ciphertext = b"ciphertext_bytes"
    return c


# ─── init_upload ──────────────────────────────────────────────────────


class TestInitUpload:
    def test_successful_init(self):
        db = _mock_db()
        vault = _mock_vault()
        db.query().filter().first.return_value = vault

        result = init_upload(
            db=db,
            user_id=str(vault.user_id),
            vault_id=str(vault.id),
            cipher_metadata=_b64("meta"),
            metadata_nonce=_b64("nonce"),
            size=1024
        )

        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_vault_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            init_upload(
                db=db,
                user_id=str(uuid.uuid4()),
                vault_id=str(uuid.uuid4()),
                cipher_metadata=_b64("meta"),
                metadata_nonce=_b64("nonce"),
                size=1024
            )
        assert exc_info.value.status_code == 404

    def test_size_exceeds_limit(self):
        db = _mock_db()
        vault = _mock_vault()
        db.query().filter().first.return_value = vault

        with pytest.raises(HTTPException) as exc_info:
            init_upload(
                db=db,
                user_id=str(vault.user_id),
                vault_id=str(vault.id),
                cipher_metadata=_b64("meta"),
                metadata_nonce=_b64("nonce"),
                size=104857601
            )
        assert exc_info.value.status_code == 413


# ─── add_chunk ────────────────────────────────────────────────────────


class TestAddChunk:
    def test_successful_add(self):
        db = _mock_db()
        file = _mock_file()
        db.query().filter().first.side_effect = [file, None]

        result = add_chunk(
            db=db,
            file_id=str(file.id),
            seq=0,
            offset=0,
            length=65536,
            nonce=_b64("nonce"),
            ciphertext=_b64("cipher")
        )

        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_duplicate_seq(self):
        db = _mock_db()
        file = _mock_file()
        existing_chunk = _mock_chunk(seq=0)
        db.query().filter().first.side_effect = [file, existing_chunk]

        with pytest.raises(HTTPException) as exc_info:
            add_chunk(
                db=db,
                file_id=str(file.id),
                seq=0,
                offset=0,
                length=65536,
                nonce=_b64("nonce"),
                ciphertext=_b64("cipher")
            )
        assert exc_info.value.status_code == 409
        assert "Chunk seq already exists" in str(exc_info.value.detail)

    def test_upload_already_complete(self):
        db = _mock_db()
        file = _mock_file(status="complete")
        db.query().filter().first.return_value = file

        with pytest.raises(HTTPException) as exc_info:
            add_chunk(
                db=db,
                file_id=str(file.id),
                seq=0,
                offset=0,
                length=65536,
                nonce=_b64("nonce"),
                ciphertext=_b64("cipher")
            )
        assert exc_info.value.status_code == 409
        assert "Upload already completed" in str(exc_info.value.detail)

    def test_file_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            add_chunk(
                db=db,
                file_id=str(uuid.uuid4()),
                seq=0,
                offset=0,
                length=65536,
                nonce=_b64("nonce"),
                ciphertext=_b64("cipher")
            )
        assert exc_info.value.status_code == 404


# ─── complete_upload ──────────────────────────────────────────────────


class TestCompleteUpload:
    def test_successful_complete(self):
        db = _mock_db()
        file = _mock_file()
        db.query().filter().first.return_value = file
        db.query().filter().count.return_value = 3

        result = complete_upload(db=db, file_id=str(file.id))

        assert file.status == "complete"
        assert file.completed_at is not None
        db.commit.assert_called_once()

    def test_no_chunks(self):
        db = _mock_db()
        file = _mock_file()
        db.query().filter().first.return_value = file
        db.query().filter().count.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            complete_upload(db=db, file_id=str(file.id))
        assert exc_info.value.status_code == 400
        assert "No chunks uploaded" in str(exc_info.value.detail)

    def test_file_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            complete_upload(db=db, file_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404


# ─── get_file ─────────────────────────────────────────────────────────


class TestGetFile:
    def test_successful_get(self):
        db = _mock_db()
        file = _mock_file()
        vault = _mock_vault(vault_id=file.vault_id)

        # First call: file lookup, second call: vault ownership
        db.query().filter().first.side_effect = [file, vault]
        db.query().filter().count.return_value = 3

        result = get_file(db=db, file_id=str(file.id), user_id=str(vault.user_id))

        assert result["id"] == file.id
        assert result["status"] == "uploading"
        assert result["chunk_count"] == 3

    def test_file_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_file(db=db, file_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404

    def test_wrong_user(self):
        db = _mock_db()
        file = _mock_file()
        db.query().filter().first.side_effect = [file, None]

        with pytest.raises(HTTPException) as exc_info:
            get_file(db=db, file_id=str(file.id), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404


# ─── get_chunks ───────────────────────────────────────────────────────


class TestGetChunks:
    def test_successful_get(self):
        db = _mock_db()
        file = _mock_file()
        vault = _mock_vault(vault_id=file.vault_id)
        chunks = [_mock_chunk(i) for i in range(3)]

        db.query().filter().first.side_effect = [file, vault]
        db.query().filter().order_by().all.return_value = chunks

        result = get_chunks(db=db, file_id=str(file.id), user_id=str(vault.user_id))

        assert len(result) == 3

    def test_file_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_chunks(db=db, file_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404


# ─── list_files ───────────────────────────────────────────────────────


class TestListFiles:
    def test_successful_list(self):
        db = _mock_db()
        vault = _mock_vault()
        files = [_mock_file(vault_id=vault.id) for _ in range(2)]

        db.query().filter().first.return_value = vault
        db.query().filter().all.return_value = files
        db.query().filter().count.return_value = 5

        result = list_files(db=db, vault_id=str(vault.id), user_id=str(vault.user_id))

        assert len(result) == 2

    def test_empty_vault(self):
        db = _mock_db()
        vault = _mock_vault()

        db.query().filter().first.return_value = vault
        db.query().filter().all.return_value = []

        result = list_files(db=db, vault_id=str(vault.id), user_id=str(vault.user_id))

        assert len(result) == 0

    def test_vault_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            list_files(db=db, vault_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404


# ─── delete_file ──────────────────────────────────────────────────────


class TestDeleteFile:
    def test_successful_delete(self):
        db = _mock_db()
        file = _mock_file()
        vault = _mock_vault(vault_id=file.vault_id)

        db.query().filter().first.side_effect = [file, vault]

        delete_file(db=db, file_id=str(file.id), user_id=str(vault.user_id))

        db.delete.assert_called_once_with(file)
        db.commit.assert_called_once()

    def test_file_not_found(self):
        db = _mock_db()
        db.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_file(db=db, file_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404

    def test_wrong_user_delete(self):
        db = _mock_db()
        file = _mock_file()
        db.query().filter().first.side_effect = [file, None]

        with pytest.raises(HTTPException) as exc_info:
            delete_file(db=db, file_id=str(file.id), user_id=str(uuid.uuid4()))
        assert exc_info.value.status_code == 404
