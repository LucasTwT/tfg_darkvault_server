from fastapi import HTTPException, status

from datetime import datetime, UTC

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.logins import Logins
from app.repositories.auth import add_new_log
from app.schemas.logins import CreateLoginRequest, ModifyLoginRequest
from app.services.actions import Actions, Results

def create_login_by_vault_id(db: Session, user_id: str, vault_id: str, payload: CreateLoginRequest, ip: str, country: str, city: str, user_agent: str):
    new_login = Logins(user_id=user_id, vault_id=vault_id, ciphertext=payload.ciphertext, nonce=payload.nonce, cipher=payload.cipher, version=payload.version)
    db.add(new_login)
    db.commit()
    db.refresh(new_login)
    add_new_log(db, user_id=user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.new_login, result=Results.success)
    return new_login

def get_all_logins_by_vault_id(db: Session, user_id: str, vault_id: str):
    logins = db.query(Logins).filter(and_(Logins.user_id == user_id, Logins.vault_id == vault_id)).all()
    print(logins)
    return logins

def modify_login(db: Session, user_id: str, payload: ModifyLoginRequest, ip: str, country: str, city: str, user_agent: str):
    data = payload.new_data
    login = db.query(Logins).filter(and_(Logins.user_id == user_id, Logins.vault_id == data.vault_id, Logins.id == data.id)).first()
    if not login:
        raise HTTPException(detail="Wrong data", status_code=status.HTTP_404_NOT_FOUND)
    login.ciphertext = data.ciphertext
    login.nonce = data.nonce
    login.cipher = data.cipher
    login.version = data.version    
    login.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(login)
    add_new_log(db, user_id=user_id,ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.modify_login, result=Results.success)
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