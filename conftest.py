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

# ============================================================================
# GRAIN CLASSIFICATION IMPORTS
# ============================================================================
from grain_classification.application.internal.classification_service import ClassificationApplicationService
from grain_classification.application.internal.classification_query_service import ClassificationQueryService
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from grain_classification.infrastructure.cloudinary_service import CloudinaryService

# ============================================================================
# COFFEE LOT MANAGEMENT IMPORTS
# ============================================================================
from coffee_lot_management.application.internal.commandservices.coffee_lot_command_service import (
    CoffeeLotCommandService
)
from coffee_lot_management.application.internal.queryservices.coffee_lot_query_service import (
    CoffeeLotQueryService
)
from coffee_lot_management.domain.services.lot_number_generator_service import (
    LotNumberGeneratorService
)
from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import (
    CoffeeLotRepository
)


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
# FIXTURES DE SERVICIOS DE INFRAESTRUCTURA - GRAIN CLASSIFICATION
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
# FIXTURES DE REPOSITORIOS - COFFEE LOT MANAGEMENT
# ============================================================================

@pytest.fixture
def mock_coffee_lot_repository():
    """
    Simula el repositorio de lotes de café.

    Returns:
        Mock: CoffeeLotRepository mockeado con operaciones CRUD
    """
    repository = Mock(spec=CoffeeLotRepository)

    # Configurar save() para retornar el objeto que recibe (comportamiento típico de repositorios)
    def save_side_effect(coffee_lot):
        # Simular asignación de ID si no tiene uno
        if coffee_lot.id is None:
            coffee_lot.id = 1
        return coffee_lot

    repository.save.side_effect = save_side_effect
    repository.find_by_id.return_value = None
    repository.find_by_producer_id.return_value = []
    repository.find_by_lot_number.return_value = None
    repository.exists_by_lot_number.return_value = False
    repository.delete.return_value = None

    return repository


# ============================================================================
# FIXTURES DE SERVICIOS DE DOMINIO - COFFEE LOT MANAGEMENT
# ============================================================================

@pytest.fixture
def mock_lot_number_service():
    """
    Simula el servicio de generación de números de lote.

    Returns:
        Mock: LotNumberGeneratorService mockeado
    """
    service = Mock(spec=LotNumberGeneratorService)
    service.generate_lot_number.return_value = "LOT-2024-0001"
    return service


# ============================================================================
# FIXTURES DE SERVICIOS DE APLICACIÓN - GRAIN CLASSIFICATION
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
# FIXTURES DE SERVICIOS DE APLICACIÓN - COFFEE LOT MANAGEMENT
# ============================================================================

@pytest.fixture
def coffee_lot_command_service(mock_db_session, mock_coffee_lot_repository, mock_lot_number_service):
    """
    Servicio de comandos para Coffee Lot configurado con dependencias mockeadas.

    Args:
        mock_db_session: Sesión de base de datos mockeada
        mock_coffee_lot_repository: Repositorio mockeado
        mock_lot_number_service: Servicio generador de números mockeado

    Returns:
        CoffeeLotCommandService: Servicio listo para testing
    """
    service = CoffeeLotCommandService(db=mock_db_session)
    service.repository = mock_coffee_lot_repository
    service.lot_number_service = mock_lot_number_service
    return service


@pytest.fixture
def coffee_lot_query_service(mock_db_session, mock_coffee_lot_repository):
    """
    Servicio de consultas para Coffee Lot configurado con dependencias mockeadas.

    Args:
        mock_db_session: Sesión de base de datos mockeada
        mock_coffee_lot_repository: Repositorio mockeado

    Returns:
        CoffeeLotQueryService: Servicio listo para testing
    """
    service = CoffeeLotQueryService(db=mock_db_session)
    service.repository = mock_coffee_lot_repository
    return service


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
    # Markers para User Stories de Grain Classification
    config.addinivalue_line(
        "markers", "us12: Tests para User Story 12 - Detección de Defectos"
    )
    config.addinivalue_line(
        "markers", "us13: Tests para User Story 13 - Análisis de Color y Uniformidad"
    )
    config.addinivalue_line(
        "markers", "us14: Tests para User Story 14 - Clasificación por Estándares"
    )

    # Markers para User Stories de Coffee Lot Management
    config.addinivalue_line(
        "markers", "us06: Tests para User Story 06 - Creación de Lotes"
    )
    config.addinivalue_line(
        "markers", "us07: Tests para User Story 07 - Edición de Información de Lote"
    )
    config.addinivalue_line(
        "markers", "us08: Tests para User Story 08 - Visualización de Lotes por Productor"
    )
    config.addinivalue_line(
        "markers", "us09: Tests para User Story 09 - Visualización de Lotes por Cooperativa"
    )
    config.addinivalue_line(
        "markers", "us10: Tests para User Story 10 - Búsqueda Rápida de Lotes"
    )
    config.addinivalue_line(
        "markers", "us11: Tests para User Story 11 - Eliminación de Lotes"
    )

    # Markers generales
    config.addinivalue_line(
        "markers", "integration: Tests de integración completos"
    )
    config.addinivalue_line(
        "markers", "slow: Tests que toman más tiempo en ejecutar"
    )