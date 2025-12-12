from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session

from app.schemas.logs import *
from app.repositories.logs import *
from app.utils.get_user_context import get_user_context
from app.core.tokens import decode_token
from app.core.constants import ENCODE_JWT_USERDATA

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.post("/get", response_model=LogsResponse, status_code=status.HTTP_200_OK)
def get_logs(ctx = Depends(get_user_context)):
    logs = get_logs_by_user_id(ctx["db"], ctx["user_id"])
    return LogsResponse(status=True, logs=logs)