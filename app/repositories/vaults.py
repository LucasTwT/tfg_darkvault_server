from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import and_

from datetime import datetime, UTC

from app.schemas.vaults import VaultConfig, Vault
from app.models.vaults import Vaults
from app.services.actions import Actions, Results
from app.repositories.logs import add_new_log

def create_vault_by_user_id(db: Session, user_id: str, vault_name, vault_settings: VaultConfig, ip: str, country: str, city: str, user_agent: str):
    new_vault = Vaults(user_id=user_id, name=vault_name, settings=vault_settings.model_dump())
    db.add(new_vault)
    db.commit()
    db.refresh(new_vault)
    add_new_log(db, user_id=user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.new_vault, result=Results.success)
    return new_vault

def get_all_vaults_by_user_id(db: Session, user_id: str):
    vaults = db.query(Vaults).filter(Vaults.user_id == user_id).all()
    return vaults

def modify_vault_by_id(db: Session, user_id: str, vault_id: str, new_data: Vault, ip: str, country: str, city: str, user_agent: str):
    vault = db.query(Vaults).filter(and_(Vaults.user_id == user_id, Vaults.id == vault_id)).first()
    if not vault:
        raise HTTPException(detail="Wrong vault id", status_code=status.HTTP_404_NOT_FOUND)
    vault.name = new_data.name
    vault.settings = new_data.settings.model_dump()
    vault.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(vault)
    
    add_new_log(db, user_id=user_id,ip=ip, country=country, city=city, user_agent=user_agent, action=Actions.modify_vault, result=Results.success)
    return vault

def delete_vault_by_id(db: Session, user_id: str, vault_id: str,
                       ip: str, country: str, city: str, user_agent: str):

    vault = db.query(Vaults).filter(
        and_(Vaults.user_id == user_id, Vaults.id == vault_id)
    ).first()

    if not vault:
        raise HTTPException(
            detail="Wrong vault id",
            status_code=status.HTTP_404_NOT_FOUND
        )

    db.delete(vault)
    db.commit()

    add_new_log(
        db, user_id=user_id,
        ip=ip, country=country, city=city, user_agent=user_agent,
        action=Actions.delete_vault,
        result=Results.success
    )