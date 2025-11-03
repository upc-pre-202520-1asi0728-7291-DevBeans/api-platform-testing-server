from iam_profile.domain.model.entities.cooperative_profile import CooperativeProfile
from sqlalchemy.orm import Session
from typing import Optional

class CooperativeProfileRepository:
    """Repositorio para CooperativeProfile"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, profile: CooperativeProfile) -> CooperativeProfile:
        """Guarda o actualiza un perfil de cooperativa"""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def find_by_user_id(self, user_id: int) -> Optional[CooperativeProfile]:
        """Busca perfil por user_id"""
        return self.db.query(CooperativeProfile).filter(CooperativeProfile.user_id == user_id).first()

    def find_by_id(self, profile_id: int) -> Optional[CooperativeProfile]:
        """Busca perfil por ID"""
        return self.db.query(CooperativeProfile).filter(CooperativeProfile.id == profile_id).first()

    def find_by_legal_registration(self, registration_number: str) -> Optional[CooperativeProfile]:
        """Busca cooperativa por número de registro legal"""
        return self.db.query(CooperativeProfile).filter(
            CooperativeProfile.legal_registration_number == registration_number
        ).first()