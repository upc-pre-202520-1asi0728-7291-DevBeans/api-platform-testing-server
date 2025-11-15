"""
Integration Tests para US14: Clasificación por Estándares Internacionales

User Story:
Como productor o cooperativa, deseo obtener clasificación automática
según estándares de exportación reconocidos para acceder a mejores precios.

Ejecutar todos los tests de esta US:
    pytest us_14_integration_test.py -v

Ejecutar un test específico:
    pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_clasificacion_categoria_specialty -v
"""

import pytest
from grain_classification.domain.model.aggregates.classification_session import (
    SessionStatus,
    ClassificationSession
)


@pytest.mark.us14
@pytest.mark.integration
class TestUS14ClasificacionEstandaresInternacionales:
    """
    Suite de tests de integración para la clasificación automática según
    estándares de exportación reconocidos internacionalmente.
    """

    def test_clasificacion_categoria_specialty(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que granos de máxima calidad se clasifiquen como 'Specialty' (≥90%).

        GIVEN granos de máxima calidad (Light, sin defectos)
        WHEN se evalúan según estándares
        THEN deben clasificarse como 'Specialty' (≥90%)
        """
        # Arrange: Configurar grano Specialty
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 95.0,  # Color premium
            'Medium': 3.0,
            'Dark': 1.0,
            'Green': 1.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar categoría Specialty
        assert session.status == SessionStatus.COMPLETED

        specialty_grains = [
            a for a in session.analyses
            if a.final_category == 'Specialty'
        ]
        assert len(specialty_grains) > 0, \
            "Debe haber al menos un grano clasificado como Specialty"

        for grain in specialty_grains:
            assert grain.final_score >= 0.9, \
                f"Specialty requiere score ≥0.9, obtuvo: {grain.final_score}"
            assert grain.quality_assessment['color_class'] == 'Light', \
                f"Specialty debe ser Light, obtuvo: {grain.quality_assessment['color_class']}"

    def test_clasificacion_categoria_premium(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que granos de alta calidad se clasifiquen como 'Premium' (80-89%).

        GIVEN granos de alta calidad (Medium, buena forma)
        WHEN se evalúan según estándares
        THEN deben clasificarse como 'Premium' (80-89%)
        """
        # Arrange: Configurar grano Premium
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 88.0,  # Color premium medio
            'Dark': 4.0,
            'Green': 3.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar categoría Premium
        assert session.status == SessionStatus.COMPLETED

        premium_grains = [
            a for a in session.analyses
            if a.final_category == 'Premium'
        ]
        assert len(premium_grains) > 0, \
            "Debe haber al menos un grano clasificado como Premium"

        for grain in premium_grains:
            assert 0.8 <= grain.final_score < 0.9, \
                f"Premium requiere 0.8 ≤ score < 0.9, obtuvo: {grain.final_score}"


    def test_reporte_lote_calidad_promedio(
            self,
            classification_service,
            sample_image_bytes
    ):
        """
        Verifica que el reporte incluya la calidad promedio del lote en escala 0-100.

        GIVEN un lote clasificado
        WHEN se genera el reporte final
        THEN debe incluir la calidad promedio del lote en escala 0-100
        """
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar reporte de calidad
        assert session.status == SessionStatus.COMPLETED

        report = session.classification_result
        assert 'overall_batch_quality' in report, \
            "Reporte debe incluir calidad general del lote"
        assert 'average_score' in report, \
            "Reporte debe incluir score promedio"

        # Verificar escala 0-100
        overall_quality = report['overall_batch_quality']
        assert 0 <= overall_quality <= 100, \
            f"Calidad debe estar en rango 0-100, obtuvo: {overall_quality}"

        # Verificar coherencia con average_score (0-1 scale)
        avg_score = report['average_score']
        expected_quality = avg_score * 100
        assert abs(overall_quality - expected_quality) < 0.1, \
            f"Calidad ({overall_quality}) debe ser coherente con score ({avg_score})"

    def test_distribucion_categorias_por_lote(
            self,
            classification_service,
            sample_image_bytes
    ):
        """
        Verifica que el reporte muestre la distribución completa de categorías.

        GIVEN un lote procesado
        WHEN se genera el reporte
        THEN debe mostrar distribución de granos por categoría
        """
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar distribución
        assert session.status == SessionStatus.COMPLETED

        report = session.classification_result
        assert 'category_distribution' in report, \
            "Reporte debe incluir distribución de categorías"

        distribution = report['category_distribution']

        # Verificar que existen todas las categorías esperadas
        expected_categories = ['Specialty', 'Premium', 'A', 'B', 'C']
        for category in expected_categories:
            assert category in distribution, \
                f"Distribución debe incluir categoría: {category}"
            assert 'count' in distribution[category], \
                f"Categoría {category} debe tener 'count'"
            assert 'percentage' in distribution[category], \
                f"Categoría {category} debe tener 'percentage'"

            # Verificar tipos de datos
            assert isinstance(distribution[category]['count'], int), \
                "Count debe ser entero"
            assert isinstance(distribution[category]['percentage'], (int, float)), \
                "Percentage debe ser numérico"

    def test_categoria_predominante_lote(
            self,
            classification_service,
            mock_ml_predictor,
            sample_image_bytes
    ):
        """
        Verifica que se identifique correctamente la categoría predominante del lote.

        GIVEN un lote con mayoría de granos de una categoría
        WHEN se genera el reporte
        THEN debe identificar correctamente la categoría predominante
        """
        # Arrange: Configurar lote predominantemente Premium
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 85.0,  # Mayoría Medium -> Premium
            'Dark': 5.0,
            'Green': 5.0
        }

        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar categoría predominante
        assert session.status == SessionStatus.COMPLETED

        report = session.classification_result
        assert 'predominant_category' in report, \
            "Reporte debe incluir categoría predominante"

        predominant = report['predominant_category']
        valid_categories = ['Specialty', 'Premium', 'A', 'B', 'C']
        assert predominant in valid_categories, \
            f"Categoría predominante debe ser válida, obtuvo: {predominant}"

    def test_almacenamiento_imagen_cloudinary(
            self,
            classification_service,
            mock_cloudinary_service,
            sample_image_bytes
    ):
        """
        Verifica que las imágenes se almacenen en Cloudinary con URL pública.

        GIVEN granos procesados
        WHEN se completa el análisis
        THEN debe almacenar imágenes en Cloudinary con URL pública
        """
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar almacenamiento
        assert session.status == SessionStatus.COMPLETED

        for analysis in session.analyses:
            assert analysis.image_url is not None, \
                "Cada análisis debe tener URL de imagen"
            assert 'cloudinary.com' in analysis.image_url, \
                f"URL debe ser de Cloudinary: {analysis.image_url}"
            assert analysis.cloudinary_public_id is not None, \
                "Cada análisis debe tener public_id de Cloudinary"

        # Verificar que Cloudinary fue llamado
        assert mock_cloudinary_service.upload_grain_image.called, \
            "Cloudinary debe haber sido invocado"
        assert mock_cloudinary_service.upload_grain_image.call_count == len(session.analyses), \
            f"Cloudinary debe ser llamado una vez por grano ({len(session.analyses)} veces)"

    def test_tiempo_procesamiento_registrado(
            self,
            classification_service,
            sample_image_bytes
    ):
        """
        Verifica que el tiempo de procesamiento se registre correctamente.

        GIVEN un lote procesado
        WHEN se completa la clasificación
        THEN debe registrar el tiempo de procesamiento en segundos
        """
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar tiempo registrado
        assert session.status == SessionStatus.COMPLETED
        assert session.processing_time_seconds is not None, \
            "Debe existir tiempo de procesamiento"
        assert session.processing_time_seconds > 0, \
            f"Tiempo debe ser positivo, obtuvo: {session.processing_time_seconds}"
        assert isinstance(session.processing_time_seconds, float), \
            f"Tiempo debe ser float, obtuvo tipo: {type(session.processing_time_seconds)}"

    def test_persistencia_sesion_completa(
            self,
            classification_service,
            mock_db_session,
            sample_image_bytes
    ):
        """
        Verifica que la sesión completa se persista correctamente en la base de datos.

        GIVEN una sesión de clasificación completada
        WHEN se persiste en la base de datos
        THEN debe guardar el agregado completo con todas las entidades
        """
        # Act: Procesar clasificación
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )

        # Assert: Verificar persistencia
        assert mock_db_session.add.called, \
            "Session.add() debe haber sido llamado"
        assert mock_db_session.commit.called, \
            "Session.commit() debe haber sido llamado"
        assert mock_db_session.refresh.called, \
            "Session.refresh() debe haber sido llamado"

        # Verificar que se agregó la sesión correcta
        added_session = mock_db_session.add.call_args[0][0]
        assert isinstance(added_session, ClassificationSession), \
            f"Debe agregarse ClassificationSession, obtuvo: {type(added_session)}"
        assert len(added_session.analyses) > 0, \
            "La sesión debe contener análisis de granos"