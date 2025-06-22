from crud.crud_base import CRUDBase
from model.user import User

from sqlalchemy.orm import Session
from typing import Optional

class CRUDUser(CRUDBase):
    def __init__(self, db):
        super().__init__(db)    
    
    def check_username_exist(self, username: str) -> bool:
        """
        Check if a username already exists in the database.
        
        Args:
            username (str): The username to check.
        
        Returns:
            bool: True if the username exists, False otherwise.
        """
        return self.db.query(User).filter(User.username == username).first() is not None
    
    def check_email_exist(self, email: str) -> bool:
        """
        Check if an email already exists in the database.
        
        Args:
            email (str): The email to check.
        
        Returns:
            bool: True if the email exists, False otherwise.
        """
        return self.db.query(User).filter(User.email == email).first() is not None
    
if __name__ == "__main__":
    from db.session import get_db
    from sqlalchemy.orm import Session

    db: Session = next(get_db())
    crud_user = CRUDUser(db)

    # Example usage
    username_exists = crud_user.check_username_exist("08112004")
    print(f"Username exists: {username_exists}")
    
    # You can also add more CRUD operations as needed