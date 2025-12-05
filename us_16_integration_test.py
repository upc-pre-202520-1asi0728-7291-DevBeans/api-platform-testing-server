"""
Integration Test 10 - US16
==========================
User Story: Reporte Consolidado para Cooperativas

Como cooperativa, deseo reportes consolidados que comparen la calidad entre 
diferentes productores asociados para optimizar procesos grupales.

Criterios de Aceptación:
- El sistema genera reporte consolidado de múltiples productores
- El reporte compara calidad entre productores
- Incluye ranking de productores por calidad
- Muestra estadísticas agregadas de la cooperativa
- Permite identificar mejores y peores desempeños
"""

import pytest
from datetime import datetime
from typing import Dict, List
from statistics import mean, stdev


class MockProducerData:
    """Mock de datos de un productor para tests"""
    def __init__(self, producer_id: int, name: str, sessions: List[Dict]):
        self.producer_id = producer_id
        self.name = name
        self.sessions = sessions


class ReporteConsolidadoCooperativaService:
    """
    Servicio para generar reportes consolidados de cooperativas.
    Compara calidad entre diferentes productores asociados.
    """
    
    def generate_consolidated_report(self, cooperative_id: int, 
                                     producers_data: List[MockProducerData]) -> Dict:
        """
        Genera un reporte consolidado comparando todos los productores.
        """
        if not producers_data:
            return {
                'cooperative_id': cooperative_id,
                'total_producers': 0,
                'producers_comparison': [],
                'aggregate_stats': {},
                'ranking': [],
                'generated_at': datetime.now().isoformat()
            }
        
        producers_comparison = []
        all_scores = []
        
        for producer in producers_data:
            # Calcular métricas del productor
            producer_scores = [s.get('average_score', 0) for s in producer.sessions]
            total_beans = sum(s.get('total_beans', 0) for s in producer.sessions)
            avg_score = mean(producer_scores) if producer_scores else 0
            
            all_scores.append(avg_score)
            
            producers_comparison.append({
                'producer_id': producer.producer_id,
                'producer_name': producer.name,
                'total_sessions': len(producer.sessions),
                'total_beans_analyzed': total_beans,
                'average_quality_score': round(avg_score * 100, 2),
                'consistency_score': self._calculate_consistency(producer_scores)
            })
        
        # Ordenar por calidad promedio (ranking)
        ranking = sorted(
            producers_comparison, 
            key=lambda x: x['average_quality_score'], 
            reverse=True
        )
        
        # Asignar posiciones
        for i, producer in enumerate(ranking):
            producer['rank'] = i + 1
        
        # Estadísticas agregadas
        aggregate_stats = {
            'total_producers': len(producers_data),
            'total_sessions': sum(p['total_sessions'] for p in producers_comparison),
            'total_beans_analyzed': sum(p['total_beans_analyzed'] for p in producers_comparison),
            'cooperative_average_quality': round(mean(all_scores) * 100, 2) if all_scores else 0,
            'best_performer': ranking[0]['producer_name'] if ranking else None,
            'lowest_performer': ranking[-1]['producer_name'] if ranking else None,
            'quality_std_deviation': round(stdev(all_scores) * 100, 2) if len(all_scores) > 1 else 0
        }
        
        return {
            'cooperative_id': cooperative_id,
            'total_producers': len(producers_data),
            'producers_comparison': producers_comparison,
            'aggregate_stats': aggregate_stats,
            'ranking': ranking,
            'improvement_suggestions': self._generate_suggestions(ranking),
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calcula un score de consistencia (menor variación = mayor consistencia)."""
        if len(scores) < 2:
            return 100.0
        std = stdev(scores)
        # Convertir a score donde 100 = muy consistente, 0 = muy variable
        consistency = max(0, 100 - (std * 100 * 2))
        return round(consistency, 2)
    
    def _generate_suggestions(self, ranking: List[Dict]) -> List[str]:
        """Genera sugerencias de mejora basadas en el ranking."""
        suggestions = []
        
        if not ranking:
            return suggestions
        
        # Sugerencias basadas en brechas de calidad
        best = ranking[0]['average_quality_score']
        worst = ranking[-1]['average_quality_score']
        gap = best - worst
        
        if gap > 20:
            suggestions.append(
                f"Alta brecha de calidad ({gap:.1f}%). Considerar capacitación para productores de menor rendimiento."
            )
        
        if worst < 60:
            suggestions.append(
                f"Productor {ranking[-1]['producer_name']} requiere atención urgente (calidad: {worst}%)."
            )
        
        # Productores con baja consistencia
        inconsistent = [p for p in ranking if p['consistency_score'] < 70]
        if inconsistent:
            suggestions.append(
                f"{len(inconsistent)} productor(es) con baja consistencia. Revisar procesos de cosecha."
            )
        
        return suggestions
    
    def compare_two_producers(self, producer1: Dict, producer2: Dict) -> Dict:
        """Compara dos productores específicos."""
        diff = producer1['average_quality_score'] - producer2['average_quality_score']
        return {
            'producer1': producer1['producer_name'],
            'producer2': producer2['producer_name'],
            'quality_difference': abs(diff),
            'better_performer': producer1['producer_name'] if diff > 0 else producer2['producer_name'],
            'comparison_summary': self._get_comparison_summary(diff)
        }
    
    def _get_comparison_summary(self, diff: float) -> str:
        """Genera un resumen de comparación."""
        abs_diff = abs(diff)
        if abs_diff < 5:
            return "Rendimiento similar"
        elif abs_diff < 15:
            return "Diferencia moderada"
        else:
            return "Diferencia significativa"


class TestUS16ReporteConsolidadoCooperativas:
    """
    Integration Test 10 - US16
    Test de Reporte Consolidado para Cooperativas
    """
    
    @pytest.fixture
    def reporte_service(self):
        """Fixture para el servicio de reportes consolidados."""
        return ReporteConsolidadoCooperativaService()
    
    @pytest.fixture
    def productores_cooperativa(self):
        """Fixture: Lista de productores con sus sesiones."""
        return [
            MockProducerData(
                producer_id=1,
                name="Juan Pérez",
                sessions=[
                    {'average_score': 0.85, 'total_beans': 150},
                    {'average_score': 0.82, 'total_beans': 200},
                    {'average_score': 0.88, 'total_beans': 175}
                ]
            ),
            MockProducerData(
                producer_id=2,
                name="María García",
                sessions=[
                    {'average_score': 0.78, 'total_beans': 180},
                    {'average_score': 0.75, 'total_beans': 160},
                    {'average_score': 0.80, 'total_beans': 190}
                ]
            ),
            MockProducerData(
                producer_id=3,
                name="Carlos López",
                sessions=[
                    {'average_score': 0.92, 'total_beans': 220},
                    {'average_score': 0.90, 'total_beans': 210},
                    {'average_score': 0.91, 'total_beans': 230}
                ]
            ),
            MockProducerData(
                producer_id=4,
                name="Ana Rodríguez",
                sessions=[
                    {'average_score': 0.65, 'total_beans': 140},
                    {'average_score': 0.68, 'total_beans': 130}
                ]
            )
        ]
    
    def test_reporte_consolidado_multiples_productores(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica generación de reporte consolidado con múltiples productores.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        assert reporte['total_producers'] == 4
        assert len(reporte['producers_comparison']) == 4
        assert 'aggregate_stats' in reporte
    
    def test_comparacion_calidad_entre_productores(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica que el reporte compara calidad entre productores.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        for producer in reporte['producers_comparison']:
            assert 'producer_name' in producer
            assert 'average_quality_score' in producer
            assert producer['average_quality_score'] >= 0
            assert producer['average_quality_score'] <= 100
    
    def test_ranking_productores_por_calidad(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica ranking de productores ordenado por calidad.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        ranking = reporte['ranking']
        assert len(ranking) == 4
        
        # Verificar que está ordenado de mayor a menor
        for i in range(len(ranking) - 1):
            assert ranking[i]['average_quality_score'] >= ranking[i + 1]['average_quality_score']
        
        # Verificar posiciones
        assert ranking[0]['rank'] == 1
        assert ranking[-1]['rank'] == 4
    
    def test_estadisticas_agregadas_cooperativa(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica cálculo de estadísticas agregadas de la cooperativa.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        stats = reporte['aggregate_stats']
        assert stats['total_producers'] == 4
        assert stats['total_sessions'] == 11  # 3+3+3+2
        assert stats['cooperative_average_quality'] > 0
        assert 'best_performer' in stats
        assert 'lowest_performer' in stats
    
    def test_identificacion_mejor_desempeno(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica identificación del productor con mejor desempeño.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        stats = reporte['aggregate_stats']
        # Carlos López tiene el mejor promedio (0.91)
        assert stats['best_performer'] == "Carlos López"
    
    def test_identificacion_peor_desempeno(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica identificación del productor con menor desempeño.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        stats = reporte['aggregate_stats']
        # Ana Rodríguez tiene el menor promedio (0.665)
        assert stats['lowest_performer'] == "Ana Rodríguez"
    
    def test_sugerencias_mejora_generadas(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica generación de sugerencias de mejora.
        """
        # Act
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        
        # Assert
        assert 'improvement_suggestions' in reporte
        assert isinstance(reporte['improvement_suggestions'], list)
    
    def test_comparacion_dos_productores_especificos(self, reporte_service, productores_cooperativa):
        """
        Test: Verifica comparación directa entre dos productores.
        """
        # Arrange
        reporte = reporte_service.generate_consolidated_report(
            cooperative_id=1,
            producers_data=productores_cooperativa
        )
        producer1 = reporte['producers_comparison'][0]
        producer2 = reporte['producers_comparison'][1]
        
        # Act
        comparison = reporte_service.compare_two_producers(producer1, producer2)
        
        # Assert
        assert 'quality_difference' in comparison
        assert 'better_performer' in comparison
        assert 'comparison_summary' in comparison


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

