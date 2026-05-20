import base64
from fastapi import HTTPException, status

from datetime import datetime, UTC

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.logins import Logins
from app.repositories.auth import add_new_log
from app.schemas.logins import CreateLoginRequest, ModifyLoginRequest
from app.services.actions import Actions, Results

def create_login_by_vault_id(db: Session, user_id: str, vault_id: str, payload: CreateLoginRequest, ip: str, country: str, city: str, user_agent: str):
    new_login = Logins(
        user_id=user_id,
        vault_id=vault_id,
        title=payload.title,
        ciphertext=base64.b64decode(payload.ciphertext),
        nonce=base64.b64decode(payload.nonce),
        cipher=payload.cipher,
        version=str(payload.version),
    )
    db.add(new_login)
    db.commit()
    db.refresh(new_login)
    add_new_log(db, user_id=user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.new_login, result=Results.success)
    return new_login

def get_all_logins_by_vault_id(db: Session, user_id: str, vault_id: str):
    logins = db.query(Logins).filter(and_(Logins.user_id == user_id, Logins.vault_id == vault_id)).all()
    # Convert BYTEA to base64 strings for JSON response
    result = []
    for login in logins:
        result.append({
            "id": login.id,
            "vault_id": login.vault_id,
            "title": login.title or "",
            "ciphertext": base64.b64encode(login.ciphertext).decode("utf-8") if login.ciphertext else "",
            "nonce": base64.b64encode(login.nonce).decode("utf-8") if login.nonce else "",
            "cipher": login.cipher,
            "version": login.version,
            "created_at": login.created_at,
            "updated_at": login.updated_at,
        })
    return result

def modify_login(db: Session, user_id: str, payload: ModifyLoginRequest, ip: str, country: str, city: str, user_agent: str):
    data = payload.new_data
    login = db.query(Logins).filter(and_(Logins.user_id == user_id, Logins.vault_id == data.vault_id, Logins.id == data.id)).first()
    if not login:
        raise HTTPException(detail="Wrong data", status_code=status.HTTP_404_NOT_FOUND)
    login.title = data.title if hasattr(data, 'title') else login.title
    login.ciphertext = base64.b64decode(data.ciphertext) if isinstance(data.ciphertext, str) else data.ciphertext
    login.nonce = base64.b64decode(data.nonce) if isinstance(data.nonce, str) else data.nonce
    login.cipher = data.cipher
    login.version = data.version    
    login.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(login)
    add_new_log(db, user_id=user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.modify_login, result=Results.success)
    return login

def delete_login(db: Session, user_id: str, vault_id: str, login_id: str,
                       ip: str, country: str, city: str, user_agent: str):

    vault = db.query(Logins).filter(
        and_(Logins.user_id == user_id, Logins.vault_id == vault_id, Logins.id == login_id)
    ).first()

    if not vault:
        raise HTTPException(
            detail="Wrong data",
            status_code=status.HTTP_404_NOT_FOUND
        )

    db.delete(vault)
    db.commit()

    add_new_log(
        db, user_id=user_id,
        ip=ip, country=country, city=city, user_agent=user_agent,
        action=Actions.delete_login,
        result=Results.success
    )
