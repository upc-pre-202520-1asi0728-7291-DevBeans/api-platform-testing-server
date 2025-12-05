"""
Integration Test 11 - US17
==========================
User Story: Exportación para Compradores

Como productor o cooperativa, deseo exportar certificados de calidad en formatos 
reconocidos internacionalmente (PDF, Excel) para presentar a compradores.

Criterios de Aceptación:
- El sistema genera certificados en formato PDF
- El sistema genera reportes en formato Excel
- Los certificados incluyen información de calidad validada
- Los formatos son reconocidos internacionalmente
- Incluyen información del lote, productor y clasificación
"""

import pytest
from datetime import datetime
from typing import Dict, List
import base64
import json


class MockCertificateData:
    """Mock de datos para certificación"""
    def __init__(self, lot_number: str, producer_name: str, 
                 quality_score: float, quality_grade: str):
        self.lot_number = lot_number
        self.producer_name = producer_name
        self.quality_score = quality_score
        self.quality_grade = quality_grade
        self.certification_date = datetime.now()
        self.beans_analyzed = 150
        self.origin = "Cusco, Perú"


class ExportacionCertificadosService:
    """
    Servicio para exportar certificados de calidad en formatos PDF y Excel.
    Genera documentos reconocidos internacionalmente.
    """
    
    SUPPORTED_FORMATS = ['PDF', 'EXCEL', 'CSV', 'JSON']
    
    def generate_pdf_certificate(self, cert_data: MockCertificateData) -> Dict:
        """
        Genera un certificado de calidad en formato PDF.
        Retorna metadatos del PDF generado.
        """
        # Simular generación de PDF
        pdf_content = self._build_pdf_structure(cert_data)
        
        return {
            'format': 'PDF',
            'filename': f"certificado_calidad_{cert_data.lot_number}.pdf",
            'content_type': 'application/pdf',
            'size_bytes': len(json.dumps(pdf_content)),
            'certificate_data': pdf_content,
            'generated_at': datetime.now().isoformat(),
            'valid': True,
            'international_standard': 'ICO_QUALITY_CERT_v2'
        }
    
    def generate_excel_report(self, cert_data: MockCertificateData) -> Dict:
        """
        Genera un reporte de calidad en formato Excel.
        """
        excel_content = self._build_excel_structure(cert_data)
        
        return {
            'format': 'EXCEL',
            'filename': f"reporte_calidad_{cert_data.lot_number}.xlsx",
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size_bytes': len(json.dumps(excel_content)),
            'sheets': excel_content['sheets'],
            'generated_at': datetime.now().isoformat(),
            'valid': True
        }
    
    def _build_pdf_structure(self, cert_data: MockCertificateData) -> Dict:
        """Construye la estructura del certificado PDF."""
        return {
            'header': {
                'title': 'CERTIFICADO DE CALIDAD DE CAFÉ',
                'standard': 'ICO International Coffee Organization',
                'certificate_number': f"CERT-{cert_data.lot_number}-{datetime.now().strftime('%Y%m%d')}",
                'logo': 'beandetect_logo_base64'
            },
            'lot_information': {
                'lot_number': cert_data.lot_number,
                'origin': cert_data.origin,
                'producer': cert_data.producer_name,
                'certification_date': cert_data.certification_date.isoformat()
            },
            'quality_assessment': {
                'overall_score': cert_data.quality_score,
                'grade': cert_data.quality_grade,
                'beans_analyzed': cert_data.beans_analyzed,
                'methodology': 'AI-Powered Visual Classification',
                'sca_equivalent': self._get_sca_equivalent(cert_data.quality_score)
            },
            'footer': {
                'disclaimer': 'Este certificado es válido para transacciones comerciales internacionales.',
                'verification_url': f"https://beandetect.ai/verify/{cert_data.lot_number}",
                'digital_signature': 'SIGNED_HASH_PLACEHOLDER'
            }
        }
    
    def _build_excel_structure(self, cert_data: MockCertificateData) -> Dict:
        """Construye la estructura del reporte Excel."""
        return {
            'sheets': [
                {
                    'name': 'Resumen',
                    'columns': ['Campo', 'Valor'],
                    'data': [
                        ['Número de Lote', cert_data.lot_number],
                        ['Productor', cert_data.producer_name],
                        ['Origen', cert_data.origin],
                        ['Puntuación de Calidad', f"{cert_data.quality_score}%"],
                        ['Grado', cert_data.quality_grade],
                        ['Granos Analizados', cert_data.beans_analyzed],
                        ['Fecha', cert_data.certification_date.strftime('%Y-%m-%d')]
                    ]
                },
                {
                    'name': 'Detalle de Calidad',
                    'columns': ['Categoría', 'Porcentaje', 'Cantidad'],
                    'data': [
                        ['Premium', '25%', 38],
                        ['Excelente', '35%', 52],
                        ['Muy Bueno', '25%', 38],
                        ['Bueno', '10%', 15],
                        ['Regular', '5%', 7]
                    ]
                }
            ]
        }
    
    def _get_sca_equivalent(self, score: float) -> str:
        """Obtiene el equivalente SCA (Specialty Coffee Association)."""
        if score >= 85:
            return "Specialty Grade (85+)"
        elif score >= 80:
            return "Premium Grade (80-84)"
        elif score >= 75:
            return "Exchange Grade (75-79)"
        elif score >= 70:
            return "Standard Grade (70-74)"
        else:
            return "Below Standard (<70)"
    
    def validate_international_format(self, export_result: Dict) -> bool:
        """Valida que el formato cumpla estándares internacionales."""
        required_fields = {
            'PDF': ['certificate_data', 'international_standard'],
            'EXCEL': ['sheets']
        }
        
        format_type = export_result.get('format')
        if format_type not in required_fields:
            return False
        
        for field in required_fields[format_type]:
            if field not in export_result:
                return False
        
        return export_result.get('valid', False)
    
    def get_supported_formats(self) -> List[str]:
        """Retorna los formatos de exportación soportados."""
        return self.SUPPORTED_FORMATS


