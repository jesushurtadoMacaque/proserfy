from datetime import date
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

URL_DATABASE = os.getenv('URL_DATABASE')

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


DEFAULT_CATEGORIES = [
    {
        "name": "Health",
        "subcategories": [
            {"name": "Physical Therapy"},
            {"name": "Nutrition"},
            {"name": "Mental Health"}
        ]
    },
    {
        "name": "Education",
        "subcategories": [
            {"name": "Tutoring"},
            {"name": "Language Lessons"},
            {"name": "Test Preparation"}
        ]
    },
    {
        "name": "Home Services",
        "subcategories": [
            {"name": "Cleaning"},
            {"name": "Plumbing"},
            {"name": "Electrician"}
        ]
    },
    {
        "name": "Beauty",
        "subcategories": [
            {"name": "Hairdressing"},
            {"name": "Makeup"},
            {"name": "Nails"}
        ]
    },
    {
        "name": "Fitness",
        "subcategories": [
            {"name": "Personal Training"},
            {"name": "Yoga"},
            {"name": "Pilates"}
        ]
    }
]

def init_db():
    from models.categories import Category
    from models.subcategories import SubCategory
    from models.roles import Role
    from models.versions import Version
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            common_role = Role(name='common')
            professional_role = Role(name='professional')
            db.add(common_role)
            db.add(professional_role)
            db.commit()
        
        if db.query(Version).count() == 0:
            first_version = Version( version="1.0.0", release_date=date.today())
            db.add(first_version)
            db.commit()

        for category_data in DEFAULT_CATEGORIES:
            category_name = category_data["name"]
            subcategories = category_data["subcategories"]
            
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.commit()
                db.refresh(category)
            
            for subcategory_data in subcategories:
                subcategory_name = subcategory_data["name"]
                subcategory = db.query(SubCategory).filter(
                    SubCategory.name == subcategory_name,
                    SubCategory.category_id == category.id
                ).first()
                if not subcategory:
                    subcategory = SubCategory(name=subcategory_name, category_id=category.id)
                    db.add(subcategory)
            db.commit()
    finally:
        db.close()


