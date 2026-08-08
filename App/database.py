from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
sqlalchemy_database_url = "sqlite:///./student.db"
engine = create_engine(sqlalchemy_database_url)
sqlalchemy_database_url, 

connect_args={"check_same_thread": False,"timeout": 15},
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()