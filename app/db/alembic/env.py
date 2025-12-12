import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Agregar /app al sys.path (ajusta según dónde esté tu env.py)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Ahora ya puedes importar
from app.db.base import Base
from app.models.users import Users
from app.models.user_settings import UserSettings
from app.models.audit_logs import AuditLogs
from app.models.file_chunks import FileChunks
from app.models.ip_blocklist import IPBlockList
from app.models.logins import Logins
from app.models.sessions import Sessions
from app.models.vault_files import VaultFiles
from app.models.vaults import Vaults

# Cargar variables de entorno (.env)
load_dotenv()

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadatos para autogenerate
target_metadata = Base.metadata

# URL de la DB

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment")

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
