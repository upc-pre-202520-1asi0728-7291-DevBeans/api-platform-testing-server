"""
Integration Tests para US13: Análisis de Color y Uniformidad

User Story:
Como productor o cooperativa, deseo medir objetivamente color y tamaño
para estandarizar calidad entre lotes de diferentes productores asociados.

Ejecutar todos los tests de esta US:
    pytest us_13_integration_test.py -v

Ejecutar un test específico:
    pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_medicion_porcentajes_color_precisa -v
"""

import pytest
import logging
from grain_classification.domain.model.aggregates.classification_session import SessionStatus

logger = logging.getLogger(__name__)


@pytest.mark.us13
@pytest.mark.integration
class TestUS13AnalisisColorUniformidad:
    """
    Suite de tests de integración para el análisis objetivo de color y tamaño,
    permitiendo estandarización de calidad entre lotes.
    """

    def test_medicion_porcentajes_color_precisa(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que el sistema retorne porcentajes precisos para todas las clases de color.

        GIVEN un grano procesado
        WHEN se analiza su color
        THEN debe retornar porcentajes para todas las clases de color
        """
        logger.info("=== TEST: Medicion precisa de porcentajes de color ===")

        # Arrange: Configurar predicción detallada
        logger.info("ARRANGE: Configurando predictor ML con porcentajes detallados")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 15.5,
            'Medium': 70.2,
            'Dark': 10.3,
            'Green': 4.0
        }
        logger.info("Prediccion configurada: Light=15.5%, Medium=70.2%, Dark=10.3%, Green=4.0%")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con analisis de color")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar análisis de color completo
        logger.info("ASSERT: Verificando analisis de color completo")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for analysis in session.analyses:
            color_percentages = analysis.color_percentages
            logger.info(f"Porcentajes de color detectados: {color_percentages}")

            # Verificar que existen todas las clases de color
            expected_classes = ['Light', 'Medium', 'Dark', 'Green']
            for color_class in expected_classes:
                assert color_class in color_percentages, \
                    f"Debe existir la clase de color: {color_class}"
            logger.info("OK: Todas las clases de color presentes")

            # Verificar que los valores suman aproximadamente 100%
            total = sum(color_percentages.values())
            logger.info(f"Suma total de porcentajes: {total:.2f}%")
            assert 95.0 <= total <= 105.0, \
                f"Los porcentajes deben sumar ~100%, suma actual: {total}%"
            logger.info("OK: Porcentajes suman aproximadamente 100%")

    def test_medicion_tamano_grano_area(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que el sistema mida y reporte el área de cada grano correctamente.

        GIVEN granos de diferentes tamaños
        WHEN se extraen características morfológicas
        THEN debe medir y reportar el área de cada grano
        """
        logger.info("=== TEST: Medicion de tamano de granos (area) ===")

        # Arrange: Configurar diferentes tamaños de granos
        logger.info("ARRANGE: Configurando CV con granos de diferentes tamanos")
        mock_cv_service.extract_all_features.side_effect = [
            {'area': 800.0, 'perimeter': 150.0, 'circularity': 0.8, 'has_cracks': 'False'},
            {'area': 2500.0, 'perimeter': 220.0, 'circularity': 0.85, 'has_cracks': 'False'}
        ]
        logger.info("Granos configurados: area=800.0 (pequeno), area=2500.0 (grande)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con medicion de tamano")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar mediciones de tamaño
        logger.info("ASSERT: Verificando mediciones de area")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        assert len(session.analyses) == 2, \
            "Deben haberse analizado 2 granos"
        logger.info(f"OK: Se analizaron {len(session.analyses)} granos")

        for i, analysis in enumerate(session.analyses):
            area = analysis.features.get('area')
            logger.info(f"Grano {i+1}: area={area}")

            assert 'area' in analysis.features, \
                "Las características deben incluir el área"
            assert area > 0, \
                "El área debe ser un valor positivo"
            assert isinstance(area, (int, float)), \
                "El área debe ser un valor numérico"

        logger.info("OK: Areas medidas correctamente para todos los granos")

    def test_bonificacion_por_tamano_grande(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que granos grandes reciban bonificación en su score de calidad.

        GIVEN granos de tamaño grande (>2000 área)
        WHEN se calcula la calidad final
        THEN debe aplicar bonificación al score
        """
        logger.info("=== TEST: Bonificacion por tamano grande ===")

        # Arrange: Configurar grano grande
        logger.info("ARRANGE: Configurando CV con grano grande (area=2500)")
        mock_cv_service.extract_all_features.return_value = {
            'area': 2500.0,  # Grano grande (> 2000)
            'perimeter': 220.0,
            'circularity': 0.85,
            'has_cracks': 'False'
        }
        logger.info("Mock configurado: area=2500 (grande), circularidad=0.85")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con grano grande")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar bonificación
        logger.info("ASSERT: Verificando bonificacion por tamano")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for analysis in session.analyses:
            adjustments = analysis.quality_assessment.get('adjustments', {})
            size_bonus = adjustments.get('size_bonus', 0)
            base_score = analysis.quality_assessment['base_score']
            final_score = analysis.final_score

            logger.info(f"Analisis: base_score={base_score:.3f}, size_bonus={size_bonus:.3f}, final_score={final_score:.3f}")

            # Debe tener bonificación de tamaño
            assert 'size_bonus' in adjustments, \
                "Granos grandes deben tener bonificación de tamaño"
            assert size_bonus > 0, \
                f"La bonificación debe ser positiva, obtuvo: {size_bonus}"
            logger.info("OK: Bonificacion de tamano positiva aplicada")

            # Score final debe ser mayor o igual que base
            assert final_score >= base_score, \
                f"Score final ({final_score}) debe ser >= base ({base_score})"
            logger.info("OK: Score final mayor o igual al base (bonificacion aplicada)")

    def test_penalizacion_por_tamano_pequeno(
            self,
            classification_service,
            mock_cv_service,
            sample_image_bytes
    ):
        """
        Verifica que granos pequeños reciban penalización en su score de calidad.

        GIVEN granos de tamaño pequeño (<500 área)
        WHEN se calcula la calidad final
        THEN debe aplicar penalización al score
        """
        logger.info("=== TEST: Penalizacion por tamano pequeno ===")

        # Arrange: Configurar grano pequeño
        logger.info("ARRANGE: Configurando CV con grano pequeno (area=400)")
        mock_cv_service.extract_all_features.return_value = {
            'area': 400.0,  # Grano pequeño (< 500)
            'perimeter': 100.0,
            'circularity': 0.8,
            'has_cracks': 'False'
        }
        logger.info("Mock configurado: area=400 (pequeno), circularidad=0.8")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con grano pequeno")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar penalización
        logger.info("ASSERT: Verificando penalizacion por tamano")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for analysis in session.analyses:
            adjustments = analysis.quality_assessment.get('adjustments', {})
            size_penalty = adjustments.get('size_penalty', 0)

            logger.info(f"Penalizacion de tamano: {size_penalty:.3f}")

            # Debe tener penalización de tamaño
            assert 'size_penalty' in adjustments, \
                "Granos pequeños deben tener penalización de tamaño"
            assert size_penalty < 0, \
                f"La penalización debe ser negativa, obtuvo: {size_penalty}"
            logger.info("OK: Penalizacion de tamano negativa aplicada correctamente")

    def test_uniformidad_lote_homogeneo(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que el sistema detecte alta uniformidad en lotes homogéneos.

        GIVEN un lote con granos de color uniforme
        WHEN se genera el reporte del lote
        THEN debe indicar alta uniformidad en distribución de categorías
        """
        logger.info("=== TEST: Deteccion de uniformidad en lote homogeneo ===")

        # Arrange: Configurar lote uniforme (todos Medium)
        logger.info("ARRANGE: Configurando predictor ML con lote uniforme (85% Medium)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 85.0,  # Todos similares -> alta uniformidad
            'Dark': 5.0,
            'Green': 5.0
        }
        logger.info("Prediccion configurada: Medium=85% (alta uniformidad)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion de lote homogeneo")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar uniformidad
        logger.info("ASSERT: Verificando alta uniformidad en distribucion")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        report = session.classification_result
        distribution = report['category_distribution']

        logger.info(f"Distribucion de categorias: {distribution}")

        # Encontrar categoría predominante
        max_percentage = max(
            cat['percentage'] for cat in distribution.values()
        )
        logger.info(f"Porcentaje maximo en una categoria: {max_percentage:.2f}%")

        # Alta uniformidad: >70% en una categoría
        assert max_percentage >= 70.0, \
            f"Lote homogéneo debe tener >70% en una categoría, obtuvo: {max_percentage}%"
        logger.info("OK: Alta uniformidad detectada (>70% en una categoria)")

    def test_almacenamiento_caracteristicas_completas(
            self,
            classification_service,
            sample_image_bytes
    ):
        """
        Verifica que todas las características medidas se almacenen correctamente.

        GIVEN un grano procesado
        WHEN se completa el análisis
        THEN debe almacenar todas las características medidas
        """
        logger.info("=== TEST: Almacenamiento de caracteristicas completas ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion completa")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar almacenamiento completo
        logger.info("ASSERT: Verificando almacenamiento de todas las caracteristicas")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for i, analysis in enumerate(session.analyses):
            logger.info(f"Verificando grano {i+1}...")

            # Verificar características morfológicas
            assert analysis.features is not None, \
                "Debe existir diccionario de características"
            logger.info(f"  Features: {list(analysis.features.keys())}")

            required_features = ['area', 'perimeter', 'circularity', 'has_cracks']
            for feature in required_features:
                assert feature in analysis.features, \
                    f"Debe existir la característica: {feature}"
            logger.info("  OK: Caracteristicas morfologicas completas")

            # Verificar análisis de color
            assert analysis.color_percentages is not None, \
                "Debe existir análisis de color"
            assert len(analysis.color_percentages) == 4, \
                "Debe haber 4 clases de color"
            logger.info(f"  Color percentages: {analysis.color_percentages}")
            logger.info("  OK: Analisis de color completo")

            # Verificar evaluación de calidad
            assert analysis.quality_assessment is not None, \
                "Debe existir evaluación de calidad"

            required_assessment_keys = ['base_score', 'final_score', 'quality_category']
            for key in required_assessment_keys:
                assert key in analysis.quality_assessment, \
                    f"La evaluación debe incluir: {key}"
            logger.info(f"  Quality assessment keys: {list(analysis.quality_assessment.keys())}")
            logger.info("  OK: Evaluacion de calidad completa")

        logger.info("OK: Todas las caracteristicas almacenadas correctamente")

    def test_comparacion_lotes_diferentes_productores(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que el sistema permita comparar lotes de diferentes productores.

        GIVEN múltiples lotes procesados
        WHEN se analizan sus características
        THEN debe permitir comparación objetiva entre productores
        """
        logger.info("=== TEST: Comparacion de lotes de diferentes productores ===")

        # Arrange & Act: Procesar dos lotes de diferentes productores
        # Lote 1 - Productor A (calidad alta)
        logger.info("ARRANGE & ACT: Procesando Lote 1 (Productor A - calidad alta)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 80.0,
            'Medium': 15.0,
            'Dark': 3.0,
            'Green': 2.0
        }
        logger.info("Lote 1: Light=80% (calidad alta)")

        session1 = classification_service.start_classification_session(
            coffee_lot_id=100,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Lote 1 procesado: status={session1.status}")

        # Lote 2 - Productor B (calidad media)
        logger.info("Procesando Lote 2 (Productor B - calidad media)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 20.0,
            'Medium': 60.0,
            'Dark': 15.0,
            'Green': 5.0
        }
        logger.info("Lote 2: Medium=60% (calidad media)")

        session2 = classification_service.start_classification_session(
            coffee_lot_id=200,
            image_bytes=sample_image_bytes,
            user_id=2
        )
        logger.info(f"Lote 2 procesado: status={session2.status}")

        # Assert: Verificar que ambas sesiones son comparables
        logger.info("ASSERT: Verificando comparabilidad de lotes")
        assert session1.status == SessionStatus.COMPLETED
        assert session2.status == SessionStatus.COMPLETED
        logger.info("OK: Ambas sesiones completadas exitosamente")

        # Verificar que tienen estructura de datos comparable
        report1 = session1.classification_result
        report2 = session2.classification_result

        # Ambos deben tener las mismas métricas
        for key in ['overall_batch_quality', 'category_distribution', 'average_score']:
            assert key in report1, f"Reporte 1 debe incluir {key}"
            assert key in report2, f"Reporte 2 debe incluir {key}"
        logger.info("OK: Ambos reportes tienen estructura comparable")

        # La calidad debe reflejar la diferencia en los colores
        quality1 = report1['overall_batch_quality']
        quality2 = report2['overall_batch_quality']

        logger.info(f"Calidad Lote 1 (Productor A): {quality1:.2f}")
        logger.info(f"Calidad Lote 2 (Productor B): {quality2:.2f}")

        assert quality1 > quality2, \
            f"Lote con más granos Light debe tener mayor calidad: {quality1} vs {quality2}"
        logger.info("OK: Lote de mayor calidad (Productor A) tiene mejor score")
        logger.info("OK: Comparacion objetiva entre productores exitosa")