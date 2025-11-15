"""
conftest_coffee_lot.py - Configuración de fixtures para tests de Coffee Lot Management

Este archivo contiene fixtures específicos para los tests de integración del
bounded context Coffee Lot Management (US06-US11).
"""

from unittest.mock import Mock

import pytest

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
# FIXTURES DE REPOSITORIOS
# ============================================================================

@pytest.fixture
def mock_coffee_lot_repository():
    """
    Simula el repositorio de lotes de café.

    Returns:
        Mock: CoffeeLotRepository mockeado con operaciones CRUD
    """
    repository = Mock(spec=CoffeeLotRepository)

    # Configurar comportamiento por defecto
    repository.save.return_value = None  # Retorna el objeto guardado
    repository.find_by_id.return_value = None
    repository.find_by_producer_id.return_value = []
    repository.find_by_lot_number.return_value = None
    repository.exists_by_lot_number.return_value = False
    repository.delete.return_value = None

    return repository


# ============================================================================
# FIXTURES DE SERVICIOS DE DOMINIO
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
# FIXTURES DE SERVICIOS DE APLICACIÓN
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
# CONFIGURACIÓN DE PYTEST
# ============================================================================

def pytest_configure(config):
    """
    Configuración adicional de pytest para Coffee Lot Management tests.
    Registra markers personalizados para categorizar tests.
    """
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