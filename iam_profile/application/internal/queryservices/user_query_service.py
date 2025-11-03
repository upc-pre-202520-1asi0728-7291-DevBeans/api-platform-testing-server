from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from iam_profile.domain.model.aggregates.user import User
from iam_profile.domain.model.queries.get_user_by_id_query import GetUserByIdQuery
from iam_profile.domain.model.queries.get_user_by_email_query import GetUserByEmailQuery
from iam_profile.infrastructure.persistence.database.repositories.user_repository import UserRepository


class UserQueryService:
    """Servicio de queries para User"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def handle_get_user_by_id(self, query: GetUserByIdQuery) -> Optional[User]:
        """Obtiene usuario por ID"""
        user = self.user_repository.find_by_id(query.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def handle_get_user_by_email(self, query: GetUserByEmailQuery) -> Optional[User]:
        """Obtiene usuario por email"""
        user = self.user_repository.find_by_email(query.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user