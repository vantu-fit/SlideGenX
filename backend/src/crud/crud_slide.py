from crud.crud_base import CRUDBase
from model.slide import Slide

from sqlalchemy.orm import Session
from typing import Optional

class CRUDSlide(CRUDBase):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_session_ids_by_username(self, username: str) -> list:
        """
        Get all session IDs associated with a given username.

        Args:
            username (str): The username to search for.

        Returns:
            list: List of session IDs associated with the username.
        """
        return self.db.query(Slide.session_id).filter(Slide.username == username).all()
    
    def check_slide_belongs_to_user(self, session_id: str, username: str) -> bool:
        """
        Check if a slide belongs to a specific user.

        Args:
            session_id (str): Session ID of the slide.
            username (str): Username of the user.

        Returns:
            bool: True if the slide belongs to the user, False otherwise.
        """
        return self.db.query(Slide).filter(Slide.session_id == session_id, Slide.username == username).first() is not None