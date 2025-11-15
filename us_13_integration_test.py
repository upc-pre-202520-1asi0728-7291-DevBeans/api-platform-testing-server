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
from grain_classification.domain.model.aggregates.classification_session import SessionStatus


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
        # Arrange: Configurar predicción detallada
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 15.5,
            'Medium': 70.2,
            'Dark': 10.3,
            'Green': 4.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar análisis de color completo
        assert session.status == SessionStatus.COMPLETED

        for analysis in session.analyses:
            color_percentages = analysis.color_percentages

            # Verificar que existen todas las clases de color
            expected_classes = ['Light', 'Medium', 'Dark', 'Green']
            for color_class in expected_classes:
                assert color_class in color_percentages, \
                    f"Debe existir la clase de color: {color_class}"

            # Verificar que los valores suman aproximadamente 100%
            total = sum(color_percentages.values())
            assert 95.0 <= total <= 105.0, \
                f"Los porcentajes deben sumar ~100%, suma actual: {total}%"

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
        # Arrange: Configurar diferentes tamaños de granos
        mock_cv_service.extract_all_features.side_effect = [
            {'area': 800.0, 'perimeter': 150.0, 'circularity': 0.8, 'has_cracks': 'False'},
            {'area': 2500.0, 'perimeter': 220.0, 'circularity': 0.85, 'has_cracks': 'False'}
        ]

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar mediciones de tamaño
        assert session.status == SessionStatus.COMPLETED
        assert len(session.analyses) == 2, \
            "Deben haberse analizado 2 granos"

        for analysis in session.analyses:
            assert 'area' in analysis.features, \
                "Las características deben incluir el área"
            assert analysis.features['area'] > 0, \
                "El área debe ser un valor positivo"
            assert isinstance(analysis.features['area'], (int, float)), \
                "El área debe ser un valor numérico"

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
        # Arrange: Configurar grano grande
        mock_cv_service.extract_all_features.return_value = {
            'area': 2500.0,  # Grano grande (> 2000)
            'perimeter': 220.0,
            'circularity': 0.85,
            'has_cracks': 'False'
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar bonificación
        assert session.status == SessionStatus.COMPLETED

        for analysis in session.analyses:
            adjustments = analysis.quality_assessment.get('adjustments', {})

            # Debe tener bonificación de tamaño
            assert 'size_bonus' in adjustments, \
                "Granos grandes deben tener bonificación de tamaño"
            assert adjustments['size_bonus'] > 0, \
                f"La bonificación debe ser positiva, obtuvo: {adjustments['size_bonus']}"

            # Score final debe ser mayor o igual que base
            base_score = analysis.quality_assessment['base_score']
            assert analysis.final_score >= base_score, \
                f"Score final ({analysis.final_score}) debe ser ≥ base ({base_score})"

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
        # Arrange: Configurar grano pequeño
        mock_cv_service.extract_all_features.return_value = {
            'area': 400.0,  # Grano pequeño (< 500)
            'perimeter': 100.0,
            'circularity': 0.8,
            'has_cracks': 'False'
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar penalización
        assert session.status == SessionStatus.COMPLETED

        for analysis in session.analyses:
            adjustments = analysis.quality_assessment.get('adjustments', {})

            # Debe tener penalización de tamaño
            assert 'size_penalty' in adjustments, \
                "Granos pequeños deben tener penalización de tamaño"
            assert adjustments['size_penalty'] < 0, \
                f"La penalización debe ser negativa, obtuvo: {adjustments['size_penalty']}"

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
        # Arrange: Configurar lote uniforme (todos Medium)
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 85.0,  # Todos similares -> alta uniformidad
            'Dark': 5.0,
            'Green': 5.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar uniformidad
        assert session.status == SessionStatus.COMPLETED

        report = session.classification_result
        distribution = report['category_distribution']

        # Encontrar categoría predominante
        max_percentage = max(
            cat['percentage'] for cat in distribution.values()
        )

        # Alta uniformidad: >70% en una categoría
        assert max_percentage >= 70.0, \
            f"Lote homogéneo debe tener >70% en una categoría, obtuvo: {max_percentage}%"

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
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar almacenamiento completo
        assert session.status == SessionStatus.COMPLETED

        for analysis in session.analyses:
            # Verificar características morfológicas
            assert analysis.features is not None, \
                "Debe existir diccionario de características"

            required_features = ['area', 'perimeter', 'circularity', 'has_cracks']
            for feature in required_features:
                assert feature in analysis.features, \
                    f"Debe existir la característica: {feature}"

            # Verificar análisis de color
            assert analysis.color_percentages is not None, \
                "Debe existir análisis de color"
            assert len(analysis.color_percentages) == 4, \
                "Debe haber 4 clases de color"

            # Verificar evaluación de calidad
            assert analysis.quality_assessment is not None, \
                "Debe existir evaluación de calidad"

            required_assessment_keys = ['base_score', 'final_score', 'quality_category']
            for key in required_assessment_keys:
                assert key in analysis.quality_assessment, \
                    f"La evaluación debe incluir: {key}"

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
        # Arrange & Act: Procesar dos lotes de diferentes productores
        # Lote 1 - Productor A (calidad alta)
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 80.0,
            'Medium': 15.0,
            'Dark': 3.0,
            'Green': 2.0
        }

        session1 = classification_service.start_classification_session(
            coffee_lot_id=100,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Lote 2 - Productor B (calidad media)
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 20.0,
            'Medium': 60.0,
            'Dark': 15.0,
            'Green': 5.0
        }

        session2 = classification_service.start_classification_session(
            coffee_lot_id=200,
            image_bytes=sample_image_bytes,
            user_id=2
        )

        # Assert: Verificar que ambas sesiones son comparables
        assert session1.status == SessionStatus.COMPLETED
        assert session2.status == SessionStatus.COMPLETED

        # Verificar que tienen estructura de datos comparable
        report1 = session1.classification_result
        report2 = session2.classification_result

        # Ambos deben tener las mismas métricas
        for key in ['overall_batch_quality', 'category_distribution', 'average_score']:
            assert key in report1, f"Reporte 1 debe incluir {key}"
            assert key in report2, f"Reporte 2 debe incluir {key}"

        # La calidad debe reflejar la diferencia en los colores
        quality1 = report1['overall_batch_quality']
        quality2 = report2['overall_batch_quality']

        assert quality1 > quality2, \
            f"Lote con más granos Light debe tener mayor calidad: {quality1} vs {quality2}"