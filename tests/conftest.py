import os

# Set DATABASE_URL before any app imports to avoid create_engine(None)
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
