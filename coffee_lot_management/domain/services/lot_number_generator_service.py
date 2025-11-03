from datetime import datetime
from sqlalchemy.orm import Session
from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import CoffeeLotRepository


class LotNumberGeneratorService:
    """
    Servicio para generar números únicos de lote
    Patrón: LOT-YYYY-NNNN donde YYYY es año y NNNN es secuencial
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = CoffeeLotRepository(db)

    def generate_lot_number(self) -> str:
        """
        Genera un número único de lote para un productor
        Formato: LOT-YYYY-NNNN
        """
        current_year = datetime.now().year

        # Obtener el último número secuencial del año actual
        lots_this_year = self.db.execute(
            f"""
            SELECT COUNT(*) FROM coffee_lots 
            WHERE EXTRACT(YEAR FROM created_at) = {current_year}
            """
        ).scalar()

        # Incrementar el secuencial
        sequential = (lots_this_year or 0) + 1

        # Formato: LOT-2024-0001
        lot_number = f"LOT-{current_year}-{sequential:04d}"

        # Verificar unicidad (por si acaso)
        while self.repository.exists_by_lot_number(lot_number):
            sequential += 1
            lot_number = f"LOT-{current_year}-{sequential:04d}"

        return lot_number