from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create the database engine
engine = create_engine(settings.DATABASE_URL)
# Create a configured "Session" class
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a base class for declarative models
Base = declarative_base()   
# Dependency to get the database session
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    #test query from User table
    from model.user import User  # Assuming you have a User model defined in models/user.py
    with SessionLocal() as session:
        users = session.query(User).all()
        for user in users:
            print(user)
