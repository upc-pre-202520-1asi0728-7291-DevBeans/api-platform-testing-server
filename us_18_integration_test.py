"""
Integration Test 12 - US18
==========================
User Story: Comparación Histórica de Calidad

Como cooperativa, deseo comparar calidad por temporadas para identificar 
patrones y mejorar prácticas agrícolas de mis asociados.

Criterios de Aceptación:
- El sistema permite comparar calidad entre diferentes temporadas
- Identifica patrones de calidad a lo largo del tiempo
- Muestra tendencias de mejora o deterioro
- Proporciona insights para mejorar prácticas agrícolas
- Permite filtrar por productor y período
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List
from statistics import mean


class MockSeasonData:
    """Mock de datos de una temporada para tests"""
    def __init__(self, season_name: str, year: int, start_date: datetime,
                 end_date: datetime, quality_scores: List[float], 
                 total_beans: int, producers_count: int):
        self.season_name = season_name
        self.year = year
        self.start_date = start_date
        self.end_date = end_date
        self.quality_scores = quality_scores
        self.total_beans = total_beans
        self.producers_count = producers_count


class ComparacionHistoricaService:
    """
    Servicio para comparar calidad histórica por temporadas.
    Identifica patrones y tendencias para mejorar prácticas agrícolas.
    """
    
    def compare_seasons(self, seasons: List[MockSeasonData]) -> Dict:
        """
        Compara calidad entre diferentes temporadas.
        """
        if not seasons:
            return {
                'total_seasons': 0,
                'comparison': [],
                'trends': {},
                'patterns': [],
                'insights': []
            }
        
        # Ordenar por fecha
        sorted_seasons = sorted(seasons, key=lambda s: s.start_date)
        
        comparison = []
        for season in sorted_seasons:
            avg_score = mean(season.quality_scores) if season.quality_scores else 0
            comparison.append({
                'season_name': season.season_name,
                'year': season.year,
                'average_quality': round(avg_score * 100, 2),
                'total_beans': season.total_beans,
                'producers_count': season.producers_count,
                'min_score': round(min(season.quality_scores) * 100, 2) if season.quality_scores else 0,
                'max_score': round(max(season.quality_scores) * 100, 2) if season.quality_scores else 0
            })
        
        # Calcular tendencias
        trends = self._calculate_trends(comparison)
        
        # Identificar patrones
        patterns = self._identify_patterns(comparison)
        
        # Generar insights
        insights = self._generate_agricultural_insights(comparison, trends, patterns)
        
        return {
            'total_seasons': len(seasons),
            'comparison': comparison,
            'trends': trends,
            'patterns': patterns,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_trends(self, comparison: List[Dict]) -> Dict:
        """Calcula tendencias de calidad entre temporadas."""
        if len(comparison) < 2:
            return {'direction': 'INSUFFICIENT_DATA', 'change_percentage': 0}
        
        first_avg = comparison[0]['average_quality']
        last_avg = comparison[-1]['average_quality']
        
        change = last_avg - first_avg
        change_percentage = round((change / first_avg) * 100, 2) if first_avg > 0 else 0
        
        if change > 5:
            direction = 'IMPROVING'
        elif change < -5:
            direction = 'DECLINING'
        else:
            direction = 'STABLE'
        
        # Calcular tendencia año a año
        year_over_year = []
        for i in range(1, len(comparison)):
            yoy_change = comparison[i]['average_quality'] - comparison[i-1]['average_quality']
            year_over_year.append({
                'from': comparison[i-1]['season_name'],
                'to': comparison[i]['season_name'],
                'change': round(yoy_change, 2)
            })
        
        return {
            'direction': direction,
            'change_percentage': change_percentage,
            'first_season_avg': first_avg,
            'last_season_avg': last_avg,
            'year_over_year': year_over_year
        }
    
    def _identify_patterns(self, comparison: List[Dict]) -> List[Dict]:
        """Identifica patrones de calidad a lo largo del tiempo."""
        patterns = []
        
        if len(comparison) < 3:
            return patterns
        
        # Patrón: Temporada consistentemente alta
        high_seasons = [s for s in comparison if s['average_quality'] >= 80]
        if len(high_seasons) >= 2:
            patterns.append({
                'type': 'CONSISTENT_HIGH_QUALITY',
                'description': f"{len(high_seasons)} temporadas con calidad superior al 80%",
                'seasons': [s['season_name'] for s in high_seasons]
            })
        
        # Patrón: Variabilidad alta
        scores = [s['average_quality'] for s in comparison]
        variability = max(scores) - min(scores)
        if variability > 20:
            patterns.append({
                'type': 'HIGH_VARIABILITY',
                'description': f"Variabilidad de {variability:.1f}% entre temporadas",
                'min_season': min(comparison, key=lambda x: x['average_quality'])['season_name'],
                'max_season': max(comparison, key=lambda x: x['average_quality'])['season_name']
            })
        
        # Patrón: Mejora continua
        improving = True
        for i in range(1, len(comparison)):
            if comparison[i]['average_quality'] < comparison[i-1]['average_quality']:
                improving = False
                break
        
        if improving and len(comparison) >= 3:
            patterns.append({
                'type': 'CONTINUOUS_IMPROVEMENT',
                'description': 'Mejora continua en todas las temporadas analizadas'
            })
        
        return patterns
    
    def _generate_agricultural_insights(self, comparison: List[Dict], 
                                        trends: Dict, patterns: List[Dict]) -> List[str]:
        """Genera insights para mejorar prácticas agrícolas."""
        insights = []
        
        # Insight basado en tendencia
        if trends.get('direction') == 'IMPROVING':
            insights.append(
                f"Las prácticas agrícolas están dando resultados positivos. "
                f"Mejora del {trends['change_percentage']}% desde la primera temporada."
            )
        elif trends.get('direction') == 'DECLINING':
            insights.append(
                f"⚠️ Tendencia de declive detectada ({trends['change_percentage']}%). "
                f"Revisar cambios en prácticas de cultivo, clima o procesamiento."
            )
        
        # Insight basado en variabilidad
        high_var = [p for p in patterns if p['type'] == 'HIGH_VARIABILITY']
        if high_var:
            insights.append(
                f"Alta variabilidad entre temporadas. Estandarizar procesos de cosecha "
                f"y fermentación para resultados más consistentes."
            )
        
        # Insight basado en mejor temporada
        if comparison:
            best_season = max(comparison, key=lambda x: x['average_quality'])
            insights.append(
                f"Mejor temporada: {best_season['season_name']} ({best_season['average_quality']}%). "
                f"Documentar condiciones climáticas y prácticas de ese período."
            )
        
        return insights
    
    def filter_by_producer(self, all_data: List[Dict], producer_id: int) -> List[Dict]:
        """Filtra datos históricos por productor específico."""
        return [d for d in all_data if d.get('producer_id') == producer_id]
    
    def filter_by_period(self, all_data: List[MockSeasonData], 
                         start_date: datetime, end_date: datetime) -> List[MockSeasonData]:
        """Filtra datos por período específico."""
        return [d for d in all_data if start_date <= d.start_date <= end_date]


class TestUS18ComparacionHistoricaCalidad:
    """
    Integration Test 12 - US18
    Test de Comparación Histórica de Calidad
    """
    
    @pytest.fixture
    def historico_service(self):
        """Fixture para el servicio de comparación histórica."""
        return ComparacionHistoricaService()
    
    @pytest.fixture
    def temporadas_multianual(self):
        """Fixture: Datos de múltiples temporadas (3 años)."""
        return [
            MockSeasonData(
                season_name="Cosecha 2022",
                year=2022,
                start_date=datetime(2022, 4, 1),
                end_date=datetime(2022, 8, 31),
                quality_scores=[0.72, 0.75, 0.70, 0.73, 0.71],
                total_beans=5000,
                producers_count=12
            ),
            MockSeasonData(
                season_name="Cosecha 2023",
                year=2023,
                start_date=datetime(2023, 4, 1),
                end_date=datetime(2023, 8, 31),
                quality_scores=[0.78, 0.80, 0.76, 0.79, 0.77],
                total_beans=6200,
                producers_count=15
            ),
            MockSeasonData(
                season_name="Cosecha 2024",
                year=2024,
                start_date=datetime(2024, 4, 1),
                end_date=datetime(2024, 8, 31),
                quality_scores=[0.82, 0.85, 0.81, 0.84, 0.83],
                total_beans=7500,
                producers_count=18
            )
        ]
    
    @pytest.fixture
    def temporadas_variables(self):
        """Fixture: Datos con alta variabilidad entre temporadas."""
        return [
            MockSeasonData(
                season_name="Temporada Alta 2023",
                year=2023,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 6, 30),
                quality_scores=[0.88, 0.90, 0.87],
                total_beans=4000,
                producers_count=10
            ),
            MockSeasonData(
                season_name="Temporada Baja 2023",
                year=2023,
                start_date=datetime(2023, 7, 1),
                end_date=datetime(2023, 12, 31),
                quality_scores=[0.65, 0.68, 0.62],
                total_beans=3000,
                producers_count=10
            ),
            MockSeasonData(
                season_name="Temporada Alta 2024",
                year=2024,
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 6, 30),
                quality_scores=[0.85, 0.87, 0.86],
                total_beans=4500,
                producers_count=12
            )
        ]
    
    def test_comparacion_entre_temporadas(self, historico_service, temporadas_multianual):
        """
        Test: Verifica comparación de calidad entre diferentes temporadas.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_multianual)
        
        # Assert
        assert resultado['total_seasons'] == 3
        assert len(resultado['comparison']) == 3
        for season in resultado['comparison']:
            assert 'average_quality' in season
            assert 'season_name' in season
    
    def test_identificacion_patrones_calidad(self, historico_service, temporadas_multianual):
        """
        Test: Verifica identificación de patrones de calidad a lo largo del tiempo.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_multianual)
        
        # Assert
        assert 'patterns' in resultado
        pattern_types = [p['type'] for p in resultado['patterns']]
        # Debe identificar mejora continua
        assert 'CONTINUOUS_IMPROVEMENT' in pattern_types
    
    def test_tendencia_mejora(self, historico_service, temporadas_multianual):
        """
        Test: Verifica detección de tendencia de mejora.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_multianual)
        
        # Assert
        trends = resultado['trends']
        assert trends['direction'] == 'IMPROVING'
        assert trends['change_percentage'] > 0
    
    def test_tendencia_deterioro(self, historico_service):
        """
        Test: Verifica detección de tendencia de deterioro.
        """
        # Arrange - Temporadas con calidad decreciente
        temporadas_declive = [
            MockSeasonData("2022", 2022, datetime(2022, 1, 1), datetime(2022, 12, 31),
                          [0.85, 0.84, 0.86], 4000, 10),
            MockSeasonData("2023", 2023, datetime(2023, 1, 1), datetime(2023, 12, 31),
                          [0.75, 0.74, 0.76], 3500, 10),
            MockSeasonData("2024", 2024, datetime(2024, 1, 1), datetime(2024, 12, 31),
                          [0.65, 0.64, 0.66], 3000, 8)
        ]
        
        # Act
        resultado = historico_service.compare_seasons(temporadas_declive)
        
        # Assert
        assert resultado['trends']['direction'] == 'DECLINING'
    
    def test_insights_mejora_practicas(self, historico_service, temporadas_multianual):
        """
        Test: Verifica generación de insights para mejorar prácticas agrícolas.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_multianual)
        
        # Assert
        assert 'insights' in resultado
        assert len(resultado['insights']) > 0
        # Debe haber insights relacionados con prácticas agrícolas
        insights_text = ' '.join(resultado['insights']).lower()
        assert any(word in insights_text for word in ['prácticas', 'temporada', 'cosecha', 'mejor'])
    
    def test_filtro_por_periodo(self, historico_service, temporadas_multianual):
        """
        Test: Verifica filtrado por período específico.
        """
        # Act
        filtrado = historico_service.filter_by_period(
            temporadas_multianual,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        # Assert
        assert len(filtrado) == 2  # 2023 y 2024
        years = [s.year for s in filtrado]
        assert 2023 in years
        assert 2024 in years
        assert 2022 not in years
    
    def test_deteccion_alta_variabilidad(self, historico_service, temporadas_variables):
        """
        Test: Verifica detección de alta variabilidad entre temporadas.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_variables)
        
        # Assert
        patterns = resultado['patterns']
        pattern_types = [p['type'] for p in patterns]
        assert 'HIGH_VARIABILITY' in pattern_types
    
    def test_comparacion_year_over_year(self, historico_service, temporadas_multianual):
        """
        Test: Verifica cálculo de cambios año a año.
        """
        # Act
        resultado = historico_service.compare_seasons(temporadas_multianual)
        
        # Assert
        yoy = resultado['trends']['year_over_year']
        assert len(yoy) == 2  # 2 cambios para 3 temporadas
        for change in yoy:
            assert 'from' in change
            assert 'to' in change
            assert 'change' in change


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

