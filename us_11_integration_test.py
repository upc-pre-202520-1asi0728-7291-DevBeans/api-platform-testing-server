"""
Integration Tests para US11: Eliminación de Lotes

User Story:
Como usuario, deseo eliminar lotes erróneos o duplicados para mantener
limpia mi base de datos de producción.

Ejecutar todos los tests de esta US:
    pytest us_11_integration_test.py -v

Ejecutar un test específico:
    pytest us_11_integration_test.py::TestUS11EliminacionLotes::test_eliminar_lote_registrado -v
"""

import pytest
import logging
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.commands.delete_coffee_lot_command import DeleteCoffeeLotCommand

logger = logging.getLogger(__name__)


@pytest.mark.us11
@pytest.mark.integration
class TestUS11EliminacionLotes:
    """
    Suite de tests de integración para eliminación de lotes.
    """

    def test_eliminar_lote_registrado(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se pueda eliminar un lote en estado REGISTERED.

        GIVEN un lote en estado REGISTERED
        WHEN se solicita su eliminación
        THEN debe eliminarse exitosamente
        """
        logger.info("=== TEST: Eliminar lote en estado REGISTERED ===")

        # Arrange: Crear lote en estado REGISTERED
        logger.info("ARRANGE: Creando lote en estado REGISTERED para eliminacion")
        coffee_lot = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        coffee_lot.id = 1
        coffee_lot.status = LotStatus.REGISTERED
        logger.info(f"Lote creado: ID={coffee_lot.id}, numero={coffee_lot.lot_number}")
        logger.info(f"Estado: {coffee_lot.status.value}")

        mock_coffee_lot_repository.find_by_id.return_value = coffee_lot
        mock_coffee_lot_repository.delete.return_value = None

        command = DeleteCoffeeLotCommand(
            lot_id=1,
            deletion_reason="Lote duplicado por error"
        )
        logger.info(f"Razon de eliminacion: {command.deletion_reason}")

        # Act: Eliminar lote
        logger.info("ACT: Eliminando lote del sistema")
        coffee_lot_command_service.handle_delete_coffee_lot(command)
        logger.info("Comando de eliminacion ejecutado")

        # Assert: Verificar eliminación
        logger.info("ASSERT: Verificando que se llamo al metodo delete")
        mock_coffee_lot_repository.delete.assert_called_once_with(coffee_lot)
        logger.info("OK: Lote eliminado exitosamente del repositorio")

    def test_no_eliminar_lote_clasificado(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que no se pueda eliminar un lote ya clasificado.

        GIVEN un lote en estado CLASSIFIED
        WHEN se intenta eliminar
        THEN debe rechazarse la operación
        """
        logger.info("=== TEST: No permitir eliminar lote CLASSIFIED ===")

        # Arrange: Crear lote clasificado
        logger.info("ARRANGE: Creando lote en estado CLASSIFIED")
        coffee_lot = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=400.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        coffee_lot.id = 2
        coffee_lot.status = LotStatus.CLASSIFIED
        logger.info(f"Lote creado: ID={coffee_lot.id}, estado={coffee_lot.status.value}")
        logger.info("Este lote NO deberia poder eliminarse")

        mock_coffee_lot_repository.find_by_id.return_value = coffee_lot

        command = DeleteCoffeeLotCommand(
            lot_id=2,
            deletion_reason="Intento de eliminar lote clasificado"
        )

        # Act & Assert: Intentar eliminación y verificar error
        logger.info("ACT & ASSERT: Intentando eliminar lote clasificado")
        with pytest.raises(Exception) as exc_info:
            coffee_lot_command_service.handle_delete_coffee_lot(command)

        logger.info(f"Excepcion capturada: {type(exc_info.value).__name__}")
        logger.info(f"Mensaje de error: {str(exc_info.value)}")

        assert "REGISTERED" in str(exc_info.value), \
            "El error debe indicar que solo se pueden eliminar lotes en estado REGISTERED"
        logger.info("OK: Proteccion de lotes clasificados funcionando correctamente")

    def test_verificar_existencia_antes_eliminar(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se valide la existencia del lote antes de eliminar.

        GIVEN un ID de lote inexistente
        WHEN se intenta eliminar
        THEN debe retornar error de no encontrado
        """
        logger.info("=== TEST: Verificar existencia de lote antes de eliminar ===")

        # Arrange: Configurar lote inexistente
        logger.info("ARRANGE: Configurando repositorio para lote inexistente")
        mock_coffee_lot_repository.find_by_id.return_value = None
        logger.info("Lote ID=999 no existe en el sistema")

        command = DeleteCoffeeLotCommand(
            lot_id=999,
            deletion_reason="Intento de eliminar lote inexistente"
        )

        # Act & Assert: Intentar eliminación y verificar error
        logger.info("ACT & ASSERT: Intentando eliminar lote inexistente")
        with pytest.raises(Exception) as exc_info:
            coffee_lot_command_service.handle_delete_coffee_lot(command)

        logger.info(f"Excepcion capturada: {type(exc_info.value).__name__}")
        logger.info(f"Mensaje de error: {str(exc_info.value)}")

        assert "not found" in str(exc_info.value).lower(), \
            "El error debe indicar que el lote no fue encontrado"
        logger.info("OK: Validacion de existencia funcionando correctamente")