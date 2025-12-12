from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.users import UserConfig

"""
1º Ruta solicitud de verificación del token (JWT):
    Recibe: token
    Devuelve: el status: true o false
    Objetivo: Verificar si el token es válido o no
    Detalles: Es la primera ruta que se llama y en función a lo que devuelva se redirige al usuario a una view o otra
    Status: True: (Tabs) Home
    Status: False (Auth) Login
"""


class TokenVerifyResponse(BaseModel):
    status: bool


"""
2º Ruta de obtención del salt:
    Recibe: username o email (1 sola entrada)
    Devuelve: el salt o error
    Objetivo: Devolver el salt por si el usuario a eliminado la app
    Detalles: Se llama cuando el usuario esta "logeandose" y no se encuentra en el amacenamiento persistente el salt, lo que devuelva lo guardamos en el almacenamiento.
"""

class SaltRequest(BaseModel):
    identifier: str  # username O email

    @field_validator("identifier")
    def validate_identifier(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError("El campo 'identifier' no puede estar vacío.")
        if " " in v:
            raise ValueError("El identifier no puede contener espacios.")
        return v


class SaltResponse(BaseModel):
    salt: str

"""
3º Ruta de registro del usuario:
    Recibe: username, email y auth_key
    Devuelve: token y refresh_token
    Objetivo: Validar, crear, guardar el usuario y obtener el token
    Detalles:
    Crear usuario
    Crear registro en sessions (guardando hash del refresh_token)
    Registrar auditoría (action: register)
"""

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    auth_key: str = Field(..., min_length=32)  # hash de 32 chars o más
    auth_salt: str = Field(..., min_length=16)
    default_settings: UserConfig
    @field_validator("username")
    def validate_username(cls, v):
        if " " in v:
            raise ValueError("El username no puede contener espacios.")
        return v


class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


"""
4º Ruta de logeo del usuario:
    Recibe: username o email (1 sola entrada) y auth_key
    Devuelve: el token o error
    Objetivo: Validar los datos recibidos con la base de datos para determinar si están bien los datos recibidos y si el usuario existe.
    Detalles:
    Validar credenciales
    Crear sesión en tabla sessions
    Registrar auditoría (login success o fail)
"""

class LoginRequest(BaseModel):
    identifier: str  # username O email
    auth_key: str = Field(..., min_length=32)

    @field_validator("identifier")
    def validate_identifier(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError("El campo 'identifier' no puede estar vacío.")
        return v


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


"""
5º POST /auth/refresh
    Recibe: refresh_token
    Devuelve: { access_token nuevo }
    Acciones:
    Comparar hash con tabla sessions
    Actualizar last_used
    Verificar expiración
    Registrar auditoría
"""

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


"""
6º POST /auth/logout
    Recibe: refresh_token
    Acciones:
    Marcar expired = true en sessions
    Registrar auditoría
"""

class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class LogoutResponse(BaseModel):
    status: bool