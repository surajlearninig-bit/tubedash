from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL: PostgreSQL ka URL jo docker-compose mein define kiya gaya hai
DATABASE_URL = "postgresql://user:password@postgres-db:5432/tubedash"

# SQLAlchemy engine banayein
engine = create_engine(DATABASE_URL)

# SessionLocal class jo database connection manage karegi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class jisme hum apne models define karenge
Base = declarative_base()
