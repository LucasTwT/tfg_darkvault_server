from sqlalchemy.orm import Session

from datetime import datetime, UTC

from app.models.audit_logs import AuditLogs
from app.services.actions import Actions, Results

def get_logs_by_user_id(db: Session, id: str):
    logs = db.query(AuditLogs).filter(AuditLogs.user_id == id).all()
    return logs

def add_new_log(db: Session, user_id: str, ip: str, country:str, city: str, user_agent: str, action: Actions, result: Results, timestamp: datetime = datetime.now(UTC)):
    log = AuditLogs(user_id=user_id, ip=ip, country=country, city=city, user_agent=user_agent, action=action, result=result, timestamp=timestamp) 
    db.add(log)
    db.commit()
    db.refresh(log)
    return log