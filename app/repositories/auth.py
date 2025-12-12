from fastapi import HTTPException, status

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

import bcrypt

from app.core.security_passwords import auth_key_context
from app.repositories.logs import add_new_log
from app.repositories.users import initialize_user_settings
from app.services.actions import Actions, Results
from app.schemas.users import UserConfig

from datetime import datetime, UTC, timedelta

from app.models.users import Users
from app.models.sessions import Sessions

def verify_user(db: Session, email: str, username: str):
    existing_user = db.query(Users).filter(
         or_(Users.email == email, Users.username == username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already in use"
        )
    return existing_user

def get_auth_salt(db: Session, identifier: str, ip: str, user_agent: str, country: str, city: str):
    existing_user = db.query(Users).filter(
        or_(Users.email == identifier.lower(), Users.username == identifier)
    ).first()
    
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ivalid credentials"
        )
    add_new_log(db, user_id=existing_user.id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.get_salt, result=Results.success)
    return existing_user.auth_salt


def add_user_to_db(db: Session, username: str, email: str, auth_hash: str, salt: str, default_settings: UserConfig ,ip: str, user_agent: str, country: str, city: str):
    user = Users(
        username=username,
        email=email.lower(),
        auth_hash=auth_hash,
        auth_salt=salt
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    initialize_user_settings(db, user_id=user.id, settings=default_settings)
    
    add_new_log(db, user_id=user.id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.create_user, result=Results.success)
    return user

def add_record_in_sessions(db: Session, user_id: str, ip: str, refresh_token_hash: bytes, country: str, city: str, user_agent: str, expires_at: timedelta = timedelta(days=30)):
    session = Sessions(user_id=user_id, refresh_token_hash=refresh_token_hash, ip=ip, country=country, city=city, user_agent=user_agent, expires_at= datetime.now(UTC) + expires_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    add_new_log(db, user_id=session.user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.create_session, result=Results.success)
    return session

def verify_login_data(db: Session, identifier: str, auth_key: str, ip: str, country: str, city: str, user_agent: str):
    user = db.query(Users).filter(
    or_(Users.email == identifier.lower(), Users.username == identifier)
    ).first()

    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
        )

    # Comparación del hash_key con el hash_key previamente hasheado
    if not auth_key_context.verify(auth_key, user.auth_hash):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

    add_new_log(db, user_id=user.id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.log_in_account, result=Results.success)
    return user


def verify_refresh_token(db: Session, refresh_token: str, id: str):
    sessions = db.query(Sessions).filter(
        and_(or_(Sessions.expired == False,
        Sessions.expires_at > datetime.now(UTC)), Sessions.user_id == id)
    ).all()
    for session in sessions:
        try:
            if bcrypt.checkpw(refresh_token.encode(), session.refresh_token_hash):
                return session
        except Exception:
            continue 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid or expired token"
    )


def get_user_data(db: Session, id):
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token or your token has expired"
        )
    return user

def update_last_used(db: Session, session: Sessions):
    session.last_used = datetime.now(UTC)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def logout_session(db: Session, session: Sessions, ip: str, country: str, city: str, user_agent: str):
    session.expired = True
    db.add(session)
    db.commit()
    db.refresh(session)
    add_new_log(db, user_id=session.user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.logout, result=Results.success)
    return session