"""
conftest.py - Configuración compartida de fixtures para tests de integración
Este archivo es automáticamente detectado por pytest y sus fixtures están
disponibles para todos los archivos de test en el directorio.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock
from sqlalchemy.orm import Session

from grain_classification.application.internal.classification_service import ClassificationApplicationService
from grain_classification.application.internal.classification_query_service import ClassificationQueryService
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from grain_classification.infrastructure.cloudinary_service import CloudinaryService


# ============================================================================
# FIXTURES DE BASE DE DATOS
# ============================================================================

@pytest.fixture
def mock_db_session():
    """
    Simula una sesión de base de datos SQLAlchemy.

    Returns:
        Mock: Objeto mock configurado para simular Session de SQLAlchemy
    """
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.query = Mock()
    return session


# ============================================================================
# FIXTURES DE SERVICIOS DE INFRAESTRUCTURA
# ============================================================================

@pytest.fixture
def mock_cv_service():
    """
    Simula el servicio de Computer Vision.
    Configura respuestas por defecto para segmentación y extracción de características.

    Returns:
        Mock: CVService mockeado con comportamiento predeterminado
    """
    cv_service = Mock(spec=CVService)

    # Simular imagen de prueba (100x100 pixels, BGR)
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:, :] = [139, 69, 19]  # Color café en BGR

    cv_service.load_image_from_bytes.return_value = test_image

    # Simular segmentación de granos (2 granos por defecto)
    cv_service.segment_beans.return_value = [
        {
            'image': test_image,
            'contour': np.array([[10, 10], [90, 10], [90, 90], [10, 90]])
        },
        {
            'image': test_image,
            'contour': np.array([[10, 10], [90, 10], [90, 90], [10, 90]])
        }
    ]

    # Simular extracción de características (grano promedio, sin defectos)
    cv_service.extract_all_features.return_value = {
        'area': 1500.0,
        'perimeter': 200.0,
        'circularity': 0.85,
        'has_cracks': 'False'
    }

    return cv_service


@pytest.fixture
def mock_ml_predictor():
    """
    Simula el servicio de predicción de Machine Learning.
    Configura predicciones por defecto para clasificación de color.

    Returns:
        Mock: MLPredictorService mockeado con predicciones de calidad premium
    """
    ml_predictor = Mock(spec=MLPredictorService)

    # Simular predicción de colores (grano de calidad premium por defecto)
    ml_predictor.predict_color_percentages.return_value = {
        'Light': 5.0,
        'Medium': 85.0,  # Clase predominante -> Premium
        'Dark': 5.0,
        'Green': 5.0
    }

    return ml_predictor


@pytest.fixture
def mock_cloudinary_service():
    """
    Simula el servicio de Cloudinary para almacenamiento de imágenes.

    Returns:
        Mock: CloudinaryService mockeado con URLs de prueba
    """
    cloudinary_service = Mock(spec=CloudinaryService)

    cloudinary_service.upload_grain_image.return_value = {
        'url': 'https://cloudinary.com/test-image.jpg',
        'public_id': 'grains/test_session/grain_0'
    }

    return cloudinary_service


@pytest.fixture
def grading_service():
    """
    Servicio de calificación real (no mock).
    Se usa la implementación real para probar la lógica de negocio.

    Returns:
        QualityGradingService: Instancia real del servicio de calificación
    """
    return QualityGradingService()


# ============================================================================
# FIXTURES DE SERVICIOS DE APLICACIÓN
# ============================================================================

@pytest.fixture
def classification_service(mock_db_session, mock_cv_service, mock_ml_predictor,
                           grading_service, mock_cloudinary_service):
    """
    Servicio de clasificación configurado con todas las dependencias mockeadas.

    Args:
        mock_db_session: Sesión de base de datos mockeada
        mock_cv_service: Servicio de CV mockeado
        mock_ml_predictor: Predictor ML mockeado
        grading_service: Servicio de calificación real
        mock_cloudinary_service: Servicio de Cloudinary mockeado

    Returns:
        ClassificationApplicationService: Servicio listo para testing
    """
    return ClassificationApplicationService(
        db=mock_db_session,
        cv_service=mock_cv_service,
        ml_predictor=mock_ml_predictor,
        grading_service=grading_service,
        cloudinary_service=mock_cloudinary_service
    )


@pytest.fixture
def query_service(mock_db_session):
    """
    Servicio de consultas configurado con base de datos mockeada.

    Args:
        mock_db_session: Sesión de base de datos mockeada

    Returns:
        ClassificationQueryService: Servicio de consultas listo para testing
    """
    return ClassificationQueryService(db=mock_db_session)


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================================

@pytest.fixture
def sample_image_bytes():
    """
    Genera bytes de imagen JPEG de prueba para usar en tests.

    Returns:
        bytes: Imagen codificada en JPEG como bytes
    """
    # Crear imagen de prueba (200x200 pixels, color café)
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    test_image[:, :] = [139, 69, 19]  # Color café en BGR

    # Codificar como JPEG
    _, buffer = cv2.imencode('.jpg', test_image)
    return buffer.tobytes()


# ============================================================================
# CONFIGURACIÓN DE PYTEST
# ============================================================================

def pytest_configure(config):
    """
    Configuración global de pytest.
    Registra markers personalizados para categorizar tests.
    """
    config.addinivalue_line(
        "markers", "us12: Tests para User Story 12 - Detección de Defectos"
    )
    config.addinivalue_line(
        "markers", "us13: Tests para User Story 13 - Análisis de Color y Uniformidad"
    )
    config.addinivalue_line(
        "markers", "us14: Tests para User Story 14 - Clasificación por Estándares"
    )
    config.addinivalue_line(
        "markers", "integration: Tests de integración completos"
    )
    config.addinivalue_line(
        "markers", "slow: Tests que toman más tiempo en ejecutar"
    )