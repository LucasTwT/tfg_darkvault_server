from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status
from uuid import UUID
import bcrypt
import os

SECRET_KEY = os.getenv('SECRET_KEY') 
ALGORITHM = os.getenv('ALGORITHM') 
def create_token(data: dict, expires_delta: timedelta | None = None): 
    
    to_encode = data.copy()
    expire =  datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token, keys: list[str]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload[keys[0]] = UUID(payload[keys[0]]) 
        for key in keys:
            if key not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token payload: missing {key}"
                )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def hash_refresh_token(token: str) -> bytes:
    # bcrypt tiene límite de 72 bytes, truncar si es necesario
    token_bytes = token.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(token_bytes, salt)
    return hash