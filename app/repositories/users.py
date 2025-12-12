from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import UUID

from app.models.user_settings import UserSettings
from app.repositories.logs import add_new_log
from app.schemas.users import UserConfig
from app.services.actions import *

def initialize_user_settings(db: Session, user_id: UUID, settings: UserConfig):
   user_settings = UserSettings(user_id=user_id, settings=settings.model_dump()) 
   db.add(user_settings)
   db.commit()
   db.refresh(user_settings)
   return user_settings

def get_user_settings_by_id(db: Session, id: str):
    settings = db.query(UserSettings).filter(UserSettings.user_id == id).first()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong token or expired token"
        )
    return settings

def update_settings(db: Session, user_settings: UserSettings, new_settings: UserConfig, ip: str, country: str, city: str, user_agent: str):
    user_settings.settings = new_settings.model_dump()
    db.commit()
    db.refresh(user_settings)
    add_new_log(db, user_id=user_settings.user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.update_user_settings, result=Results.success)
    return user_settings