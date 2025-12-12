from fastapi import APIRouter, status, Depends

from app.schemas.vaults import *
from app.utils.get_user_context import get_user_context

from app.repositories.vaults import *

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

@router.delete('/{vault_id}', response_model=DeleteVaultResponse, status_code=status.HTTP_202_ACCEPTED)
def delete_vault(vault_id: str, ctx = Depends(get_user_context)):
    delete_vault_by_id(ctx["db"], user_id=ctx["user_id"], vault_id=vault_id, ip=ctx["ip"], city=ctx["city"], country=ctx["country"], user_agent=ctx["agent"])
    return DeleteVaultResponse(status=True)
