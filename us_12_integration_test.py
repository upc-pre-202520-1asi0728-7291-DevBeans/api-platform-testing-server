"""
Integration Tests para US12: Detección de Defectos Críticos

User Story:
Como productor o cooperativa, deseo que el sistema detecte defectos
que causan rechazos internacionales (quiebres, manchas, moho, broca)
para prevenir pérdidas económicas.

Ejecutar todos los tests de esta US:
    pytest us_12_integration_test.py -v

Ejecutar un test específico:
    pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_detectar_granos_con_grietas -v
"""

import pytest
import logging
from grain_classification.domain.model.aggregates.classification_session import SessionStatus

logger = logging.getLogger(__name__)


@pytest.mark.us12
@pytest.mark.integration
class TestUS12DeteccionDefectosCriticos:
    """
    Suite de tests de integración para la detección de defectos críticos
    en granos de café según estándares internacionales.
    """

    def test_detectar_granos_con_grietas(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que el sistema detecte granos con grietas mediante análisis CV.

        GIVEN un lote con granos que presentan grietas
        WHEN se procesa la imagen
        THEN el sistema debe detectar y reportar granos con grietas
        """
        logger.info("=== TEST: Deteccion de granos con grietas ===")

        # Arrange: Configurar grano con grietas
        logger.info("ARRANGE: Configurando mock de CV con grano con grietas detectadas")
        mock_cv_service.extract_all_features.return_value = {
            'area': 1500.0,
            'perimeter': 200.0,
            'circularity': 0.85,
            'has_cracks': 'True'  # Grano con grietas detectadas
        }
        logger.info("Mock configurado: area=1500.0, has_cracks=True")

        # Act: Procesar clasificación
        logger.info("ACT: Iniciando sesion de clasificacion con imagen de test")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")
        logger.info(f"Total de granos analizados: {session.total_grains_analyzed}")

        # Assert: Verificar detección exitosa
        logger.info("ASSERT: Verificando deteccion exitosa de grietas")
        assert session.status == SessionStatus.COMPLETED, \
            "La sesión debe completarse exitosamente"
        logger.info("OK: Sesion completada exitosamente")

        assert session.total_grains_analyzed > 0, \
            "Debe haber granos analizados"
        logger.info(f"OK: Se analizaron {session.total_grains_analyzed} granos")

        # Verificar que al menos un grano tiene grietas detectadas
        analyses_with_cracks = [
            a for a in session.analyses
            if a.features.get('has_cracks') == 'True'
        ]
        logger.info(f"Granos con grietas detectados: {len(analyses_with_cracks)}")

        assert len(analyses_with_cracks) > 0, \
            "Debe detectarse al menos un grano con grietas"
        logger.info("OK: Test completado exitosamente")

    def test_detectar_granos_oscuros_defectuosos(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que granos oscuros (moho/fermentación) se clasifiquen como defectuosos.

        GIVEN un lote con granos oscuros (indicador de moho/fermentación)
        WHEN se clasifica la imagen
        THEN el sistema debe identificarlos como categoría C (defectuosos)
        """
        logger.info("=== TEST: Deteccion de granos oscuros defectuosos ===")

        # Arrange: Configurar predicción de grano oscuro
        logger.info("ARRANGE: Configurando predictor ML con grano oscuro (80% Dark)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 10.0,
            'Dark': 80.0,  # Grano predominantemente oscuro
            'Green': 5.0
        }
        logger.info("Prediccion configurada: Dark=80% (indicador de defecto)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con grano oscuro")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar clasificación baja
        logger.info("ASSERT: Verificando clasificacion como defectuoso")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        dark_grains = [
            a for a in session.analyses
            if a.quality_assessment.get('color_class') == 'Dark'
        ]
        logger.info(f"Granos oscuros detectados: {len(dark_grains)}")

        assert len(dark_grains) > 0, \
            "Debe detectarse al menos un grano oscuro"
        logger.info("OK: Se detectaron granos oscuros")

        for grain in dark_grains:
            logger.info(f"Grano oscuro: categoria={grain.final_category}, score={grain.final_score:.3f}")
            assert grain.final_category in ['C', 'B'], \
                f"Grano oscuro debe ser categoría baja, obtuvo: {grain.final_category}"
            assert grain.final_score < 0.7, \
                f"Grano oscuro debe tener score bajo, obtuvo: {grain.final_score}"

        logger.info("OK: Todos los granos oscuros clasificados correctamente")

    def test_detectar_granos_verdes_inmaduros(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que granos verdes (inmaduros) se identifiquen como defectos de maduración.

        GIVEN un lote con granos verdes (inmaduros)
        WHEN se procesa la clasificación
        THEN el sistema debe identificarlos como defectos de maduración
        """
        logger.info("=== TEST: Deteccion de granos verdes inmaduros ===")

        # Arrange: Configurar grano verde inmaduro
        logger.info("ARRANGE: Configurando predictor ML con grano verde (80% Green)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 10.0,
            'Dark': 5.0,
            'Green': 80.0  # Grano inmaduro
        }
        logger.info("Prediccion configurada: Green=80% (grano inmaduro)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con grano verde")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar detección de granos verdes
        logger.info("ASSERT: Verificando clasificacion como categoria C")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        green_grains = [
            a for a in session.analyses
            if a.quality_assessment.get('color_class') == 'Green'
        ]
        logger.info(f"Granos verdes detectados: {len(green_grains)}")

        assert len(green_grains) > 0, \
            "Debe detectarse al menos un grano verde"
        logger.info("OK: Se detectaron granos verdes")

        for grain in green_grains:
            logger.info(f"Grano verde: categoria={grain.final_category}, score={grain.final_score:.3f}")
            assert grain.final_category == 'C', \
                f"Grano verde debe ser categoría C, obtuvo: {grain.final_category}"
            assert grain.final_score <= 0.5, \
                f"Grano verde debe tener score muy bajo, obtuvo: {grain.final_score}"

        logger.info("OK: Todos los granos verdes clasificados como categoria C")

    def test_penalizacion_por_forma_irregular(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que granos con forma irregular reciban penalización en su score.

        GIVEN granos con forma irregular (baja circularidad)
        WHEN se evalúan las características morfológicas
        THEN el sistema debe aplicar penalización al score final
        """
        logger.info("=== TEST: Penalizacion por forma irregular ===")

        # Arrange: Configurar grano con forma muy irregular
        logger.info("ARRANGE: Configurando CV con grano de forma irregular (circularidad=0.5)")
        mock_cv_service.extract_all_features.return_value = {
            'area': 1500.0,
            'perimeter': 300.0,
            'circularity': 0.5,  # Forma muy irregular (< 0.7)
            'has_cracks': 'False'
        }
        logger.info("Mock configurado: circularidad=0.5 (muy irregular)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con grano irregular")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar penalización
        logger.info("ASSERT: Verificando penalizacion por forma irregular")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for analysis in session.analyses:
            base_score = analysis.quality_assessment['base_score']
            final_score = analysis.final_score

            logger.info(f"Grano analizado: base_score={base_score:.3f}, final_score={final_score:.3f}")

            # El score final debe ser menor o igual que el base por penalización
            assert final_score <= base_score, \
                f"Score final ({final_score}) debe ser <= base ({base_score})"
            logger.info("OK: Score final menor o igual al base (penalizacion aplicada)")

            # Debe existir penalización de forma
            adjustments = analysis.quality_assessment.get('adjustments', {})
            assert 'shape_penalty' in adjustments, \
                "Debe existir penalización por forma irregular"

            shape_penalty = adjustments['shape_penalty']
            logger.info(f"Penalizacion de forma: {shape_penalty:.3f}")

            assert shape_penalty < 0, \
                "La penalización de forma debe ser negativa"
            logger.info("OK: Penalizacion de forma aplicada correctamente")

    def test_reporte_estadistico_defectos_lote(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que el reporte final incluya estadísticas sobre defectos detectados.

        GIVEN un lote procesado con múltiples granos
        WHEN se genera el reporte final
        THEN debe incluir estadísticas sobre defectos detectados
        """
        logger.info("=== TEST: Reporte estadistico de defectos del lote ===")

        # Arrange: Configurar lote mixto (algunos defectuosos)
        logger.info("ARRANGE: Configurando lote mixto (1 bueno, 1 defectuoso)")
        mock_ml_predictor.predict_color_percentages.side_effect = [
            {'Light': 90.0, 'Medium': 5.0, 'Dark': 3.0, 'Green': 2.0},  # Bueno
            {'Light': 10.0, 'Medium': 10.0, 'Dark': 75.0, 'Green': 5.0},  # Defecto
        ]
        logger.info("Granos configurados: 1 Light (bueno), 1 Dark (defectuoso)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion del lote mixto")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar reporte completo
        logger.info("ASSERT: Verificando estructura del reporte")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        assert session.classification_result is not None, \
            "Debe existir un reporte de clasificación"
        logger.info("OK: Reporte de clasificacion generado")

        report = session.classification_result

        # Verificar estructura del reporte
        assert 'total_beans_analyzed' in report, \
            "Reporte debe incluir total de granos analizados"
        logger.info(f"Total de granos analizados: {report['total_beans_analyzed']}")

        assert 'category_distribution' in report, \
            "Reporte debe incluir distribución por categorías"
        logger.info("OK: Distribucion por categorias presente")

        assert 'quality_breakdown' in report, \
            "Reporte debe incluir desglose de calidad"
        logger.info("OK: Desglose de calidad presente")

        # Verificar que se reportan categorías de calidad
        breakdown = report['quality_breakdown']
        logger.info(f"Categorias en breakdown: {list(breakdown.keys())}")

        assert 'poor' in breakdown, \
            "Debe existir categoría 'poor' para granos defectuosos"
        logger.info(f"Granos defectuosos (poor): {breakdown['poor']}")

        assert breakdown['poor'] >= 0, \
            "Conteo de granos defectuosos debe ser no negativo"
        logger.info("OK: Reporte estadistico completo y valido")

    def test_manejo_error_imagen_invalida(
            self,
            classification_service,
            mock_cv_service
    ):
        """
        Verifica que el sistema maneje graciosamente imágenes inválidas o corruptas.

        GIVEN una imagen que no puede procesarse
        WHEN se intenta clasificar
        THEN debe fallar graciosamente con mensaje claro
        """
        logger.info("=== TEST: Manejo de error con imagen invalida ===")

        # Arrange: Simular error de carga
        logger.info("ARRANGE: Configurando CV para simular fallo de carga de imagen")
        mock_cv_service.load_image_from_bytes.return_value = None
        logger.info("Mock configurado para retornar None (imagen invalida)")

        # Act: Intentar procesar imagen inválida
        logger.info("ACT: Intentando procesar imagen invalida")
        session = classification_service.start_classification_session(
            coffee_lot_id=400,
            image_bytes=b'invalid_data',
            user_id=4
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar manejo de error
        logger.info("ASSERT: Verificando manejo gracioso del error")
        assert session.status == SessionStatus.FAILED, \
            "La sesión debe marcar como FAILED cuando la imagen es inválida"
        logger.info("OK: Status marcado como FAILED")

        assert 'error' in session.classification_result, \
            "El resultado debe contener mensaje de error"
        logger.info(f"Mensaje de error: {session.classification_result.get('error')}")

        assert len(session.analyses) == 0, \
            "No debe haber análisis cuando la imagen es inválida"
        logger.info("OK: Error manejado graciosamente, sin analisis generados")

    def test_manejo_error_sin_granos_detectados(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que el sistema maneje el caso donde no se detectan granos en la imagen.

        GIVEN una imagen válida, pero sin granos visibles
        WHEN se segmenta
        THEN debe fallar indicando que no hay granos
        """
        logger.info("=== TEST: Manejo de error sin granos detectados ===")

        # Arrange: Simular ausencia de granos
        logger.info("ARRANGE: Configurando CV para simular imagen sin granos")
        mock_cv_service.segment_beans.return_value = []
        logger.info("Mock configurado para retornar lista vacia (sin granos)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando imagen sin granos")
        session = classification_service.start_classification_session(
            coffee_lot_id=500,
            image_bytes=sample_image_bytes,
            user_id=5
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar fallo apropiado
        logger.info("ASSERT: Verificando mensaje de error apropiado")
        assert session.status == SessionStatus.FAILED, \
            "La sesión debe fallar cuando no hay granos"
        logger.info("OK: Status marcado como FAILED")

        assert 'No se detectaron granos' in session.classification_result['error'], \
            "El error debe indicar claramente que no se detectaron granos"
        logger.info(f"Mensaje de error: {session.classification_result['error']}")
        logger.info("OK: Error manejado correctamente con mensaje descriptivo")