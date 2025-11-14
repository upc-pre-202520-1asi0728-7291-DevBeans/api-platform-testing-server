from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from grain_classification.domain.model.aggregates.classification_session import ClassificationSession
from grain_classification.domain.model.aggregates.grain_analysis import GrainAnalysis


class ClassificationQueryService:
    """
    Servicio para consultas de lectura sobre sesiones de clasificación
    """

    def __init__(self, db: Session):
        self.db = db


    """
    Obtiene TODAS las sesiones de clasificación
    """
    def get_all_sessions(self) -> list[type[ClassificationSession]]:
        return (
            self.db.query(ClassificationSession)
            .options(joinedload(ClassificationSession.analyses))
            .order_by(ClassificationSession.created_at.desc())
            .all()
        )


    """
    Obtiene todas las sesiones de clasificación de un lote de café
    """
    def get_sessions_by_coffee_lot(self, coffee_lot_id: int) -> list[type[ClassificationSession]]:
        return (
            self.db.query(ClassificationSession)
            .filter(ClassificationSession.coffee_lot_id == coffee_lot_id)
            .options(joinedload(ClassificationSession.analyses))
            .order_by(ClassificationSession.created_at.desc())
            .all()
        )


    """
    Calcula la calidad promedio de TODOS los granos (sin filtro por lote)
    """
    def get_overall_average_quality(self) -> Optional[dict]:
        result = (
            self.db.query(
                func.avg(GrainAnalysis.final_score).label('avg_score'),
                func.count(GrainAnalysis.id).label('total_grains'),
                func.count(func.distinct(ClassificationSession.coffee_lot_id)).label('total_lots')
            )
            .join(ClassificationSession)
            .first()
        )

        if result and result.avg_score is not None:
            # Convertir de 0-1 a 0-100%
            avg_percentage = round(float(result.avg_score) * 100, 2)
            return {
                'average_quality_percentage': avg_percentage,
                'total_grains_analyzed': result.total_grains,
                'total_coffee_lots': result.total_lots,
                'quality_scale': '0-100%'
            }

        return None


    """
    Calcula la calidad promedio de todos los granos de un lote (0-100%)
    """
    def get_average_quality_by_coffee_lot(self, coffee_lot_id: int) -> Optional[dict]:
        result = (
            self.db.query(
                func.avg(GrainAnalysis.final_score).label('avg_score'),
                func.count(GrainAnalysis.id).label('total_grains')
            )
            .join(ClassificationSession)
            .filter(ClassificationSession.coffee_lot_id == coffee_lot_id)
            .first()
        )

        if result and result.avg_score is not None:
            # Convertir de 0-1 a 0-100%
            avg_percentage = round(float(result.avg_score) * 100, 2)
            return {
                'coffee_lot_id': coffee_lot_id,
                'average_quality_percentage': avg_percentage,
                'total_grains_analyzed': result.total_grains,
                'quality_scale': '0-100%'
            }

        return None


    """
    Obtiene una sesión específica con todos sus análisis
    """
    def get_session_by_id(self, session_id: int) -> Optional[ClassificationSession]:
        return (
            self.db.query(ClassificationSession)
            .filter(ClassificationSession.id == session_id)
            .options(joinedload(ClassificationSession.analyses))
            .first()
        )