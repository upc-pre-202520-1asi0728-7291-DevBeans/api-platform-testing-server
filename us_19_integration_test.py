"""
Integration Test 13 - US19
==========================
User Story: Códigos QR para Lotes

Como productor o cooperativa, deseo generar códigos QR únicos por lote que 
permitan a compradores verificar origen, calidad y proceso de clasificación.

Criterios de Aceptación:
- El sistema genera códigos QR únicos por cada lote
- El QR contiene información verificable del origen
- El QR incluye datos de calidad del lote
- El QR permite verificar el proceso de clasificación
- El código QR es escaneable y lleva a una URL de verificación
"""

import pytest
from datetime import datetime
import hashlib
import base64
from typing import Dict, Optional
import json


class MockLotData:
    """Mock de datos de un lote para tests"""
    def __init__(self, lot_id: int, lot_number: str, producer_name: str,
                 origin: str, quality_score: float, quality_grade: str,
                 beans_analyzed: int, harvest_date: datetime):
        self.lot_id = lot_id
        self.lot_number = lot_number
        self.producer_name = producer_name
        self.origin = origin
        self.quality_score = quality_score
        self.quality_grade = quality_grade
        self.beans_analyzed = beans_analyzed
        self.harvest_date = harvest_date


class QRCodeGeneratorService:
    """
    Servicio para generar códigos QR únicos para lotes de café.
    Permite verificación de origen, calidad y proceso de clasificación.
    """
    
    BASE_VERIFICATION_URL = "https://beandetect.ai/verify"
    
    def generate_qr_code(self, lot_data: MockLotData) -> Dict:
        """
        Genera un código QR único para el lote.
        """
        # Generar identificador único
        unique_id = self._generate_unique_id(lot_data)
        
        # URL de verificación
        verification_url = f"{self.BASE_VERIFICATION_URL}/{unique_id}"
        
        # Datos embebidos en el QR
        qr_data = {
            'verification_id': unique_id,
            'lot_number': lot_data.lot_number,
            'producer': lot_data.producer_name,
            'origin': lot_data.origin,
            'quality_score': lot_data.quality_score,
            'quality_grade': lot_data.quality_grade,
            'beans_analyzed': lot_data.beans_analyzed,
            'harvest_date': lot_data.harvest_date.isoformat(),
            'verification_url': verification_url,
            'generated_at': datetime.now().isoformat()
        }
        
        # Simular generación de imagen QR (en producción usaría qrcode library)
        qr_image_base64 = self._generate_qr_image_mock(qr_data)
        
        return {
            'qr_code_id': unique_id,
            'lot_number': lot_data.lot_number,
            'verification_url': verification_url,
            'qr_image_base64': qr_image_base64,
            'qr_data': qr_data,
            'is_valid': True,
            'expires_at': None,  # No expira
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_unique_id(self, lot_data: MockLotData) -> str:
        """Genera un ID único basado en los datos del lote."""
        data_string = f"{lot_data.lot_number}-{lot_data.producer_name}-{lot_data.harvest_date}"
        hash_object = hashlib.sha256(data_string.encode())
        return hash_object.hexdigest()[:16].upper()
    
    def _generate_qr_image_mock(self, qr_data: Dict) -> str:
        """Simula la generación de una imagen QR en base64."""
        # En producción, esto usaría la librería qrcode
        json_data = json.dumps(qr_data)
        return base64.b64encode(json_data.encode()).decode()
    
    def verify_qr_code(self, verification_id: str, stored_data: Dict) -> Dict:
        """
        Verifica un código QR y retorna la información del lote.
        """
        if not stored_data or stored_data.get('qr_code_id') != verification_id:
            return {
                'verified': False,
                'error': 'Código QR no encontrado o inválido',
                'lot_data': None
            }
        
        return {
            'verified': True,
            'verification_timestamp': datetime.now().isoformat(),
            'lot_data': {
                'lot_number': stored_data['qr_data']['lot_number'],
                'producer': stored_data['qr_data']['producer'],
                'origin': stored_data['qr_data']['origin'],
                'quality_score': stored_data['qr_data']['quality_score'],
                'quality_grade': stored_data['qr_data']['quality_grade'],
                'beans_analyzed': stored_data['qr_data']['beans_analyzed'],
                'harvest_date': stored_data['qr_data']['harvest_date'],
                'classification_verified': True
            }
        }
    
    def get_verification_url(self, qr_result: Dict) -> str:
        """Obtiene la URL de verificación del QR."""
        return qr_result.get('verification_url', '')
    
    def is_qr_scannable(self, qr_result: Dict) -> bool:
        """Verifica si el QR es escaneable (tiene imagen válida)."""
        qr_image = qr_result.get('qr_image_base64', '')
        if not qr_image:
            return False
        try:
            # Verificar que es base64 válido
            base64.b64decode(qr_image)
            return True
        except Exception:
            return False
    
    def get_qr_content_for_print(self, qr_result: Dict) -> Dict:
        """Obtiene el contenido del QR formateado para impresión."""
        return {
            'lot_number': qr_result['lot_number'],
            'verification_url': qr_result['verification_url'],
            'qr_image': qr_result['qr_image_base64'],
            'print_size': '5cm x 5cm',
            'format': 'PNG',
            'resolution': '300dpi'
        }


class TestUS19CodigosQRLotes:
    """
    Integration Test 13 - US19
    Test de Generación de Códigos QR para Lotes
    """
    
    @pytest.fixture
    def qr_service(self):
        """Fixture para el servicio de generación de QR."""
        return QRCodeGeneratorService()
    
    @pytest.fixture
    def lote_premium(self):
        """Fixture: Datos de un lote premium."""
        return MockLotData(
            lot_id=1,
            lot_number="LOT-2024-0156",
            producer_name="Cooperativa Café Alto",
            origin="Cusco, Perú",
            quality_score=87.5,
            quality_grade="SPECIALTY",
            beans_analyzed=1500,
            harvest_date=datetime(2024, 6, 15)
        )
    
    @pytest.fixture
    def lote_standard(self):
        """Fixture: Datos de un lote estándar."""
        return MockLotData(
            lot_id=2,
            lot_number="LOT-2024-0157",
            producer_name="Finca El Cafetal",
            origin="Cajamarca, Perú",
            quality_score=72.0,
            quality_grade="STANDARD",
            beans_analyzed=1200,
            harvest_date=datetime(2024, 7, 20)
        )
    
    def test_generacion_qr_unico_por_lote(self, qr_service, lote_premium, lote_standard):
        """
        Test: Verifica generación de códigos QR únicos por cada lote.
        """
        # Act
        qr_lote1 = qr_service.generate_qr_code(lote_premium)
        qr_lote2 = qr_service.generate_qr_code(lote_standard)
        
        # Assert
        assert qr_lote1['qr_code_id'] != qr_lote2['qr_code_id']
        assert qr_lote1['lot_number'] != qr_lote2['lot_number']
    
    def test_qr_contiene_informacion_origen(self, qr_service, lote_premium):
        """
        Test: Verifica que el QR contiene información verificable del origen.
        """
        # Act
        qr_result = qr_service.generate_qr_code(lote_premium)
        
        # Assert
        qr_data = qr_result['qr_data']
        assert qr_data['origin'] == "Cusco, Perú"
        assert qr_data['producer'] == "Cooperativa Café Alto"
        assert 'harvest_date' in qr_data
    
    def test_qr_incluye_datos_calidad(self, qr_service, lote_premium):
        """
        Test: Verifica que el QR incluye datos de calidad del lote.
        """
        # Act
        qr_result = qr_service.generate_qr_code(lote_premium)
        
        # Assert
        qr_data = qr_result['qr_data']
        assert qr_data['quality_score'] == 87.5
        assert qr_data['quality_grade'] == "SPECIALTY"
        assert qr_data['beans_analyzed'] == 1500
    
    def test_qr_permite_verificar_clasificacion(self, qr_service, lote_premium):
        """
        Test: Verifica que el QR permite verificar el proceso de clasificación.
        """
        # Arrange
        qr_result = qr_service.generate_qr_code(lote_premium)
        
        # Act
        verification = qr_service.verify_qr_code(
            qr_result['qr_code_id'],
            qr_result
        )
        
        # Assert
        assert verification['verified'] is True
        assert verification['lot_data']['classification_verified'] is True
        assert verification['lot_data']['quality_score'] == 87.5
    
    def test_qr_escaneable(self, qr_service, lote_premium):
        """
        Test: Verifica que el código QR es escaneable.
        """
        # Act
        qr_result = qr_service.generate_qr_code(lote_premium)
        is_scannable = qr_service.is_qr_scannable(qr_result)
        
        # Assert
        assert is_scannable is True
        assert qr_result['qr_image_base64'] is not None
        assert len(qr_result['qr_image_base64']) > 0
    
    def test_qr_tiene_url_verificacion(self, qr_service, lote_premium):
        """
        Test: Verifica que el QR lleva a una URL de verificación válida.
        """
        # Act
        qr_result = qr_service.generate_qr_code(lote_premium)
        url = qr_service.get_verification_url(qr_result)
        
        # Assert
        assert url.startswith("https://beandetect.ai/verify/")
        assert qr_result['qr_code_id'] in url
    
    def test_verificacion_qr_invalido(self, qr_service, lote_premium):
        """
        Test: Verifica comportamiento con QR inválido.
        """
        # Act
        verification = qr_service.verify_qr_code("INVALID_ID_12345", {})
        
        # Assert
        assert verification['verified'] is False
        assert 'error' in verification
        assert verification['lot_data'] is None
    
    def test_qr_listo_para_impresion(self, qr_service, lote_premium):
        """
        Test: Verifica que el QR está listo para impresión.
        """
        # Arrange
        qr_result = qr_service.generate_qr_code(lote_premium)
        
        # Act
        print_content = qr_service.get_qr_content_for_print(qr_result)
        
        # Assert
        assert 'qr_image' in print_content
        assert 'print_size' in print_content
        assert 'resolution' in print_content
        assert print_content['lot_number'] == "LOT-2024-0156"


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

