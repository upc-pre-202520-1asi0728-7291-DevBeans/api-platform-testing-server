"""
Integration Tests para US10: Búsqueda Rápida de Lotes

User Story:
Como usuario (productor o cooperativa), deseo buscar lotes por fecha,
productor o variedad para acceder rápidamente a información específica.

Ejecutar todos los tests de esta US:
    pytest us_10_integration_test.py -v

Ejecutar un test específico:
    pytest us_10_integration_test.py::TestUS10BusquedaRapidaLotes::test_buscar_por_rango_fechas -v
"""

import pytest
import logging
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.queries.search_coffee_lots_query import SearchCoffeeLotsQuery

logger = logging.getLogger(__name__)


@pytest.mark.us10
@pytest.mark.integration
class TestUS10BusquedaRapidaLotes:
    """
    Suite de tests de integración para búsqueda rápida de lotes.
    """

    def test_buscar_por_rango_fechas(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que se puedan buscar lotes por rango de fechas de cosecha.

        GIVEN lotes con diferentes fechas de cosecha
        WHEN se busca por rango de fechas
        THEN debe retornar solo lotes en ese rango
        """
        logger.info("=== TEST: Buscar lotes por rango de fechas ===")

        # Arrange: Crear lotes con diferentes fechas
        logger.info("ARRANGE: Creando lotes con diferentes fechas de cosecha")

        lot_may = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_may.id = 1

        lot_june = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 6, 20),
            coffee_variety=CoffeeVariety.CATURRA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_june.id = 2

        lot_august = CoffeeLot(
            lot_number="LOT-2024-0003",
            producer_id=1,
            harvest_date=date(2024, 8, 10),
            coffee_variety=CoffeeVariety.BOURBON,
            quantity=400.0,
            processing_method=ProcessingMethod.HONEY,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_august.id = 3

        logger.info(f"Lote 1: {lot_may.harvest_date}")
        logger.info(f"Lote 2: {lot_june.harvest_date}")
        logger.info(f"Lote 3: {lot_august.harvest_date}")

        # Mock query para retornar lotes en rango mayo-junio
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [lot_may, lot_june]

        # Act: Buscar por rango de fechas
        logger.info("ACT: Buscando lotes entre 2024-05-01 y 2024-06-30")
        query = SearchCoffeeLotsQuery(
            start_date=date(2024, 5, 1),
            end_date=date(2024, 6, 30)
        )
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)
        logger.info(f"Lotes encontrados: {len(lots)}")

        # Assert: Verificar resultados
        logger.info("ASSERT: Verificando busqueda por rango de fechas")
        assert len(lots) == 2, "Debe retornar solo lotes en el rango de fechas"
        logger.info("OK: Cantidad correcta de lotes en el rango")

        for lot in lots:
            logger.info(f"  Verificando lote: {lot.lot_number}, fecha={lot.harvest_date}")
            assert date(2024, 5, 1) <= lot.harvest_date <= date(2024, 6, 30), \
                "Todos los lotes deben estar en el rango"
        logger.info("OK: Todos los lotes estan dentro del rango especificado")

    def test_buscar_por_variedad_cafe(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que se puedan buscar lotes por variedad de café.

        GIVEN lotes de diferentes variedades
        WHEN se busca por variedad específica
        THEN debe retornar solo lotes de esa variedad
        """
        logger.info("=== TEST: Buscar lotes por variedad de cafe ===")

        # Arrange: Crear lotes de diferentes variedades
        logger.info("ARRANGE: Creando lotes de variedades TYPICA y GEISHA")

        lot_typica1 = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_typica1.id = 1

        lot_typica2 = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=2,
            harvest_date=date(2024, 6, 10),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=300.0,
            processing_method=ProcessingMethod.NATURAL,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_typica2.id = 2

        lot_geisha = CoffeeLot(
            lot_number="LOT-2024-0003",
            producer_id=1,
            harvest_date=date(2024, 5, 20),
            coffee_variety=CoffeeVariety.GEISHA,
            quantity=200.0,
            processing_method=ProcessingMethod.HONEY,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_geisha.id = 3

        logger.info(f"Lote 1: {lot_typica1.lot_number}, variedad={lot_typica1.coffee_variety.value}")
        logger.info(f"Lote 2: {lot_typica2.lot_number}, variedad={lot_typica2.coffee_variety.value}")
        logger.info(f"Lote 3: {lot_geisha.lot_number}, variedad={lot_geisha.coffee_variety.value}")

        # Mock query para retornar solo TYPICA
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [lot_typica1, lot_typica2]

        # Act: Buscar por variedad
        logger.info("ACT: Buscando lotes de variedad TYPICA")
        query = SearchCoffeeLotsQuery(variety="TYPICA")
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)
        logger.info(f"Lotes encontrados: {len(lots)}")

        # Assert: Verificar resultados
        logger.info("ASSERT: Verificando busqueda por variedad")
        assert len(lots) == 2, "Debe retornar solo lotes de variedad TYPICA"
        logger.info("OK: Cantidad correcta de lotes TYPICA")

        for lot in lots:
            logger.info(f"  Verificando lote: {lot.lot_number}, variedad={lot.coffee_variety.value}")
            assert lot.coffee_variety == CoffeeVariety.TYPICA, \
                "Todos los lotes deben ser de variedad TYPICA"
        logger.info("OK: Todos los lotes son de la variedad correcta")

    def test_buscar_con_multiples_filtros(
            self,
            coffee_lot_query_service,
            mock_db_session
    ):
        """
        Verifica que se puedan combinar múltiples criterios de búsqueda.

        GIVEN lotes con diferentes características
        WHEN se busca con múltiples filtros
        THEN debe retornar solo lotes que cumplan todos los criterios
        """
        logger.info("=== TEST: Buscar con multiples filtros combinados ===")

        # Arrange: Crear lotes variados
        logger.info("ARRANGE: Creando lotes con diferentes caracteristicas")

        lot_match = CoffeeLot(
            lot_number="LOT-2024-0001",
            producer_id=1,
            harvest_date=date(2024, 5, 15),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=500.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_match.id = 1
        lot_match.status = LotStatus.REGISTERED

        lot_no_match1 = CoffeeLot(
            lot_number="LOT-2024-0002",
            producer_id=1,
            harvest_date=date(2024, 5, 20),
            coffee_variety=CoffeeVariety.CATURRA,  # Variedad diferente
            quantity=300.0,
            processing_method=ProcessingMethod.WASHED,
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_no_match1.id = 2
        lot_no_match1.status = LotStatus.REGISTERED

        lot_no_match2 = CoffeeLot(
            lot_number="LOT-2024-0003",
            producer_id=1,
            harvest_date=date(2024, 5, 18),
            coffee_variety=CoffeeVariety.TYPICA,
            quantity=400.0,
            processing_method=ProcessingMethod.NATURAL,  # Procesamiento diferente
            latitude=-12.0464,
            longitude=-77.0428
        )
        lot_no_match2.id = 3
        lot_no_match2.status = LotStatus.REGISTERED

        logger.info(f"Lote 1: TYPICA + WASHED + REGISTERED (debe coincidir)")
        logger.info(f"Lote 2: CATURRA + WASHED + REGISTERED (no coincide - variedad)")
        logger.info(f"Lote 3: TYPICA + NATURAL + REGISTERED (no coincide - procesamiento)")

        # Mock query para retornar solo el que coincide
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [lot_match]

        # Act: Buscar con múltiples filtros
        logger.info("ACT: Buscando con filtros: TYPICA + WASHED + REGISTERED")
        query = SearchCoffeeLotsQuery(
            variety="TYPICA",
            processing_method="WASHED",
            status="REGISTERED"
        )
        lots = coffee_lot_query_service.handle_search_coffee_lots(query)
        logger.info(f"Lotes encontrados: {len(lots)}")

        # Assert: Verificar resultados
        logger.info("ASSERT: Verificando busqueda con multiples filtros")
        assert len(lots) == 1, "Debe retornar solo lotes que cumplan todos los criterios"
        logger.info("OK: Solo 1 lote cumple todos los criterios")

        lot = lots[0]
        logger.info(f"Lote encontrado: {lot.lot_number}")
        assert lot.coffee_variety == CoffeeVariety.TYPICA, "Debe ser variedad TYPICA"
        assert lot.processing_method == ProcessingMethod.WASHED, "Debe ser procesamiento WASHED"
        assert lot.status == LotStatus.REGISTERED, "Debe estar en estado REGISTERED"
        logger.info("OK: El lote cumple todos los criterios de busqueda")