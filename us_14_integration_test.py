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
import logging
from grain_classification.domain.model.aggregates.classification_session import (
    SessionStatus,
    ClassificationSession
)

logger = logging.getLogger(__name__)


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
        logger.info("=== TEST: Clasificacion categoria Specialty ===")

        # Arrange: Configurar grano Specialty
        logger.info("ARRANGE: Configurando predictor ML con grano Specialty (95% Light)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 95.0,  # Color premium
            'Medium': 3.0,
            'Dark': 1.0,
            'Green': 1.0
        }
        logger.info("Prediccion configurada: Light=95% (maxima calidad)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion de grano Specialty")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar categoría Specialty
        logger.info("ASSERT: Verificando clasificacion como Specialty")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        specialty_grains = [
            a for a in session.analyses
            if a.final_category == 'Specialty'
        ]
        logger.info(f"Granos clasificados como Specialty: {len(specialty_grains)}")

        assert len(specialty_grains) > 0, \
            "Debe haber al menos un grano clasificado como Specialty"
        logger.info("OK: Se detectaron granos Specialty")

        for grain in specialty_grains:
            logger.info(f"Grano Specialty: score={grain.final_score:.3f}, color={grain.quality_assessment['color_class']}")

            assert grain.final_score >= 0.9, \
                f"Specialty requiere score ≥0.9, obtuvo: {grain.final_score}"
            logger.info("  OK: Score >= 0.9 (cumple estandar Specialty)")

            assert grain.quality_assessment['color_class'] == 'Light', \
                f"Specialty debe ser Light, obtuvo: {grain.quality_assessment['color_class']}"
            logger.info("  OK: Color Light (calidad premium)")

        logger.info("OK: Clasificacion Specialty exitosa")

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
        logger.info("=== TEST: Clasificacion categoria Premium ===")

        # Arrange: Configurar grano Premium
        logger.info("ARRANGE: Configurando predictor ML con grano Premium (88% Medium)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 88.0,  # Color premium medio
            'Dark': 4.0,
            'Green': 3.0
        }
        logger.info("Prediccion configurada: Medium=88% (alta calidad)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion de grano Premium")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar categoría Premium
        logger.info("ASSERT: Verificando clasificacion como Premium")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        premium_grains = [
            a for a in session.analyses
            if a.final_category == 'Premium'
        ]
        logger.info(f"Granos clasificados como Premium: {len(premium_grains)}")

        assert len(premium_grains) > 0, \
            "Debe haber al menos un grano clasificado como Premium"
        logger.info("OK: Se detectaron granos Premium")

        for grain in premium_grains:
            logger.info(f"Grano Premium: score={grain.final_score:.3f}")

            assert 0.8 <= grain.final_score < 0.9, \
                f"Premium requiere 0.8 ≤ score < 0.9, obtuvo: {grain.final_score}"
            logger.info("  OK: Score en rango 0.8-0.89 (cumple estandar Premium)")

        logger.info("OK: Clasificacion Premium exitosa")


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
        logger.info("=== TEST: Reporte de calidad promedio del lote ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion del lote")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar reporte de calidad
        logger.info("ASSERT: Verificando reporte de calidad promedio")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        report = session.classification_result
        assert 'overall_batch_quality' in report, \
            "Reporte debe incluir calidad general del lote"
        logger.info(f"Calidad general del lote: {report['overall_batch_quality']:.2f}")

        assert 'average_score' in report, \
            "Reporte debe incluir score promedio"
        logger.info(f"Score promedio: {report['average_score']:.3f}")

        # Verificar escala 0-100
        overall_quality = report['overall_batch_quality']
        assert 0 <= overall_quality <= 100, \
            f"Calidad debe estar en rango 0-100, obtuvo: {overall_quality}"
        logger.info("OK: Calidad en escala 0-100")

        # Verificar coherencia con average_score (0-1 scale)
        avg_score = report['average_score']
        expected_quality = avg_score * 100
        logger.info(f"Verificando coherencia: {overall_quality:.2f} vs {expected_quality:.2f}")

        assert abs(overall_quality - expected_quality) < 0.1, \
            f"Calidad ({overall_quality}) debe ser coherente con score ({avg_score})"
        logger.info("OK: Calidad coherente con score promedio")

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
        logger.info("=== TEST: Distribucion de categorias por lote ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion del lote")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar distribución
        logger.info("ASSERT: Verificando distribucion de categorias")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        report = session.classification_result
        assert 'category_distribution' in report, \
            "Reporte debe incluir distribución de categorías"

        distribution = report['category_distribution']
        logger.info(f"Distribucion encontrada: {list(distribution.keys())}")

        # Verificar que existen todas las categorías esperadas
        expected_categories = ['Specialty', 'Premium', 'A', 'B', 'C']
        for category in expected_categories:
            assert category in distribution, \
                f"Distribución debe incluir categoría: {category}"

            cat_data = distribution[category]
            logger.info(f"  {category}: count={cat_data['count']}, percentage={cat_data['percentage']:.2f}%")

            assert 'count' in cat_data, \
                f"Categoría {category} debe tener 'count'"
            assert 'percentage' in cat_data, \
                f"Categoría {category} debe tener 'percentage'"

            # Verificar tipos de datos
            assert isinstance(cat_data['count'], int), \
                "Count debe ser entero"
            assert isinstance(cat_data['percentage'], (int, float)), \
                "Percentage debe ser numérico"

        logger.info("OK: Distribucion completa con todas las categorias")

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
        logger.info("=== TEST: Identificacion de categoria predominante ===")

        # Arrange: Configurar lote predominantemente Premium
        logger.info("ARRANGE: Configurando lote predominantemente Premium (85% Medium)")
        mock_ml_predictor.predict_color_percentages.return_value = {
            'Light': 5.0,
            'Medium': 85.0,  # Mayoría Medium -> Premium
            'Dark': 5.0,
            'Green': 5.0
        }
        logger.info("Prediccion configurada: Medium=85% (mayoria Premium)")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion del lote")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar categoría predominante
        logger.info("ASSERT: Verificando categoria predominante")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        report = session.classification_result
        assert 'predominant_category' in report, \
            "Reporte debe incluir categoría predominante"

        predominant = report['predominant_category']
        logger.info(f"Categoria predominante detectada: {predominant}")

        valid_categories = ['Specialty', 'Premium', 'A', 'B', 'C']
        assert predominant in valid_categories, \
            f"Categoría predominante debe ser válida, obtuvo: {predominant}"
        logger.info("OK: Categoria predominante valida e identificada correctamente")

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
        logger.info("=== TEST: Almacenamiento de imagenes en Cloudinary ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con almacenamiento de imagenes")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar almacenamiento
        logger.info("ASSERT: Verificando almacenamiento en Cloudinary")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        for i, analysis in enumerate(session.analyses):
            logger.info(f"Verificando grano {i+1}...")

            assert analysis.image_url is not None, \
                "Cada análisis debe tener URL de imagen"
            logger.info(f"  URL: {analysis.image_url}")

            assert 'cloudinary.com' in analysis.image_url, \
                f"URL debe ser de Cloudinary: {analysis.image_url}"
            logger.info("  OK: URL de Cloudinary valida")

            assert analysis.cloudinary_public_id is not None, \
                "Cada análisis debe tener public_id de Cloudinary"
            logger.info(f"  Public ID: {analysis.cloudinary_public_id}")

        # Verificar que Cloudinary fue llamado
        assert mock_cloudinary_service.upload_grain_image.called, \
            "Cloudinary debe haber sido invocado"
        logger.info(f"Cloudinary invocado {mock_cloudinary_service.upload_grain_image.call_count} veces")

        assert mock_cloudinary_service.upload_grain_image.call_count == len(session.analyses), \
            f"Cloudinary debe ser llamado una vez por grano ({len(session.analyses)} veces)"
        logger.info("OK: Imagenes almacenadas correctamente en Cloudinary")

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
        logger.info("=== TEST: Registro de tiempo de procesamiento ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con medicion de tiempo")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar tiempo registrado
        logger.info("ASSERT: Verificando registro de tiempo de procesamiento")
        assert session.status == SessionStatus.COMPLETED
        logger.info("OK: Sesion completada")

        assert session.processing_time_seconds is not None, \
            "Debe existir tiempo de procesamiento"
        logger.info(f"Tiempo de procesamiento: {session.processing_time_seconds:.3f} segundos")

        assert session.processing_time_seconds > 0, \
            f"Tiempo debe ser positivo, obtuvo: {session.processing_time_seconds}"
        logger.info("OK: Tiempo positivo")

        assert isinstance(session.processing_time_seconds, float), \
            f"Tiempo debe ser float, obtuvo tipo: {type(session.processing_time_seconds)}"
        logger.info("OK: Tipo de dato correcto (float)")
        logger.info("OK: Tiempo de procesamiento registrado correctamente")

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
        logger.info("=== TEST: Persistencia de sesion completa en BD ===")

        # Act: Procesar clasificación
        logger.info("ACT: Procesando clasificacion con persistencia")
        session = classification_service.start_classification_session(
            coffee_lot_id=1,
            image_bytes=sample_image_bytes,
            user_id=1
        )
        logger.info(f"Sesion creada con status: {session.status}")

        # Assert: Verificar persistencia
        logger.info("ASSERT: Verificando operaciones de persistencia en BD")

        assert mock_db_session.add.called, \
            "Session.add() debe haber sido llamado"
        logger.info("OK: Session.add() fue invocado")

        assert mock_db_session.commit.called, \
            "Session.commit() debe haber sido llamado"
        logger.info("OK: Session.commit() fue invocado")

        assert mock_db_session.refresh.called, \
            "Session.refresh() debe haber sido llamado"
        logger.info("OK: Session.refresh() fue invocado")

        # Verificar que se agregó la sesión correcta
        added_session = mock_db_session.add.call_args[0][0]
        logger.info(f"Tipo de objeto agregado: {type(added_session).__name__}")

        assert isinstance(added_session, ClassificationSession), \
            f"Debe agregarse ClassificationSession, obtuvo: {type(added_session)}"
        logger.info("OK: Tipo de objeto correcto (ClassificationSession)")

        assert len(added_session.analyses) > 0, \
            "La sesión debe contener análisis de granos"
        logger.info(f"Analisis contenidos en la sesion: {len(added_session.analyses)}")
        logger.info("OK: Sesion completa persistida correctamente en BD")