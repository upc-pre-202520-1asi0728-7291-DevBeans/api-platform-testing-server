"""
Integration Tests para US08: Visualización de Lotes por Productor

User Story:
Como productor, deseo ver todos mis lotes en una vista simple para revisar
mi histórico de producción sin complejidad técnica.

Ejecutar todos los tests de esta US:
    pytest us_08_integration_test.py -v

Ejecutar un test específico:
    pytest us_08_integration_test.py::TestUS08VisualizacionLotesProductor::test_listar_todos_lotes_productor -v
"""

import pytest
import logging
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.queries.get_coffee_lots_by_producer_query import (
    GetCoffeeLotsByProducerQuery
)

logger = logging.getLogger(__name__)


@pytest.mark.us08
@pytest.mark.integration
class TestUS08VisualizacionLotesProductor:
    """
    Suite de tests de integración para visualización de lotes por productor.
    """

    def test_listar_todos_lotes_productor(
            self,
            coffee_lot_query_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que un productor pueda ver todos sus lotes registrados.

        GIVEN un productor con múltiples lotes
        WHEN solicita ver sus lotes
        THEN debe recibir todos sus lotes
        """
        logger.info("=== TEST: Listar todos los lotes de un productor ===")

        # Arrange: Crear lotes del productor
        logger.info("ARRANGE: Creando lotes de prueba para productor ID=1")
        producer_lots = [
            CoffeeLot(
                lot_number="LOT-2024-0001",
                producer_id=1,
                harvest_date=date(2024, 5, 15),
                coffee_variety=CoffeeVariety.TYPICA,
                quantity=500.0,
                processing_method=ProcessingMethod.WASHED,
                latitude=-12.0464,
                longitude=-77.0428
            ),
            CoffeeLot(
                lot_number="LOT-2024-0002",
                producer_id=1,
                harvest_date=date(2024, 6, 10),
                coffee_variety=CoffeeVariety.CATURRA,
                quantity=300.0,
                processing_method=ProcessingMethod.NATURAL,
                latitude=-12.0464,
                longitude=-77.0428
            ),
            CoffeeLot(
                lot_number="LOT-2024-0003",
                producer_id=1,
                harvest_date=date(2024, 7, 5),
                coffee_variety=CoffeeVariety.BOURBON,
                quantity=450.0,
                processing_method=ProcessingMethod.HONEY,
                latitude=-12.0464,
                longitude=-77.0428
            )
        ]

        for i, lot in enumerate(producer_lots):
            lot.id = i + 1

        logger.info(f"Creados {len(producer_lots)} lotes de prueba")
        for lot in producer_lots:
            logger.info(f"  - {lot.lot_number}: {lot.quantity}kg, {lot.coffee_variety.value}")

        mock_coffee_lot_repository.find_by_producer_id.return_value = producer_lots

        query = GetCoffeeLotsByProducerQuery(producer_id=1)

        # Act: Consultar lotes
        logger.info("ACT: Consultando lotes del productor")
        lots = coffee_lot_query_service.handle_get_coffee_lots_by_producer(query)
        logger.info(f"Lotes recuperados: {len(lots)}")

        # Assert: Verificar resultados
        logger.info("ASSERT: Verificando que se recuperaron todos los lotes")
        assert len(lots) == 3, "Debe retornar todos los lotes del productor"
        logger.info("OK: Cantidad correcta de lotes recuperados")

        assert all(lot.producer_id == 1 for lot in lots), \
            "Todos los lotes deben pertenecer al productor"
        logger.info("OK: Todos los lotes pertenecen al productor correcto")

        lot_numbers = [lot.lot_number for lot in lots]
        assert "LOT-2024-0001" in lot_numbers, "Debe incluir el primer lote"
        assert "LOT-2024-0002" in lot_numbers, "Debe incluir el segundo lote"
        assert "LOT-2024-0003" in lot_numbers, "Debe incluir el tercer lote"
        logger.info("OK: Todos los lotes esperados estan presentes")

    def test_filtrar_lotes_por_estado(
            self,
            coffee_lot_query_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se puedan filtrar lotes por estado.

        GIVEN un productor con lotes en diferentes estados
        WHEN filtra por estado específico
        THEN debe recibir solo lotes en ese estado
        """
        logger.info("=== TEST: Filtrar lotes por estado ===")

        # Arrange: Crear lotes con diferentes estados
        logger.info("ARRANGE: Creando lotes con diferentes estados")
        lot1 = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot1.id = 1
        lot1.status = LotStatus.REGISTERED

        lot2 = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot2.id = 2
        lot2.status = LotStatus.CLASSIFIED

        logger.info(f"Lote 1: {lot1.lot_number}, estado={lot1.status.value}")
        logger.info(f"Lote 2: {lot2.lot_number}, estado={lot2.status.value}")

        mock_coffee_lot_repository.find_by_producer_id.return_value = [lot1, lot2]

        query = GetCoffeeLotsByProducerQuery(
            producer_id=1,
            status="REGISTERED"
        )
        logger.info(f"Filtrando por estado: {query.status}")

        # Act: Consultar lotes filtrados
        logger.info("ACT: Consultando lotes filtrados por estado")
        lots = coffee_lot_query_service.handle_get_coffee_lots_by_producer(query)
        logger.info(f"Lotes recuperados: {len(lots)}")

        # Assert: Verificar filtrado
        logger.info("ASSERT: Verificando filtrado por estado")
        assert len(lots) == 1, "Debe retornar solo lotes en estado REGISTERED"
        logger.info("OK: Cantidad correcta de lotes filtrados")

        assert lots[0].status == LotStatus.REGISTERED, \
            "El lote debe estar en estado REGISTERED"
        logger.info(f"OK: Lote filtrado correcto: {lots[0].lot_number}, estado={lots[0].status.value}")

    def test_filtrar_lotes_por_anio_cosecha(
            self,
            coffee_lot_query_service,
            mock_coffee_lot_repository
    ):
        """
        Verifica que se puedan filtrar lotes por año de cosecha.

        GIVEN un productor con lotes de diferentes años
        WHEN filtra por año específico
        THEN debe recibir solo lotes de ese año
        """
        logger.info("=== TEST: Filtrar lotes por anio de cosecha ===")

        # Arrange: Crear lotes de diferentes años
        logger.info("ARRANGE: Creando lotes de diferentes anios")
        lot_2023 = CoffeeLot(
            lot_number="LOT-2023-0001",
            producer_id=1,
            harvest_date=date(2023, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_2023.id = 1

        lot_2024 = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_2024.id = 2

        logger.info(f"Lote 2023: {lot_2023.lot_number}, fecha={lot_2023.harvest_date}")
        logger.info(f"Lote 2024: {lot_2024.lot_number}, fecha={lot_2024.harvest_date}")

        mock_coffee_lot_repository.find_by_producer_id.return_value = [lot_2023, lot_2024]

        query = GetCoffeeLotsByProducerQuery(
            producer_id=1,
            harvest_year=2024
        )
        logger.info(f"Filtrando por anio: {query.harvest_year}")

        # Act: Consultar lotes filtrados
        logger.info("ACT: Consultando lotes del anio 2024")
        lots = coffee_lot_query_service.handle_get_coffee_lots_by_producer(query)
        logger.info(f"Lotes recuperados: {len(lots)}")

        # Assert: Verificar filtrado
        logger.info("ASSERT: Verificando filtrado por anio")
        assert len(lots) == 1, "Debe retornar solo lotes del año 2024"
        logger.info("OK: Cantidad correcta de lotes del anio 2024")

        assert lots[0].harvest_date.year == 2024, \
            "El lote debe ser del año 2024"
        logger.info(f"OK: Lote filtrado correcto: {lots[0].lot_number}, anio={lots[0].harvest_date.year}")