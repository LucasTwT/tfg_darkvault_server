from pydantic import BaseModel, Field, UUID4

from datetime import datetime

from app.services.actions import Actions, Results


class Log(BaseModel):
    id: int
    user_id: UUID4
    ip: str
    country: str
    city: str
    user_agent: str
    action: Actions
    result: Results
    timestamp: datetime

    class Config:
        from_attributes = True 

class LogsResponse(BaseModel):
    status: bool
    logs: list[Log]
    