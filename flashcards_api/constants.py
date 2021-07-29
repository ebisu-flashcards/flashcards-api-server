SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_CONNECTION_ARGS = {"check_same_thread": False}

DISPLAY_TRACEBACK_ON_500 = True
