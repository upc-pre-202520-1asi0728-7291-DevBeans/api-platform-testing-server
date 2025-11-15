"""
Integration Tests para US06: Creación de Lotes

User Story:
Como productor o cooperativa, deseo registrar mis lotes con información básica
(fecha cosecha, variedad, origen) para organizar mi producción de forma eficiente.

Ejecutar todos los tests de esta US:
    pytest us_06_integration_test.py -v

Ejecutar un test específico:
    pytest us_06_integration_test.py::TestUS06CreacionLotes::test_registrar_lote_exitoso -v
"""

import pytest
import logging
from datetime import date, timedelta
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.commands.register_coffee_lot_command import RegisterCoffeeLotCommand

logger = logging.getLogger(__name__)


@pytest.mark.us06
@pytest.mark.integration
class TestUS06CreacionLotes:
    """
    Suite de tests de integración para la creación de lotes de café.
    """

    def test_registrar_lote_exitoso(
            self,
            coffee_lot_command_service,
            mock_lot_number_service
    ):
        """
        Verifica que se pueda registrar un lote exitosamente con información básica.

        GIVEN un productor con datos válidos de un lote
        WHEN se registra el lote
        THEN debe crearse exitosamente con número único de lote
        """
        logger.info("=== TEST: Registrar lote exitosamente ===")

        # Arrange: Preparar comando de registro
        logger.info("ARRANGE: Preparando datos del lote")
        mock_lot_number_service.generate_lot_number.return_value = "LOT-2024-0001"

        command = RegisterCoffeeLotCommand(
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety="TYPICA",
            quantity=500.0,
            processing_method="WASHED",
            latitude=-12.0464,
            longitude=-77.0428,
            altitude=1500.0,
            soil_type="Volcanic",
            climate_zone="Tropical"
        )
        logger.info(f"Comando creado: producer_id={command.producer_id}, variety={command.coffee_variety}")
        logger.info(f"Cantidad: {command.quantity}kg, Fecha: {command.harvest_date}")

        # Act: Registrar lote
        logger.info("ACT: Registrando lote en el sistema")
        coffee_lot = coffee_lot_command_service.handle_register_coffee_lot(command)
        logger.info(f"Lote registrado con ID: {coffee_lot.id}")
        logger.info(f"Numero de lote: {coffee_lot.lot_number}")

        # Assert: Verificar creación exitosa
        logger.info("ASSERT: Verificando creacion exitosa del lote")
        assert coffee_lot is not None, "El lote debe haberse creado"
        logger.info("OK: Lote creado correctamente")

        assert coffee_lot.lot_number == "LOT-2024-0001", "Debe tener número de lote único"
        logger.info(f"OK: Numero de lote asignado: {coffee_lot.lot_number}")

        assert coffee_lot.producer_id == 1, "Debe pertenecer al productor correcto"
        assert coffee_lot.coffee_variety == CoffeeVariety.TYPICA, "Debe tener la variedad correcta"
        assert coffee_lot.quantity == 500.0, "Debe tener la cantidad correcta"
        assert coffee_lot.status == LotStatus.REGISTERED, "Estado inicial debe ser REGISTERED"
        logger.info(f"OK: Estado inicial: {coffee_lot.status.value}")
        logger.info("OK: Todos los datos basicos almacenados correctamente")

    def test_validacion_fecha_cosecha_futura(
            self,
            coffee_lot_command_service
    ):
        """
        Verifica que no se permita registrar lotes con fecha de cosecha futura.

        GIVEN un comando con fecha de cosecha futura
        WHEN se intenta registrar el lote
        THEN debe rechazarse con error de validación
        """
        logger.info("=== TEST: Validacion de fecha de cosecha futura ===")

        # Arrange: Preparar comando con fecha futura
        logger.info("ARRANGE: Preparando comando con fecha futura (invalida)")
        future_date = date.today() + timedelta(days=30)
        logger.info(f"Fecha futura intentada: {future_date}")

        command = RegisterCoffeeLotCommand(
            producer_id=1,
            harvest_date=future_date,
            coffee_variety="CATURRA",
            quantity=300.0,
            processing_method="NATURAL",
            latitude=-12.0464,
            longitude=-77.0428
        )

        # Act & Assert: Intentar registro y verificar error
        logger.info("ACT & ASSERT: Intentando registrar con fecha invalida")
        with pytest.raises(Exception) as exc_info:
            coffee_lot_command_service.handle_register_coffee_lot(command)

        logger.info(f"Excepcion capturada: {type(exc_info.value).__name__}")
        logger.info(f"Mensaje de error: {str(exc_info.value)}")

        assert "future" in str(exc_info.value).lower(), \
            "El error debe indicar que la fecha no puede ser futura"
        logger.info("OK: Validacion de fecha futura funcionando correctamente")

    def test_generacion_numero_lote_unico(
            self,
            coffee_lot_command_service,
            mock_lot_number_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que cada lote reciba un número único generado automáticamente.

        GIVEN múltiples registros de lotes
        WHEN se generan números de lote
        THEN cada uno debe ser único
        """
        logger.info("=== TEST: Generacion de numero de lote unico ===")

        # Arrange: Configurar generación de números únicos
        logger.info("ARRANGE: Configurando generacion de numeros unicos")
        mock_lot_number_service.generate_lot_number.side_effect = [
            "LOT-2024-0001",
            "LOT-2024-0002",
            "LOT-2024-0003"
        ]
        logger.info("Numeros configurados: LOT-2024-0001, 0002, 0003")

        lot_numbers = []

        # Act: Registrar múltiples lotes
        logger.info("ACT: Registrando 3 lotes")
        for i in range(3):
            command = RegisterCoffeeLotCommand(
                producer_id=i + 1,
                harvest_date=date(2024, 5, 15),
                coffee_variety="TYPICA",
                quantity=200.0,
                processing_method="WASHED",
                latitude=-12.0464,
                longitude=-77.0428
            )
            coffee_lot = coffee_lot_command_service.handle_register_coffee_lot(command)
            lot_numbers.append(coffee_lot.lot_number)
            logger.info(f"Lote {i + 1} registrado: {coffee_lot.lot_number}")

        # Assert: Verificar unicidad
        logger.info("ASSERT: Verificando unicidad de numeros de lote")
        assert len(lot_numbers) == len(set(lot_numbers)), \
            "Todos los números de lote deben ser únicos"
        logger.info(f"Numeros generados: {lot_numbers}")
        logger.info("OK: Todos los numeros de lote son unicos")

        assert all("LOT-2024-" in num for num in lot_numbers), \
            "Todos deben seguir el formato correcto"
        logger.info("OK: Formato de numero de lote correcto")