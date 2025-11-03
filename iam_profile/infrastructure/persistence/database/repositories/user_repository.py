from sqlalchemy.orm import Session
from typing import Optional
from iam_profile.domain.model.aggregates.user import User


class UserRepository:
    """Repositorio para la entidad User"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        """Guarda o actualiza un usuario"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuario por email"""
        return self.db.query(User).filter(User.email == email).first()

    def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con el email"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def delete(self, user: User) -> None:
        """Elimina un usuario"""
        self.db.delete(user)
        self.db.commit()