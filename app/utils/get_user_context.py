from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db.conect_db import get_db

from app.core.ip_management import *
from app.core.tokens import decode_token
from app.core.constants import ENCODE_JWT_USERDATA

def get_user_context(request: Request, db:Session = Depends(get_db)):
    ip = get_client_ip(request=request)
    user_agent = get_user_agent(request=request)
    country, city = get_location_by_ip(ip)
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = auth_header.split(" ")[1]
    data = decode_token(token, ENCODE_JWT_USERDATA)
    
    return {
        "db": db,
        "user_id": data["id"],
        "username": data["username"],
        "email": data["email"],
        "ip": ip,
        "city": city,
        "country": country,
        "agent": user_agent
    }