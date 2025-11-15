"""
Integration Tests para US09: Visualización de Lotes por Cooperativa

User Story:
Como cooperativa, deseo visualizar lotes agrupados por productor asociado
para facilitar la gestión y seguimiento de múltiples orígenes.

Ejecutar todos los tests de esta US:
    pytest us_09_integration_test.py -v

Ejecutar un test específico:
    pytest us_09_integration_test.py::TestUS09VisualizacionLotesCooperativa::test_agrupar_lotes_por_productor -v
"""

import pytest
import logging
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.queries.search_coffee_lots_query import SearchCoffeeLotsQuery

logger = logging.getLogger(__name__)


@pytest.mark.us09
@pytest.mark.integration
class TestUS09VisualizacionLotesCooperativa:
    """
    Suite de tests de integración para visualización de lotes por cooperativa.
    """

    def test_agrupar_lotes_por_productor(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que una cooperativa pueda ver lotes agrupados por productor.

        GIVEN múltiples productores con sus lotes
        WHEN la cooperativa consulta todos los lotes
        THEN debe poder identificar lotes por productor
        """
        logger.info("=== TEST: Agrupar lotes por productor ===")

        # Arrange: Crear lotes de múltiples productores
        logger.info("ARRANGE: Creando lotes de 3 productores diferentes")

        # Productor 1 - 2 lotes
        lot1_p1 = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot1_p1.id = 1

        lot2_p1 = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot2_p1.id = 2

        # Productor 2 - 1 lote
        lot1_p2 = CoffeeLot(
            lot_number="LOT-2024-0003",
            producer_id=2,
            harvest_date=date(2024, 5, 20),
            coffee_variety=CoffeeVariety.BOURBON,
            quantity=400.0,
            processing_method=ProcessingMethod.HONEY,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot1_p2.id = 3

        all_lots = [lot1_p1, lot2_p1, lot1_p2]
        logger.info(f"Total de lotes creados: {len(all_lots)}")
        logger.info(f"Productor 1: 2 lotes")
        logger.info(f"Productor 2: 1 lote")

        # Mock query result
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = all_lots

        # Act: Consultar todos los lotes y agrupar
        logger.info("ACT: Consultando y agrupando lotes por productor")
        query = SearchCoffeeLotsQuery()
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)

        # Agrupar por productor
        grouped_lots = {}
        for lot in lots:
            if lot.producer_id not in grouped_lots:
                grouped_lots[lot.producer_id] = []
            grouped_lots[lot.producer_id].append(lot)

        logger.info(f"Productores encontrados: {list(grouped_lots.keys())}")
        for producer_id, producer_lots in grouped_lots.items():
            logger.info(f"  Productor {producer_id}: {len(producer_lots)} lotes")

        # Assert: Verificar agrupación
        logger.info("ASSERT: Verificando agrupacion correcta")
        assert len(grouped_lots) == 2, "Debe haber lotes de 2 productores"
        logger.info("OK: Numero correcto de productores")

        assert len(grouped_lots[1]) == 2, "Productor 1 debe tener 2 lotes"
        logger.info(f"OK: Productor 1 tiene {len(grouped_lots[1])} lotes")

        assert len(grouped_lots[2]) == 1, "Productor 2 debe tener 1 lote"
        logger.info(f"OK: Productor 2 tiene {len(grouped_lots[2])} lote")

    def test_visualizar_estadisticas_por_productor(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que se puedan calcular estadísticas por productor.

        GIVEN lotes de múltiples productores
        WHEN se calculan estadísticas
        THEN debe mostrar totales por productor
        """
        logger.info("=== TEST: Visualizar estadisticas por productor ===")

        # Arrange: Crear lotes con cantidades conocidas
        logger.info("ARRANGE: Creando lotes con cantidades especificas")

        lot1_p1 = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot1_p1.id = 1

        lot2_p1 = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot2_p1.id = 2

        all_lots = [lot1_p1, lot2_p1]
        logger.info(f"Productor 1: Lote 1 = {lot1_p1.quantity}kg, Lote 2 = {lot2_p1.quantity}kg")

        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = all_lots

        # Act: Calcular estadísticas
        logger.info("ACT: Calculando estadisticas por productor")
        query = SearchCoffeeLotsQuery()
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)

        # Calcular total por productor
        producer_stats = {}
        for lot in lots:
            if lot.producer_id not in producer_stats:
                producer_stats[lot.producer_id] = {
                    'total_lots': 0,
                    'total_quantity': 0.0
                }
            producer_stats[lot.producer_id]['total_lots'] += 1
            producer_stats[lot.producer_id]['total_quantity'] += lot.quantity

        logger.info(f"Estadisticas calculadas:")
        for producer_id, stats in producer_stats.items():
            logger.info(f"  Productor {producer_id}: {stats['total_lots']} lotes, {stats['total_quantity']}kg")

        # Assert: Verificar estadísticas
        logger.info("ASSERT: Verificando estadisticas calculadas")
        assert producer_stats[1]['total_lots'] == 2, \
            "Productor 1 debe tener 2 lotes"
        logger.info("OK: Numero de lotes correcto")

        assert producer_stats[1]['total_quantity'] == 800.0, \
            "Productor 1 debe tener 800kg totales"
        logger.info(f"OK: Cantidad total correcta: {producer_stats[1]['total_quantity']}kg")

    def test_filtrar_lotes_cooperativa_por_variedad(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que la cooperativa pueda filtrar lotes por variedad de café.

        GIVEN lotes de diferentes variedades
        WHEN se filtra por variedad específica
        THEN debe mostrar solo lotes de esa variedad
        """
        logger.info("=== TEST: Filtrar lotes de cooperativa por variedad ===")

        # Arrange: Crear lotes de diferentes variedades
        logger.info("ARRANGE: Creando lotes de diferentes variedades")

        lot_typica = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_typica.id = 1

        lot_caturra = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=2,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_caturra.id = 2

        logger.info(f"Lote 1: {lot_typica.lot_number}, variedad={lot_typica.coffee_variety.value}")
        logger.info(f"Lote 2: {lot_caturra.lot_number}, variedad={lot_caturra.coffee_variety.value}")

        # Mock query para filtrar solo TYPICA
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [lot_typica]

        # Act: Filtrar por variedad
        logger.info("ACT: Filtrando lotes por variedad TYPICA")
        query = SearchCoffeeLotsQuery(variety="TYPICA")
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)
        logger.info(f"Lotes recuperados: {len(lots)}")

        # Assert: Verificar filtrado
        logger.info("ASSERT: Verificando filtrado por variedad")
        assert len(lots) == 1, "Debe retornar solo lotes de variedad TYPICA"
        logger.info("OK: Cantidad correcta de lotes filtrados")

        assert lots[0].coffee_variety == CoffeeVariety.TYPICA, \
            "El lote debe ser de variedad TYPICA"
        logger.info(f"OK: Variedad correcta: {lots[0].coffee_variety.value}")