"""
Integration Tests para US07: Edición de Información de Lote

User Story:
Como productor o cooperativa, deseo editar datos de mis lotes cuando detecte
errores o cambios en la información de cosecha.

Ejecutar todos los tests de esta US:
    pytest us_07_integration_test.py -v

Ejecutar un test específico:
    pytest us_07_integration_test.py::TestUS07EdicionInformacionLote::test_actualizar_cantidad_lote -v
"""

import pytest
import logging
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.commands.update_coffee_lot_command import UpdateCoffeeLotCommand

logger = logging.getLogger(__name__)


@pytest.mark.us07
@pytest.mark.integration
class TestUS07EdicionInformacionLote:
    """
    Suite de tests de integración para la edición de información de lotes.
    """

    def test_actualizar_cantidad_lote(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se pueda actualizar la cantidad de un lote existente.

        GIVEN un lote registrado con cantidad inicial
        WHEN se actualiza la cantidad
        THEN debe reflejarse el cambio correctamente
        """
        logger.info("=== TEST: Actualizar cantidad de lote ===")

        # Arrange: Crear lote existente
        logger.info("ARRANGE: Creando lote existente para edicion")
        existing_lot = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        existing_lot.id = 1
        logger.info(f"Lote existente: ID={existing_lot.id}, cantidad original={existing_lot.quantity}kg")

        mock_coffee_lot_repository.find_by_id.return_value = existing_lot
        mock_coffee_lot_repository.save.return_value = existing_lot

        command = UpdateCoffeeLotCommand(
            lot_id=1,
            quantity=600.0
        )
        logger.info(f"Nueva cantidad a actualizar: {command.quantity}kg")

        # Act: Actualizar lote
        logger.info("ACT: Actualizando cantidad del lote")
        updated_lot = coffee_lot_command_service.handle_update_coffee_lot(command)
        logger.info(f"Lote actualizado: nueva cantidad={updated_lot.quantity}kg")

        # Assert: Verificar actualización
        logger.info("ASSERT: Verificando actualizacion exitosa")
        assert updated_lot.quantity == 600.0, "La cantidad debe haberse actualizado"
        logger.info("OK: Cantidad actualizada correctamente")

        assert updated_lot.id == 1, "Debe ser el mismo lote"
        assert updated_lot.lot_number == "LOT-2024-0001", "El número de lote no debe cambiar"
        logger.info("OK: Identidad del lote preservada")

    def test_no_permitir_edicion_lote_clasificado(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que no se permita editar lotes que ya fueron clasificados.

        GIVEN un lote con estado CLASSIFIED
        WHEN se intenta actualizar
        THEN debe rechazarse la operación
        """
        logger.info("=== TEST: No permitir edicion de lote clasificado ===")

        # Arrange: Crear lote clasificado
        logger.info("ARRANGE: Creando lote ya clasificado (estado CLASSIFIED)")
        classified_lot = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=400.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        classified_lot.id = 2
        classified_lot.status = LotStatus.CLASSIFIED
        logger.info(f"Lote clasificado: ID={classified_lot.id}, estado={classified_lot.status.value}")

        mock_coffee_lot_repository.find_by_id.return_value = classified_lot

        command = UpdateCoffeeLotCommand(
            lot_id=2,
            quantity=450.0
        )

        # Act & Assert: Intentar actualización y verificar error
        logger.info("ACT & ASSERT: Intentando actualizar lote clasificado")
        with pytest.raises(Exception) as exc_info:
            coffee_lot_command_service.handle_update_coffee_lot(command)

        logger.info(f"Excepcion capturada: {type(exc_info.value).__name__}")
        logger.info(f"Mensaje de error: {str(exc_info.value)}")

        assert "classification" in str(exc_info.value).lower(), \
            "El error debe indicar que no se puede editar después de clasificar"
        logger.info("OK: Proteccion de lotes clasificados funcionando correctamente")

    def test_actualizar_metodo_procesamiento(
            self,
            coffee_lot_command_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se pueda actualizar el método de procesamiento.

        GIVEN un lote con método de procesamiento inicial
        WHEN se actualiza el método
        THEN debe cambiar correctamente
        """
        logger.info("=== TEST: Actualizar metodo de procesamiento ===")

        # Arrange: Crear lote con procesamiento WASHED
        logger.info("ARRANGE: Creando lote con procesamiento WASHED")
        existing_lot = CoffeeLot(
            lot_number="LOT-2024-0003",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.BOURBON,
            quantity=350.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        existing_lot.id = 3
        logger.info(f"Metodo original: {existing_lot.processing_method.value}")

        mock_coffee_lot_repository.find_by_id.return_value = existing_lot
        mock_coffee_lot_repository.save.return_value = existing_lot

        command = UpdateCoffeeLotCommand(
            lot_id=3,
            processing_method="HONEY"
        )
        logger.info(f"Nuevo metodo a aplicar: {command.processing_method}")

        # Act: Actualizar método
        logger.info("ACT: Actualizando metodo de procesamiento")
        updated_lot = coffee_lot_command_service.handle_update_coffee_lot(command)
        logger.info(f"Metodo actualizado: {updated_lot.processing_method.value}")

        # Assert: Verificar actualización
        logger.info("ASSERT: Verificando cambio de metodo")
        assert updated_lot.processing_method == ProcessingMethod.HONEY, \
            "El método de procesamiento debe haberse actualizado"
        logger.info("OK: Metodo de procesamiento actualizado correctamente")

        assert updated_lot.coffee_variety == CoffeeVariety.BOURBON, \
            "Otros campos no deben cambiar"
        logger.info("OK: Otros campos preservados correctamente")