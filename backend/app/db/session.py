from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()
engine = create_engine(str(settings.database_url), future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
