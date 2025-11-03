import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.orm import relationship

from shared.domain.aggregate_root import AuditableAbstractAggregateRoot


class LotStatus(str, enum.Enum):
    REGISTERED = "REGISTERED"
    PROCESSING = "PROCESSING"
    CLASSIFIED = "CLASSIFIED"
    CERTIFIED = "CERTIFIED"
    SHIPPED = "SHIPPED"


class CoffeeVariety(str, enum.Enum):
    TYPICA = "TYPICA"
    CATURRA = "CATURRA"
    BOURBON = "BOURBON"
    GEISHA = "GEISHA"
    SL28 = "SL28"
    SL34 = "SL34"
    CASTILLO = "CASTILLO"
    COLOMBIA = "COLOMBIA"


class ProcessingMethod(str, enum.Enum):
    WASHED = "WASHED"
    NATURAL = "NATURAL"
    HONEY = "HONEY"
    SEMI_WASHED = "SEMI_WASHED"


class CoffeeLot(AuditableAbstractAggregateRoot):
    """
    Agregado CoffeeLot - Gestiona el ciclo de vida de lotes de café
    """
    __tablename__ = "coffee_lots"

    lot_number = Column(String(50), unique=True, nullable=False, index=True)
    producer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    harvest_date = Column(Date, nullable=False)
    coffee_variety = Column(SQLEnum(CoffeeVariety), nullable=False)
    quantity = Column(Float, nullable=False)  # Kilogramos
    status = Column(SQLEnum(LotStatus), default=LotStatus.REGISTERED, nullable=False)
    processing_method = Column(SQLEnum(ProcessingMethod), nullable=False)

    # Información de origen
    altitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    soil_type = Column(String(100), nullable=True)
    climate_zone = Column(String(100), nullable=True)
    farm_section = Column(String(100), nullable=True)

    # Relaciones
    origin_data = relationship("OriginData", back_populates="coffee_lot", uselist=False, cascade="all, delete-orphan")

    def __init__(self, lot_number: str, producer_id: int, harvest_date: date, coffee_variety: CoffeeVariety,
                 quantity: float, processing_method: ProcessingMethod, latitude: float, longitude: float, **kw: Any):
        super().__init__(**kw)
        self.lot_number = lot_number
        self.producer_id = producer_id
        self.harvest_date = harvest_date
        self.coffee_variety = coffee_variety
        self.quantity = quantity
        self.processing_method = processing_method
        self.status = LotStatus.REGISTERED
        self.latitude = latitude
        self.longitude = longitude

    def update_quantity(self, new_quantity: float) -> None:
        """Actualiza la cantidad del lote"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        self.quantity = new_quantity

    def change_status(self, new_status: LotStatus) -> None:
        """Cambia el estado del lote siguiendo el workflow definido"""
        # Validar transiciones válidas
        valid_transitions = {
            LotStatus.REGISTERED: [LotStatus.PROCESSING],
            LotStatus.PROCESSING: [LotStatus.CLASSIFIED],
            LotStatus.CLASSIFIED: [LotStatus.CERTIFIED],
            LotStatus.CERTIFIED: [LotStatus.SHIPPED]
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")

        self.status = new_status

    def can_be_deleted(self) -> bool:
        """Verifica si el lote puede ser eliminado"""
        return self.status == LotStatus.REGISTERED

    def is_ready_for_classification(self) -> bool:
        """Determina si cumple requisitos para clasificación"""
        return (
                self.status == LotStatus.REGISTERED and
                self.quantity >= 100 and  # Mínimo 100 kg
                self.harvest_date is not None
        )