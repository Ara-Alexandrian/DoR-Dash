#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import models and base
from app.db.base import Base
from app.db.models.user import User, UserRole

# Import all models to ensure they're registered with Base
from app.db.models.file_upload import FileUpload
from app.db.models.mock_exam_request import MockExamRequest
from app.db.models.presentation import AssignedPresentation
from app.db.models.student_update import StudentUpdate
from app.db.models.support_request import SupportRequest

# Create database URL from env variables
DB_USER = os.getenv("POSTGRES_USER", "DoRadmin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1232")
DB_HOST = os.getenv("POSTGRES_SERVER", "172.30.98.213")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "DoR")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine and session
engine = create_engine(DATABASE_URL)

# Create all tables if they don't exist
inspector = inspect(engine)
if not inspector.has_table("users"):
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Create admin user
try:
    # Check if user already exists
    existing_user = session.query(User).filter(User.username == "admin").first()
    
    if existing_user:
        print("Admin user already exists.")
    else:
        # Create new admin user with password 'password'
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        print("Admin user created successfully!")
except Exception as e:
    print(f"Error creating admin user: {e}")
    session.rollback()
finally:
    session.close()