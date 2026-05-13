from fastapi import APIRouter, status, Depends

from app.schemas.logins import *
from app.utils.get_user_context import get_user_context

from app.repositories.logins import *
from app.repositories.auth import create_challenge, get_user_data, consume_challenge, verify_challenge_signature

router = APIRouter(prefix="/login", tags=["login"])

@router.post('/{vault_id}/create', response_model=CreateLoginResponse, status_code=status.HTTP_201_CREATED)
def create_login(vault_id: str, payload: CreateLoginRequest, ctx = Depends(get_user_context)):
    create_login_by_vault_id(db=ctx["db"],payload=payload, user_id=ctx["user_id"], vault_id=vault_id, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return CreateLoginResponse(status=True)

@router.post('/{vault_id}/all', response_model=GetAllLoginResponseByVaultID, status_code=status.HTTP_200_OK)
def get_all_logins(vault_id: str, ctx = Depends(get_user_context)):
    logins = get_all_logins_by_vault_id(db=ctx["db"], user_id=ctx["user_id"], vault_id=vault_id)
    return GetAllLoginResponseByVaultID(status=True, user_logins=logins)


@router.patch('/{vault_id}/{login_id}', response_model=ModifyLoginResponse, status_code=status.HTTP_202_ACCEPTED)
def modify_login_endpoint(vault_id: str, login_id: str, payload: ModifyLoginRequest, ctx = Depends(get_user_context)):
    modify_login(ctx["db"], user_id=ctx["user_id"], payload=payload, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return ModifyLoginResponse(status=True)

@router.delete('/start', response_model=DeleteLoginStartResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_vault(ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = create_challenge(ctx["db"], user=user)
    return DeleteLoginStartResponse (
        salt=user.kdf_salt,
        kdf_params=user.kdf_params,
        challenge=challenge.challenge
    )

@router.delete('/{vault_id}/{login_id}/finish', response_model=DeleteLoginFinishResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_vault(vault_id: str, login_id: str, payload: DeleteLoginFinishRequest, ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = consume_challenge(db=ctx["db"], user_id=user.id)
    
    if not verify_challenge_signature(user.auth_verifier, challenge.challenge, payload.signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    delete_login(ctx["db"], user_id=user.id, vault_id=vault_id, login_id=login_id, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return DeleteLoginFinishResponse(status=True)
