from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from shared.domain.database import Base


class CooperativeProfile(Base):
    """
    Entidad CooperativeProfile - Perfil de cooperativa cafetalera
    """
    __tablename__ = "cooperative_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Información de la cooperativa
    cooperative_name = Column(String(255), nullable=False)
    legal_registration_number = Column(String(100), nullable=False, unique=True)

    # Información de contacto
    phone_number = Column(String(20), nullable=False)
    alternative_phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="Perú")

    # Representante legal
    legal_representative_name = Column(String(200), nullable=False)
    legal_representative_email = Column(String(255), nullable=False)

    # Información operativa
    processing_capacity = Column(Integer, nullable=True)  # Kg por año
    certifications = Column(JSON, nullable=True)  # Lista de certificaciones
    associated_producers = Column(JSON, nullable=True)  # IDS de productores asociados

    # Relaciones
    user = relationship("User", back_populates="cooperative_profile")

    def add_associated_producer(self, producer_id: int) -> None:
        """Asocia un productor a la cooperativa"""
        if self.associated_producers is None:
            self.associated_producers = []
        if producer_id not in self.associated_producers:
            self.associated_producers.append(producer_id)

    def update_processing_capacity(self, capacity: int) -> None:
        """Actualiza la capacidad de procesamiento"""
        self.processing_capacity = capacity

    def add_certification(self, certification: str) -> None:
        """Agrega una certificación obtenida"""
        if self.certifications is None:
            self.certifications = []
        if certification not in self.certifications:
            self.certifications.append(certification)