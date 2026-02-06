from fastapi import APIRouter, status, Depends

from app.schemas.vaults import *
from app.utils.get_user_context import get_user_context

from app.repositories.vaults import *
from app.repositories.auth import create_challenge, get_user_data, consume_challenge, verify_challenge_signature

from app.core.ip_management import *

router = APIRouter(prefix="/vault", tags=["Vaults"])

@router.post('/create', response_model=CreateVaultResponse, status_code=status.HTTP_201_CREATED)
def create_vault(payload: CreateVaultRequest, ctx = Depends(get_user_context)):
    create_vault_by_user_id(db=ctx["db"], user_id=ctx["user_id"], vault_name=payload.vault_name, vault_settings=payload.vault_config, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return CreateVaultResponse(status=True)

@router.post('/all', response_model=GetAllVaultsResponse, status_code=status.HTTP_200_OK)
def get_all_vaults(ctx = Depends(get_user_context)):
    vaults = get_all_vaults_by_user_id(db=ctx["db"], user_id=ctx["user_id"])
    return GetAllVaultsResponse(status=True, vaults=vaults)


@router.patch('/{vault_id}', response_model=ModifyVaultResponse, status_code=status.HTTP_202_ACCEPTED)
def modify_vault(vault_id: str, payload: ModifyVaultRequest, ctx = Depends(get_user_context)):
    modify_vault_by_id(ctx["db"], user_id=ctx["user_id"], vault_id=vault_id, new_data=payload.new_data, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return ModifyVaultResponse(status=True)

# Revisión feature/featureHotfixCrypto:
@router.delete('/start', response_model=DeleteVaultStartResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_vault(ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = create_challenge(ctx["db"], user=user)
    return DeleteVaultStartResponse (
        salt=user.kdf_salt,
        kdf_params=user.kdf_params,
        challenge=challenge.challenge
    )

@router.delete('/{vault_id}/finish', response_model=DeleteVaultFinishResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_vault(vault_id: str, payload: DeleteVaultFinishRequest, ctx = Depends(get_user_context)):
    user = get_user_data(ctx["db"], ctx["user_id"])
    challenge = consume_challenge(db=ctx["db"], user_id=user.id)
    
    if not verify_challenge_signature(user.auth_verifier, challenge.challenge, payload.signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    delete_vault_by_id(ctx["db"], user.id, vault_id=vault_id, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return DeleteVaultFinishResponse(status=True)
