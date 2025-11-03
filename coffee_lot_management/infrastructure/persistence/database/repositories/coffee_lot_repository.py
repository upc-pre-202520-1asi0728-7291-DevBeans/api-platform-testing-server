from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from coffee_lot_management.domain.model.aggregates.coffee_lot import CoffeeLot, LotStatus, CoffeeVariety


class CoffeeLotRepository:
    """Repositorio para la entidad CoffeeLot"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, coffee_lot: CoffeeLot) -> CoffeeLot:
        """Guarda o actualiza un lote de café"""
        self.db.add(coffee_lot)
        self.db.commit()
        self.db.refresh(coffee_lot)
        return coffee_lot

    def find_by_id(self, lot_id: int) -> Optional[CoffeeLot]:
        """Busca lote por ID"""
        return self.db.query(CoffeeLot).filter(CoffeeLot.id == lot_id).first()

    def find_by_lot_number(self, lot_number: str) -> Optional[CoffeeLot]:
        """Busca lote por número único"""
        return self.db.query(CoffeeLot).filter(CoffeeLot.lot_number == lot_number).first()

    def find_by_producer_id(self, producer_id: int) -> list[type[CoffeeLot]]:
        """Obtiene todos los lotes de un productor"""
        return self.db.query(CoffeeLot).filter(CoffeeLot.producer_id == producer_id).all()

    def find_by_producer_id_and_status(self, producer_id: int, status: LotStatus) -> list[type[CoffeeLot]]:
        """Obtiene lotes de un productor filtrados por estado"""
        return self.db.query(CoffeeLot).filter(
            CoffeeLot.producer_id == producer_id,
            CoffeeLot.status == status
        ).all()

    def find_by_harvest_date_between(self, start_date: date, end_date: date) -> list[type[CoffeeLot]]:
        """Obtiene lotes por rango de fechas de cosecha"""
        return self.db.query(CoffeeLot).filter(
            CoffeeLot.harvest_date >= start_date,
            CoffeeLot.harvest_date <= end_date
        ).all()

    def find_by_coffee_variety(self, variety: CoffeeVariety) -> list[type[CoffeeLot]]:
        """Obtiene lotes por variedad de café"""
        return self.db.query(CoffeeLot).filter(CoffeeLot.coffee_variety == variety).all()

    def exists_by_lot_number(self, lot_number: str) -> bool:
        """Verifica si existe un lote con el número dado"""
        return self.db.query(CoffeeLot).filter(CoffeeLot.lot_number == lot_number).first() is not None

    def count_by_producer_id_and_status(self, producer_id: int, status: LotStatus) -> int:
        """Cuenta lotes de un productor por estado"""
        return self.db.query(CoffeeLot).filter(
            CoffeeLot.producer_id == producer_id,
            CoffeeLot.status == status
        ).count()

    def delete(self, coffee_lot: CoffeeLot) -> None:
        """Elimina un lote de café"""
        self.db.delete(coffee_lot)
        self.db.commit()