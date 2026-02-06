from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class CreateLoginRequest(BaseModel):
    ciphertext: bytes
    nonce: bytes
    cipher: str
    version: int
    
class CreateLoginResponse(BaseModel):
    status: bool

class LoginData(BaseModel):
    id: UUID4
    vault_id: UUID4
    ciphertext: bytes
    nonce: bytes
    cipher: str
    version: int
    created_at: datetime
    updated_at: datetime

class GetAllLoginResponseByVaultID(BaseModel):
    status: bool
    user_logins: Optional[list[LoginData]] = []

class ModifyLoginRequest(BaseModel):
    new_data: LoginData

class ModifyLoginResponse(BaseModel):
    status: bool
    
class DeleteLoginStartResponse(BaseModel):
    salt: str
    kdf_params: dict
    challenge: str

class DeleteLoginFinishRequest(BaseModel):
    signature: str
    
class DeleteLoginFinishResponse(BaseModel):
    status: bool