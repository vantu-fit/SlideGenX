from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class Slide(Base):
    __tablename__ = "Slide"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    username = Column(String, nullable=False)

    def __repr__(self):
        return f"<Slide(id={self.id}, session_id={self.session_id}, username={self.username})>"