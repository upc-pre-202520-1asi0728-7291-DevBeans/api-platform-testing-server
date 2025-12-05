"""
Integration Test 09 - US15
==========================
User Story: Reporte Simple de Clasificación

Como productor, deseo un reporte fácil de entender que muestre el porcentaje 
de café apto para exportación vs. mercado local.

Criterios de Aceptación:
- El sistema genera reporte con porcentaje de exportación
- El sistema calcula porcentaje de mercado local
- El reporte incluye resumen de calidad por categorías
- Los porcentajes suman 100%
- El reporte es fácil de interpretar
"""

import pytest
from datetime import datetime
from typing import Dict, List


class MockClassificationSession:
    """Mock de una sesión de clasificación para tests"""
    def __init__(self, session_id: str, quality_distribution: Dict[str, int], 
                 average_score: float, total_beans: int):
        self.session_id_vo = session_id
        self.classification_result = {
            'quality_distribution': quality_distribution,
            'average_quality_score': average_score,
            'total_beans_analyzed': total_beans
        }
        self.total_grains_analyzed = total_beans
        self.status = "COMPLETED"
        self.completed_at = datetime.now()


class ReporteSimpleService:
    """
    Servicio para generar reportes simples de clasificación.
    Calcula porcentajes de café apto para exportación vs mercado local.
    """
    
    # Categorías aptas para exportación (alta calidad)
    EXPORT_CATEGORIES = ['Premium', 'Excelente', 'Muy Bueno', 'Specialty']
    
    # Categorías para mercado local (calidad estándar)
    LOCAL_MARKET_CATEGORIES = ['Bueno', 'Regular', 'Defectuoso']
    
    def generate_simple_report(self, session: MockClassificationSession) -> Dict:
        """
        Genera un reporte simple mostrando porcentaje de exportación vs local.
        """
        quality_dist = session.classification_result.get('quality_distribution', {})
        total_beans = session.total_grains_analyzed
        
        if total_beans == 0:
            return {
                'session_id': session.session_id_vo,
                'export_percentage': 0,
                'local_market_percentage': 0,
                'total_beans': 0,
                'export_beans': 0,
                'local_beans': 0,
                'quality_summary': {},
                'recommendation': 'Sin datos para analizar'
            }
        
        # Calcular granos para exportación
        export_beans = sum(
            quality_dist.get(cat, 0) for cat in self.EXPORT_CATEGORIES
        )
        
        # Calcular granos para mercado local
        local_beans = sum(
            quality_dist.get(cat, 0) for cat in self.LOCAL_MARKET_CATEGORIES
        )
        
        # Calcular porcentajes
        export_percentage = round((export_beans / total_beans) * 100, 2)
        local_percentage = round((local_beans / total_beans) * 100, 2)
        
        # Generar recomendación
        if export_percentage >= 80:
            recommendation = "Excelente lote para exportación premium"
        elif export_percentage >= 60:
            recommendation = "Buen lote con potencial de exportación"
        elif export_percentage >= 40:
            recommendation = "Lote mixto: considerar separación por calidad"
        else:
            recommendation = "Lote orientado principalmente a mercado local"
        
        return {
            'session_id': session.session_id_vo,
            'export_percentage': export_percentage,
            'local_market_percentage': local_percentage,
            'total_beans': total_beans,
            'export_beans': export_beans,
            'local_beans': local_beans,
            'quality_summary': quality_dist,
            'recommendation': recommendation,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_export_grade(self, export_percentage: float) -> str:
        """Obtiene el grado de exportación basado en el porcentaje."""
        if export_percentage >= 90:
            return "SPECIALTY"
        elif export_percentage >= 80:
            return "PREMIUM"
        elif export_percentage >= 70:
            return "GRADE_A"
        elif export_percentage >= 60:
            return "GRADE_B"
        else:
            return "STANDARD"


class TestUS15ReporteSimpleClasificacion:
    """
    Integration Test 09 - US15
    Test de Reporte Simple de Clasificación para Productores
    """
    
    @pytest.fixture
    def reporte_service(self):
        """Fixture para el servicio de reportes simples."""
        return ReporteSimpleService()
    
    @pytest.fixture
    def session_alta_calidad(self):
        """Fixture: Sesión con alta calidad (apta para exportación)."""
        return MockClassificationSession(
            session_id="SESS-2024-001",
            quality_distribution={
                'Premium': 25,
                'Excelente': 35,
                'Muy Bueno': 20,
                'Bueno': 15,
                'Regular': 5
            },
            average_score=0.85,
            total_beans=100
        )
    
    @pytest.fixture
    def session_calidad_mixta(self):
        """Fixture: Sesión con calidad mixta."""
        return MockClassificationSession(
            session_id="SESS-2024-002",
            quality_distribution={
                'Premium': 10,
                'Excelente': 15,
                'Muy Bueno': 20,
                'Bueno': 30,
                'Regular': 20,
                'Defectuoso': 5
            },
            average_score=0.65,
            total_beans=100
        )
    
    @pytest.fixture
    def session_baja_calidad(self):
        """Fixture: Sesión con baja calidad (mercado local)."""
        return MockClassificationSession(
            session_id="SESS-2024-003",
            quality_distribution={
                'Premium': 5,
                'Excelente': 10,
                'Bueno': 35,
                'Regular': 35,
                'Defectuoso': 15
            },
            average_score=0.45,
            total_beans=100
        )
    
    def test_reporte_porcentaje_exportacion_alta_calidad(self, reporte_service, session_alta_calidad):
        """
        Test: Verifica cálculo correcto del porcentaje de exportación 
        para lote de alta calidad.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_alta_calidad)
        
        # Assert
        assert reporte['export_percentage'] == 80.0  # Premium(25) + Excelente(35) + MuyBueno(20)
        assert reporte['local_market_percentage'] == 20.0  # Bueno(15) + Regular(5)
        assert reporte['export_beans'] == 80
        assert reporte['local_beans'] == 20
        assert 'exportación' in reporte['recommendation'].lower()
    
    def test_reporte_porcentaje_mercado_local(self, reporte_service, session_baja_calidad):
        """
        Test: Verifica cálculo correcto del porcentaje de mercado local
        para lote de baja calidad.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_baja_calidad)
        
        # Assert
        assert reporte['export_percentage'] == 15.0  # Premium(5) + Excelente(10)
        assert reporte['local_market_percentage'] == 85.0  # Bueno(35) + Regular(35) + Defectuoso(15)
        assert 'local' in reporte['recommendation'].lower()
    
    def test_reporte_suma_porcentajes_100(self, reporte_service, session_calidad_mixta):
        """
        Test: Verifica que los porcentajes de exportación y local suman 100%.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_calidad_mixta)
        
        # Assert
        total = reporte['export_percentage'] + reporte['local_market_percentage']
        assert total == 100.0, f"Los porcentajes deben sumar 100%, suma actual: {total}"
    
    def test_reporte_incluye_resumen_calidad(self, reporte_service, session_alta_calidad):
        """
        Test: Verifica que el reporte incluye resumen de calidad por categorías.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_alta_calidad)
        
        # Assert
        assert 'quality_summary' in reporte
        assert isinstance(reporte['quality_summary'], dict)
        assert len(reporte['quality_summary']) > 0
        assert 'Premium' in reporte['quality_summary']
    
    def test_reporte_facil_interpretacion(self, reporte_service, session_alta_calidad):
        """
        Test: Verifica que el reporte es fácil de interpretar con todos los campos necesarios.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_alta_calidad)
        
        # Assert - Todos los campos esenciales deben estar presentes
        campos_requeridos = [
            'session_id', 'export_percentage', 'local_market_percentage',
            'total_beans', 'export_beans', 'local_beans', 
            'quality_summary', 'recommendation'
        ]
        for campo in campos_requeridos:
            assert campo in reporte, f"Falta el campo: {campo}"
    
    def test_reporte_grado_exportacion(self, reporte_service, session_alta_calidad):
        """
        Test: Verifica la asignación correcta del grado de exportación.
        """
        # Act
        reporte = reporte_service.generate_simple_report(session_alta_calidad)
        grado = reporte_service.get_export_grade(reporte['export_percentage'])
        
        # Assert
        assert grado == "PREMIUM"  # 80% = PREMIUM
    
    def test_reporte_session_sin_granos(self, reporte_service):
        """
        Test: Verifica comportamiento con sesión sin granos analizados.
        """
        # Arrange
        session_vacia = MockClassificationSession(
            session_id="SESS-2024-EMPTY",
            quality_distribution={},
            average_score=0,
            total_beans=0
        )
        
        # Act
        reporte = reporte_service.generate_simple_report(session_vacia)
        
        # Assert
        assert reporte['export_percentage'] == 0
        assert reporte['local_market_percentage'] == 0
        assert reporte['total_beans'] == 0


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

