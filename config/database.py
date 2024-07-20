from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

URL_DATABASE = os.getenv('URL_DATABASE')

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    from models.user import Role
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            common_role = Role(name='common')
            professional_role = Role(name='professional')
            db.add(common_role)
            db.add(professional_role)
            db.commit()
    finally:
        db.close()