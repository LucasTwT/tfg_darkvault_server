from fastapi import APIRouter, status, Depends, Request, Response

from app.schemas.auth import *
from app.core.tokens import create_token, decode_token, hash_refresh_token
from app.core.security_passwords import auth_key_context
from app.core.constants import ENCODE_REFRESH_TOKEN
from app.core.ip_management import get_client_ip, get_user_agent, get_location_by_ip
from app.core.cookie import set_refresh_token_cookie, clear_refresh_token_cookie, REFRESH_TOKEN_COOKIE_NAME
from app.db.conect_db import get_db
from app.utils.get_user_context import get_user_context

from sqlalchemy.orm import Session
router = APIRouter(prefix="/auth", tags=["Authentication"])


from app.repositories.auth import *

from datetime import timedelta

@router.post("/verify_token", response_model=TokenVerifyResponse, status_code=status.HTTP_200_OK)
def verify_jwt(ctx = Depends(get_user_context)):
    return TokenVerifyResponse(status=True)
    
@router.post("/request_salt", response_model=SaltResponse, status_code=status.HTTP_200_OK)
def get_salt(payload: SaltRequest, request: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(request=request)
    user_agent = get_user_agent(request=request)
    country, city = get_location_by_ip(ip)
    salt = get_auth_salt(db, payload.identifier, ip, user_agent, country, city)
    return SaltResponse(salt=salt)

@router.post("/register/user", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = verify_user(db, payload.email, payload.username)

    if not user:
        ip = get_client_ip(request=request)
        user_agent = get_user_agent(request=request)
        country, city = get_location_by_ip(ip)
        created_user = add_user_to_db(db, username=payload.username, email=payload.email, public_key=payload.public_key, params=payload.kdf_params, salt=payload.auth_salt, default_settings=payload.default_settings,ip=ip, user_agent=user_agent, country=country, city=city)
        access_token = create_token({"id": str(created_user.id), "username": payload.username, "email": payload.email})
        refresh_token = create_token({"session": True, "user_id": str(created_user.id)}, expires_delta=timedelta(days=30))
        session = add_record_in_sessions(db, created_user.id, ip, hash_refresh_token(refresh_token), country, city, user_agent)
        
        # Set refresh token as HttpOnly cookie
        set_refresh_token_cookie(response, refresh_token)
        
        return RegisterResponse(access_token=access_token)

@router.post("/login/start", response_model=LoginStartResponse, status_code=status.HTTP_200_OK)
def login_user(payload: LoginStartRequest, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db=db, identifier=payload.identifier)
    challenge = create_challenge(db=db, user=user)
    return LoginStartResponse (
        salt=user.kdf_salt,
        kdf_params=user.kdf_params,
        challenge=challenge.challenge
    )

@router.post("/login/finish", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login_user(payload: LoginFinishRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db=db, identifier=payload.identifier)
    challenge = consume_challenge(db=db, user_id=user.id)
    if not verify_challenge_signature(user.auth_verifier, challenge.challenge, payload.signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    ip = get_client_ip(request=request)
    user_agent = get_user_agent(request=request)
    country, city = get_location_by_ip(ip)
    
    access_token = create_token({"id": str(user.id), "username": user.username, "email": user.email})
    refresh_token = create_token({"session": True, "user_id": str(user.id)}, expires_delta=timedelta(days=30))
    session = add_record_in_sessions(db, user.id, ip, hash_refresh_token(refresh_token), country, city, user_agent)
    
    # Set refresh token as HttpOnly cookie
    set_refresh_token_cookie(response, refresh_token)
    
    return LoginResponse (
        access_token=access_token,
    )

@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_201_CREATED)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    # Read refresh token from cookie
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token in cookie")
    
    try:
        # Decode and validate
        data = decode_token(refresh_token, ENCODE_REFRESH_TOKEN)
        session = verify_refresh_token(db=db, refresh_token=refresh_token, id=data["user_id"])
        user = get_user_data(db=db, id=session.user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Refresh failed: {str(e)}")
    
    # Rotation: invalidate old session, create new tokens
    invalidate_session(db, session)
    
    new_access_token = create_token({"id": str(user.id), "username": user.username, "email": user.email})
    new_refresh_token = create_token({"session": True, "user_id": str(user.id)}, expires_delta=timedelta(days=30))
    
    ip = get_client_ip(request=request)
    user_agent = get_user_agent(request=request)
    country, city = get_location_by_ip(ip)
    add_record_in_sessions(db, user.id, ip, hash_refresh_token(new_refresh_token), country, city, user_agent)
    
    # Set new rotated refresh token cookie
    set_refresh_token_cookie(response, new_refresh_token)
    
    return RefreshResponse(access_token=new_access_token)
    
@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if refresh_token:
        try:
            data = decode_token(refresh_token, ENCODE_REFRESH_TOKEN)
            session = verify_refresh_token(db, refresh_token=refresh_token, id=data["user_id"])
            ip = get_client_ip(request=request)
            user_agent = get_user_agent(request=request)
            country, city = get_location_by_ip(ip)
            logout_session(db, session=session, ip=ip, user_agent=user_agent, country=country, city=city)
        except Exception:
            pass  # Cookie might be invalid, still clear it
    
    # Always clear the cookie
    clear_refresh_token_cookie(response)
    
    return LogoutResponse(status=True)
    
@router.post("/challenge/start", response_model=ChallengeStartResponse, status_code=status.HTTP_200_OK)
def challenge_start(ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = create_challenge(ctx["db"], user=user)
    return ChallengeStartResponse (
        salt=user.kdf_salt,
        kdf_params=user.kdf_params,
        challenge=challenge.challenge
    )

@router.post("/challenge/finish", response_model=ChallengeFinishResponse, status_code=status.HTTP_202_ACCEPTED)
def challenge_finish(payload: ChallengeFinishRequest, ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    
    challenge = consume_challenge(db=ctx["db"], user_id=user.id)
    if not verify_challenge_signature(user.auth_verifier, challenge.challenge, payload.signature):
        return ChallengeFinishResponse(status=False)
    
    return ChallengeFinishResponse(status=True)
