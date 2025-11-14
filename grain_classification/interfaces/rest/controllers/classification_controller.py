from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Path
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from grain_classification.application.internal.classification_service import ClassificationApplicationService
from grain_classification.application.internal.classification_query_service import ClassificationQueryService
from grain_classification.domain.model.valueobjetcs.quality_models import CNN_COLOR_CLASSES
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from grain_classification.infrastructure.cloudinary_service import CloudinaryService
from shared.domain.database import get_db


# --- Inyección de Dependencias ---

def get_ml_predictor() -> MLPredictorService:
    model_path = "grain_classification/infrastructure/ml_models/defect_detector.h5"
    if not hasattr(get_ml_predictor, "singleton"):
        get_ml_predictor.singleton = MLPredictorService(model_path, CNN_COLOR_CLASSES)
    return get_ml_predictor.singleton

def get_cv_service() -> CVService:
    if not hasattr(get_cv_service, "singleton"):
        get_cv_service.singleton = CVService()
    return get_cv_service.singleton

def get_grading_service() -> QualityGradingService:
    if not hasattr(get_grading_service, "singleton"):
        get_grading_service.singleton = QualityGradingService()
    return get_grading_service.singleton

def get_cloudinary_service() -> CloudinaryService:
    if not hasattr(get_cloudinary_service, "singleton"):
        get_cloudinary_service.singleton = CloudinaryService()
    return get_cloudinary_service.singleton

def get_classification_service(
        db: Session = Depends(get_db),
        cv: CVService = Depends(get_cv_service),
        ml: MLPredictorService = Depends(get_ml_predictor),
        grading: QualityGradingService = Depends(get_grading_service),
        cloudinary: CloudinaryService = Depends(get_cloudinary_service)
) -> ClassificationApplicationService:
    return ClassificationApplicationService(db, cv, ml, grading, cloudinary)

def get_query_service(db: Session = Depends(get_db)) -> ClassificationQueryService:
    return ClassificationQueryService(db)


# --- Router ---

router = APIRouter(
    prefix="/api/v1/classification",
    tags=["Grain Classification"]
)


# --- DTOs (Data Transfer Objects) ---

class GrainAnalysisResponse(BaseModel):
    """DTO para un análisis individual de grano"""
    id: int
    session_id: int
    image_url: Optional[str]
    color_percentages: dict
    features: dict
    quality_assessment: dict
    final_score: float
    final_category: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClassificationSessionResponse(BaseModel):
    """DTO para una sesión de clasificación"""
    id: int
    session_id_vo: str
    coffee_lot_id: int
    user_id: int
    status: str
    total_grains_analyzed: int
    processing_time_seconds: Optional[float]
    classification_result: dict
    created_at: datetime
    completed_at: Optional[datetime]
    analyses: List[GrainAnalysisResponse] = []

    class Config:
        from_attributes = True


class AverageQualityResponse(BaseModel):
    """DTO para la calidad promedio"""
    coffee_lot_id: int
    average_quality_percentage: float
    total_grains_analyzed: int
    quality_scale: str


class OverallAverageQualityResponse(BaseModel):
    """DTO para la calidad promedio general (todos los lotes)"""
    average_quality_percentage: float
    total_grains_analyzed: int
    total_coffee_lots: int
    quality_scale: str


# --- Endpoints ---

@router.post("/session", response_model=ClassificationSessionResponse, status_code=201)
async def start_and_process_classification_session(
        coffee_lot_id: int = Form(...),
        image: UploadFile = File(...),
        service: ClassificationApplicationService = Depends(get_classification_service)
):
    """
    Inicia, procesa y completa una sesión de clasificación a partir de una imagen.
    Guarda los resultados en la base de datos y las imágenes en Cloudinary.
    """
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Formato de imagen no válido. Usar JPG o PNG."
        )

    image_bytes = await image.read()

    try:
        session = service.start_classification_session(
            coffee_lot_id=coffee_lot_id,
            image_bytes=image_bytes,
            user_id=1  # TODO: Reemplazar con ID de usuario autenticado
        )

        if session.status == "FAILED":
            raise HTTPException(
                status_code=500,
                detail=f"Clasificación fallida: {session.classification_result.get('error')}"
            )

        return session

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error interno durante la clasificación: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor de clasificación."
        )


@router.get("/sessions", response_model=List[ClassificationSessionResponse])
async def get_all_sessions(
        query_service: ClassificationQueryService = Depends(get_query_service)
):
    """
    Obtiene TODAS las sesiones de clasificación (sin filtro por lote).
    """
    sessions = query_service.get_all_sessions()

    if not sessions:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron sesiones de clasificación"
        )

    return sessions


@router.get("/sessions/coffee-lot/{coffee_lot_id}", response_model=List[ClassificationSessionResponse])
async def get_sessions_by_coffee_lot(
        coffee_lot_id: int = Path(..., description="ID del lote de café"),
        query_service: ClassificationQueryService = Depends(get_query_service)
):
    """
    Obtiene todas las sesiones de clasificación de un lote de café específico.
    """
    sessions = query_service.get_sessions_by_coffee_lot(coffee_lot_id)

    if not sessions:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron sesiones para el lote {coffee_lot_id}"
        )

    return sessions


@router.get("/overall-average-quality", response_model=OverallAverageQualityResponse)
async def get_overall_average_quality(
        query_service: ClassificationQueryService = Depends(get_query_service)
):
    """
    Calcula la calidad promedio de todos los granos analizados (sin filtro por lote).
    Retorna un porcentaje en escala de 0-100%.
    """
    result = query_service.get_overall_average_quality()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron análisis de granos"
        )

    return result


@router.get("/average-quality/coffee-lot/{coffee_lot_id}", response_model=AverageQualityResponse)
async def get_average_quality_by_coffee_lot(
        coffee_lot_id: int = Path(..., description="ID del lote de café"),
        query_service: ClassificationQueryService = Depends(get_query_service)
):
    """
    Calcula la calidad promedio de todos los granos analizados de un lote.
    Retorna un porcentaje en escala de 0-100%.
    """
    result = query_service.get_average_quality_by_coffee_lot(coffee_lot_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron análisis para el lote {coffee_lot_id}"
        )

    return result


@router.get("/session/{session_id}", response_model=ClassificationSessionResponse)
async def get_session_by_id(
        session_id: int = Path(..., description="ID de la sesión"),
        query_service: ClassificationQueryService = Depends(get_query_service)
):
    """
    Obtiene una sesión específica con todos sus análisis de granos.
    """
    session = query_service.get_session_by_id(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la sesión {session_id}"
        )

    return session