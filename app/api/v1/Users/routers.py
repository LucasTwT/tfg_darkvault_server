from fastapi import APIRouter, status, Depends

from app.schemas.users import *
from app.core.tokens import decode_token
from app.core.constants import ENCODE_JWT_USERDATA
from app.db.conect_db import get_db
from app.utils.get_user_context import get_user_context
from app.repositories.users import *
from app.core.ip_management import *

from sqlalchemy.orm import Session

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.post('/get', response_model=GetUserSettingsResponse, status_code=status.HTTP_200_OK)
def get_user_settings(ctx = Depends(get_user_context)):
    user_settings = get_user_settings_by_id(ctx["db"], ctx["user_id"])
    return GetUserSettingsResponse(settings=user_settings.settings, username=ctx["username"], email=ctx["email"])
    
@router.post('/update', response_model=SetUserSettingsResponse, status_code=status.HTTP_201_CREATED)
def update_user_settings(payload: SetUserSettingsRequest, ctx = Depends(get_user_context)):
    settings = get_user_settings_by_id(ctx["db"], ctx["user_id"])
    new_settings = update_settings(ctx["db"], user_settings=settings, new_settings=payload.settings,  ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return SetUserSettingsResponse(status=True)