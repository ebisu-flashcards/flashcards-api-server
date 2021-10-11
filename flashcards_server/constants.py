#
# Database
#

#: Database path
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

#: Database connection args (for SQLAlchemy engine)
SQLALCHEMY_DATABASE_CONNECTION_ARGS = {"check_same_thread": False}

#
# Authentication
#

#: Secret key. To get a string like this, run: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

#: Hashing algorithm for authentication
HASHING_ALGORITHM = "HS256"

#: How many minutes should the access token last
ACCESS_TOKEN_EXPIRE_MINUTES = 15

#: The domain name where this app is deployed
DOMAIN = "localhost"  # FIXME


#
# Development
#

#: Return 200 with a stacktrace instead of 500
DISPLAY_TRACEBACK_ON_500 = True
