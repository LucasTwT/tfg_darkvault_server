import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.auth.routers import router as router_auth
from .api.v1.logs.routers import router as router_log
from .api.v1.Users.routers import router as router_user
from .api.v1.vaults.routers import router as vault_router
from .api.v1.logins.routers import router as login_router

from app.models import *

app = FastAPI()

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router_auth)
app.include_router(router=router_log)
app.include_router(router=router_user)
app.include_router(router=vault_router)
app.include_router(router=login_router)
