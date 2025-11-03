from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.domain.database import Base


class OriginData(Base):
    """
    Entidad OriginData - Información detallada del origen geográfico del lote
    """
    __tablename__ = "origin_data"

    id = Column(Integer, primary_key=True, index=True)
    coffee_lot_id = Column(Integer, ForeignKey("coffee_lots.id"), unique=True, nullable=False)

    altitude = Column(Float, nullable=False)  # Metros sobre nivel del mar
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    soil_type = Column(String(100), nullable=True)
    climate_zone = Column(String(100), nullable=True)
    farm_section = Column(String(100), nullable=True)

    # Relaciones
    coffee_lot = relationship("CoffeeLot", back_populates="origin_data")

    def validate_coordinates(self) -> bool:
        """Esto valida que las coordenadas estén dentro de rangos geográficos válidos"""
        return (
                -90 <= self.latitude <= 90 and
                -180 <= self.longitude <= 180
        )

    def is_specialty_altitude(self) -> bool:
        """Determina si la altitud cumple requisitos para café especial (> 1200m)"""
        return self.altitude >= 1200 if self.altitude else False