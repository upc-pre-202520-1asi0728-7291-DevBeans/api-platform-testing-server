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
from grain_classification.domain.model.aggregates.classification_session import SessionStatus


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
        # Arrange: Configurar grano con grietas
        mock_cv_service.extract_all_features.return_value = {
            'area': 1500.0,
            'perimeter': 200.0,
            'circularity': 0.85,
            'has_cracks': 'True'  # Grano con grietas detectadas
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar detección exitosa
        assert session.status == SessionStatus.COMPLETED, \
            "La sesión debe completarse exitosamente"
        assert session.total_grains_analyzed > 0, \
            "Debe haber granos analizados"

        # Verificar que al menos un grano tiene grietas detectadas
        analyses_with_cracks = [
            a for a in session.analyses
            if a.features.get('has_cracks') == 'True'
        ]
        assert len(analyses_with_cracks) > 0, \
            "Debe detectarse al menos un grano con grietas"

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
        # Arrange: Configurar predicción de grano oscuro
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 10.0,
            'Dark': 80.0,  # Grano predominantemente oscuro
            'Green': 5.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar clasificación baja
        assert session.status == SessionStatus.COMPLETED

        dark_grains = [
            a for a in session.analyses
            if a.quality_assessment.get('color_class') == 'Dark'
        ]
        assert len(dark_grains) > 0, \
            "Debe detectarse al menos un grano oscuro"

        for grain in dark_grains:
            assert grain.final_category in ['C', 'B'], \
                f"Grano oscuro debe ser categoría baja, obtuvo: {grain.final_category}"
            assert grain.final_score < 0.7, \
                f"Grano oscuro debe tener score bajo, obtuvo: {grain.final_score}"

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
        # Arrange: Configurar grano verde inmaduro
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 10.0,
            'Dark': 5.0,
            'Green': 80.0  # Grano inmaduro
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar detección de granos verdes
        assert session.status == SessionStatus.COMPLETED

        green_grains = [
            a for a in session.analyses
            if a.quality_assessment.get('color_class') == 'Green'
        ]
        assert len(green_grains) > 0, \
            "Debe detectarse al menos un grano verde"

        for grain in green_grains:
            assert grain.final_category == 'C', \
                f"Grano verde debe ser categoría C, obtuvo: {grain.final_category}"
            assert grain.final_score <= 0.5, \
                f"Grano verde debe tener score muy bajo, obtuvo: {grain.final_score}"

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
        # Arrange: Configurar grano con forma muy irregular
        mock_cv_service.extract_all_features.return_value = {
            'area': 1500.0,
            'perimeter': 300.0,
            'circularity': 0.5,  # Forma muy irregular (< 0.7)
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
            base_score = analysis.quality_assessment['base_score']
            final_score = analysis.final_score

            # El score final debe ser menor o igual que el base por penalización
            assert final_score <= base_score, \
                f"Score final ({final_score}) debe ser ≤ base ({base_score})"

            # Debe existir penalización de forma
            adjustments = analysis.quality_assessment.get('adjustments', {})
            assert 'shape_penalty' in adjustments, \
                "Debe existir penalización por forma irregular"
            assert adjustments['shape_penalty'] < 0, \
                "La penalización de forma debe ser negativa"

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
        # Arrange: Configurar lote mixto (algunos defectuosos)
        mock_ml_predictor.predict_color_percentages.side_effect = [
            {'Light': 90.0, 'Medium': 5.0, 'Dark': 3.0, 'Green': 2.0},  # Bueno
            {'Light': 10.0, 'Medium': 10.0, 'Dark': 75.0, 'Green': 5.0},  # Defecto
        ]

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar reporte completo
        assert session.status == SessionStatus.COMPLETED
        assert session.classification_result is not None, \
            "Debe existir un reporte de clasificación"

        report = session.classification_result

        # Verificar estructura del reporte
        assert 'total_beans_analyzed' in report, \
            "Reporte debe incluir total de granos analizados"
        assert 'category_distribution' in report, \
            "Reporte debe incluir distribución por categorías"
        assert 'quality_breakdown' in report, \
            "Reporte debe incluir desglose de calidad"

        # Verificar que se reportan categorías de calidad
        breakdown = report['quality_breakdown']
        assert 'poor' in breakdown, \
            "Debe existir categoría 'poor' para granos defectuosos"
        assert breakdown['poor'] >= 0, \
            "Conteo de granos defectuosos debe ser no negativo"

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
        # Arrange: Simular error de carga
        mock_cv_service.load_image_from_bytes.return_value = None

        # Act: Intentar procesar imagen inválida
        session = classification_service.start_classification_session(
            coffee_lot_id=400,
            image_bytes=b'invalid_data',
            user_id=4
        )

        # Assert: Verificar manejo de error
        assert session.status == SessionStatus.FAILED, \
            "La sesión debe marcar como FAILED cuando la imagen es inválida"
        assert 'error' in session.classification_result, \
            "El resultado debe contener mensaje de error"
        assert len(session.analyses) == 0, \
            "No debe haber análisis cuando la imagen es inválida"

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
        # Arrange: Simular ausencia de granos
        mock_cv_service.segment_beans.return_value = []

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=500,
            image_bytes=sample_image_bytes,
            user_id=5
        )

        # Assert: Verificar fallo apropiado
        assert session.status == SessionStatus.FAILED, \
            "La sesión debe fallar cuando no hay granos"
        assert 'No se detectaron granos' in session.classification_result['error'], \
            "El error debe indicar claramente que no se detectaron granos"