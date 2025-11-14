# grain_classification/domain/services/grading_service.py

from typing import Dict, Any, List
from grain_classification.domain.model.valueobjetcs.quality_models import QUALITY_THRESHOLDS


class QualityGradingService:
    """
    Servicio de dominio para evaluación de calidad de granos
    """

    def calculate_final_quality(
            self,
            base_score: float,
            winning_class: str,
            features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula la puntuación final y categoría de calidad considerando:
        - Score base del modelo CNN
        - Características morfológicas (forma, tamaño)
        - Clase de color predominante
        """
        adjustments = {}
        final_score = base_score

        # Ajuste por circularidad (forma)
        circularity = features.get('circularity', 0)
        if circularity < 0.7:
            adjustment = -0.05
            adjustments['shape_penalty'] = adjustment
            final_score += adjustment

        # Ajuste por tamaño (área)
        area = features.get('area', 0)
        if area < 500:
            adjustment = -0.03
            adjustments['size_penalty'] = adjustment
            final_score += adjustment
        elif area > 2000:
            adjustment = 0.02
            adjustments['size_bonus'] = adjustment
            final_score += adjustment

        # Asegurar que el score esté en rango [0, 1]
        final_score = max(0.0, min(1.0, final_score))

        # Determinar categoría de calidad
        quality_category = self._get_quality_category(final_score)

        return {
            'base_score': base_score,
            'adjustments': adjustments,
            'final_score': final_score,
            'quality_category': quality_category,
            'color_class': winning_class
        }

    @staticmethod
    def _get_quality_category(score: float) -> str:
        """
        Mapea el score (0-1) a una categoría de calidad
        """
        if score >= QUALITY_THRESHOLDS['Specialty']:
            return 'Specialty'
        elif score >= QUALITY_THRESHOLDS['Premium']:
            return 'Premium'
        elif score >= QUALITY_THRESHOLDS['A']:
            return 'A'
        elif score >= QUALITY_THRESHOLDS['B']:
            return 'B'
        else:
            return 'C'

    @staticmethod
    def generate_batch_report(bean_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un reporte consolidado del lote completo
        """
        if not bean_assessments:
            return {
                'total_beans_analyzed': 0,
                'overall_batch_quality': 0.0,
                'predominant_category': 'N/A',
                'category_distribution': {},
                'average_score': 0.0
            }

        total_beans = len(bean_assessments)
        total_score = sum(assessment['final_score'] for assessment in bean_assessments)
        average_score = total_score / total_beans

        # Contar distribución por categoría
        category_counts = {}
        for assessment in bean_assessments:
            category = assessment['quality_category']
            category_counts[category] = category_counts.get(category, 0) + 1

        # Encontrar categoría predominante
        predominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'N/A'

        # Crear distribución con porcentajes
        category_distribution = {}
        for category, count in category_counts.items():
            percentage = (count / total_beans) * 100
            category_distribution[category] = {
                'count': count,
                'percentage': percentage
            }

        # Asegurar que todas las categorías existan (incluso con 0)
        for category in ['Specialty', 'Premium', 'A', 'B', 'C']:
            if category not in category_distribution:
                category_distribution[category] = {
                    'count': 0,
                    'percentage': 0.0
                }

        # Calidad general del lote (en porcentaje 0-100)
        overall_batch_quality = average_score * 100

        return {
            'total_beans_analyzed': total_beans,
            'overall_batch_quality': round(overall_batch_quality, 2),
            'predominant_category': predominant_category,
            'category_distribution': category_distribution,
            'average_score': round(average_score, 4),
            'quality_breakdown': {
                'excellent': category_counts.get('Specialty', 0) + category_counts.get('Premium', 0),
                'good': category_counts.get('A', 0),
                'fair': category_counts.get('B', 0),
                'poor': category_counts.get('C', 0)
            }
        }