class TestUS17ExportacionCompradores:
    """
    Integration Test 11 - US17
    Test de Exportación de Certificados para Compradores
    """
    
    @pytest.fixture
    def export_service(self):
        """Fixture para el servicio de exportación."""
        return ExportacionCertificadosService()
    
    @pytest.fixture
    def certificado_premium(self):
        """Fixture: Datos de certificado premium."""
        return MockCertificateData(
            lot_number="LOT-2024-0156",
            producer_name="Cooperativa Café Alto",
            quality_score=87.5,
            quality_grade="SPECIALTY"
        )
    
    @pytest.fixture
    def certificado_standard(self):
        """Fixture: Datos de certificado estándar."""
        return MockCertificateData(
            lot_number="LOT-2024-0157",
            producer_name="Finca El Cafetal",
            quality_score=72.0,
            quality_grade="STANDARD"
        )
    
    def test_generacion_certificado_pdf(self, export_service, certificado_premium):
        """
        Test: Verifica generación de certificados en formato PDF.
        """
        # Act
        resultado = export_service.generate_pdf_certificate(certificado_premium)
        
        # Assert
        assert resultado['format'] == 'PDF'
        assert resultado['filename'].endswith('.pdf')
        assert resultado['content_type'] == 'application/pdf'
        assert resultado['valid'] is True
    
    def test_generacion_reporte_excel(self, export_service, certificado_premium):
        """
        Test: Verifica generación de reportes en formato Excel.
        """
        # Act
        resultado = export_service.generate_excel_report(certificado_premium)
        
        # Assert
        assert resultado['format'] == 'EXCEL'
        assert resultado['filename'].endswith('.xlsx')
        assert 'sheets' in resultado
        assert len(resultado['sheets']) >= 1
    
    def test_certificado_incluye_informacion_calidad(self, export_service, certificado_premium):
        """
        Test: Verifica que el certificado incluye información de calidad validada.
        """
        # Act
        resultado = export_service.generate_pdf_certificate(certificado_premium)
        
        # Assert
        cert_data = resultado['certificate_data']
        assert 'quality_assessment' in cert_data
        assert cert_data['quality_assessment']['overall_score'] == 87.5
        assert cert_data['quality_assessment']['grade'] == 'SPECIALTY'
        assert 'sca_equivalent' in cert_data['quality_assessment']
    
    def test_formato_reconocido_internacionalmente_pdf(self, export_service, certificado_premium):
        """
        Test: Verifica que el PDF cumple estándares internacionales.
        """
        # Act
        resultado = export_service.generate_pdf_certificate(certificado_premium)
        is_valid = export_service.validate_international_format(resultado)
        
        # Assert
        assert is_valid is True
        assert 'international_standard' in resultado
        assert resultado['international_standard'] == 'ICO_QUALITY_CERT_v2'
    
    def test_certificado_incluye_info_lote(self, export_service, certificado_premium):
        """
        Test: Verifica que el certificado incluye información del lote.
        """
        # Act
        resultado = export_service.generate_pdf_certificate(certificado_premium)
        
        # Assert
        lot_info = resultado['certificate_data']['lot_information']
        assert lot_info['lot_number'] == "LOT-2024-0156"
        assert lot_info['origin'] == "Cusco, Perú"
    
    def test_certificado_incluye_info_productor(self, export_service, certificado_premium):
        """
        Test: Verifica que el certificado incluye información del productor.
        """
        # Act
        resultado = export_service.generate_pdf_certificate(certificado_premium)
        
        # Assert
        lot_info = resultado['certificate_data']['lot_information']
        assert lot_info['producer'] == "Cooperativa Café Alto"
    
    def test_excel_multiples_hojas(self, export_service, certificado_premium):
        """
        Test: Verifica que el Excel contiene múltiples hojas con información.
        """
        # Act
        resultado = export_service.generate_excel_report(certificado_premium)
        
        # Assert
        sheets = resultado['sheets']
        assert len(sheets) == 2
        assert sheets[0]['name'] == 'Resumen'
        assert sheets[1]['name'] == 'Detalle de Calidad'
    
    def test_formatos_soportados(self, export_service):
        """
        Test: Verifica los formatos de exportación soportados.
        """
        # Act
        formatos = export_service.get_supported_formats()
        
        # Assert
        assert 'PDF' in formatos
        assert 'EXCEL' in formatos
        assert len(formatos) >= 2


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

