from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union
from enum import Enum

class Languages(str, Enum):
    en = "en"
    es = "es"

class Themes(str, Enum):
    system = "system"
    light = "light"
    dark = "dark"        

class Clipboard(int, Enum):
    later_15s = 15
    later_1m = 60
    later_2m = 120

class UserConfig(BaseModel):
    lang: Languages
    theme: Themes
    logged: bool
    clipboard_cleaning: Optional[Clipboard] = None
    class Config:
        from_attributes = True 

    
class GetUserSettingsResponse(BaseModel):
    settings: UserConfig
    username: str
    email: str

class SetUserSettingsRequest(BaseModel):
    settings: UserConfig

class SetUserSettingsResponse(BaseModel):
    status: bool