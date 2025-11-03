from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from shared.domain.database import Base


class ProducerProfile(Base):
    """
    Entidad ProducerProfile - Perfil específico de productor independiente
    """
    __tablename__ = "producer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Información personal
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    document_number = Column(String(50), nullable=False)
    document_type = Column(String(20), nullable=False)

    # Información de contacto
    phone_number = Column(String(20), nullable=False)
    alternative_phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="Perú")

    # Información de la finca
    farm_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    region = Column(String(100), nullable=False)
    hectares = Column(Float, nullable=False)
    coffee_varieties = Column(JSON, nullable=True)  # Lista de variedades
    production_capacity = Column(Integer, nullable=True)  # Kg por año

    # Relaciones
    user = relationship("User", back_populates="producer_profile")

    def add_coffee_variety(self, variety: str) -> None:
        """Agrega una variedad de café"""
        if self.coffee_varieties is None:
            self.coffee_varieties = []
        if variety not in self.coffee_varieties:
            self.coffee_varieties.append(variety)

    def update_location(self, latitude: float, longitude: float, altitude: float = None) -> None:
        """Actualiza la ubicación de la finca"""
        self.latitude = latitude
        self.longitude = longitude
        if altitude:
            self.altitude = altitude