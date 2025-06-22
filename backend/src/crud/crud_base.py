from typing import Any, Dict, List, Optional
# import Model from sqlalchemy
from sqlalchemy.orm import Session

class CRUDBase:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model) -> Any:
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def get(self, model_class, filters: Dict[str, Any]) -> Optional[Any]:
        query = self.db.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        return query.first()
    
    def get_by_id(self, model_class, id: int) -> Optional[Any]:
        return self.db.query(model_class).filter(model_class.id == id).first()

    def get_all(self, model_class) -> List[Any]:
        return self.db.query(model_class).all()
    
    def update(self, model: Any, updates: Dict[str, Any]) -> Any:
        for key, value in updates.items():
            setattr(model, key, value)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def delete(self, model: Any) -> None:
        self.db.delete(model)
        self.db.commit()
        return None
    

