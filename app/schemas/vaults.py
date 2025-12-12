from pydantic import BaseModel, EmailStr, Field, field_validator, UUID4
from typing import Optional, Union
from enum import Enum
from datetime import datetime

class Color(BaseModel):
    bgColor: str
    icColor: str
    class Config:
        from_attributes = True

class VaultConfig(BaseModel):
    icon: str
    colors: Color
    class Config:
        from_attributes = True  

class Vault(BaseModel):
    id: UUID4
    name: str
    settings: VaultConfig
    created_at: datetime
    updated_at: datetime 
    class Config:
        from_attributes = True
        
class CreateVaultRequest(BaseModel):
    vault_name: str = Field(..., min_length=3, max_length=32)
    vault_config: VaultConfig

class CreateVaultResponse(BaseModel):
    status: bool
    
    
class GetAllVaultsResponse(BaseModel):
    status: bool
    vaults: Optional[list[Vault]] = []
    
class ModifyVaultRequest(BaseModel):
    new_data: Vault
    
class ModifyVaultResponse(BaseModel):
    status: bool
    

class DeleteVaultResponse(BaseModel):
    status: bool
    