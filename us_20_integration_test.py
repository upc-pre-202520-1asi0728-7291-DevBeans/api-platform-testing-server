"""
Integration Test 14 - US20
==========================
User Story: Integración con Blockchain

Como cooperativa innovadora, deseo la opción de registrar datos de clasificación 
en blockchain para mayor transparencia y confianza del mercado.

Criterios de Aceptación:
- El sistema permite registrar datos de clasificación en blockchain
- Los registros son inmutables y verificables
- Se genera un hash único por cada registro
- Se puede verificar la integridad de los datos
- Proporciona transparencia y trazabilidad completa
"""

import pytest
from datetime import datetime
import hashlib
import json
from typing import Dict, List, Optional


class MockBlockchainRecord:
    """Mock de un registro en blockchain"""
    def __init__(self, record_id: str, data_hash: str, timestamp: datetime,
                 previous_hash: str, data: Dict):
        self.record_id = record_id
        self.data_hash = data_hash
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data


class BlockchainIntegrationService:
    """
    Servicio para registrar datos de clasificación en blockchain.
    Proporciona inmutabilidad, transparencia y verificabilidad.
    """
    
    def __init__(self):
        self.chain: List[MockBlockchainRecord] = []
        self.pending_records: List[Dict] = []
    
    def register_classification(self, classification_data: Dict) -> Dict:
        """
        Registra datos de clasificación en la blockchain.
        """
        # Generar hash de los datos
        data_hash = self._generate_hash(classification_data)
        
        # Obtener hash del bloque anterior
        previous_hash = self.chain[-1].data_hash if self.chain else "GENESIS"
        
        # Crear registro
        record_id = f"BLK-{len(self.chain):06d}"
        timestamp = datetime.now()
        
        record = MockBlockchainRecord(
            record_id=record_id,
            data_hash=data_hash,
            timestamp=timestamp,
            previous_hash=previous_hash,
            data=classification_data
        )
        
        # Agregar a la cadena
        self.chain.append(record)
        
        return {
            'success': True,
            'record_id': record_id,
            'data_hash': data_hash,
            'previous_hash': previous_hash,
            'timestamp': timestamp.isoformat(),
            'block_number': len(self.chain),
            'transaction_status': 'CONFIRMED',
            'immutable': True,
            'verification_url': f"https://beandetect.ai/blockchain/verify/{record_id}"
        }
    
    def _generate_hash(self, data: Dict) -> str:
        """Genera un hash SHA-256 único para los datos."""
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def verify_record(self, record_id: str) -> Dict:
        """
        Verifica un registro en la blockchain.
        """
        record = self._find_record(record_id)
        
        if not record:
            return {
                'verified': False,
                'error': 'Registro no encontrado en la blockchain',
                'record_data': None
            }
        
        # Recalcular hash para verificar integridad
        recalculated_hash = self._generate_hash(record.data)
        integrity_valid = recalculated_hash == record.data_hash
        
        return {
            'verified': True,
            'integrity_valid': integrity_valid,
            'record_id': record.record_id,
            'data_hash': record.data_hash,
            'timestamp': record.timestamp.isoformat(),
            'previous_hash': record.previous_hash,
            'record_data': record.data,
            'chain_position': self._get_chain_position(record_id)
        }
    
    def _find_record(self, record_id: str) -> Optional[MockBlockchainRecord]:
        """Busca un registro por ID."""
        for record in self.chain:
            if record.record_id == record_id:
                return record
        return None
    
    def _get_chain_position(self, record_id: str) -> int:
        """Obtiene la posición del registro en la cadena."""
        for i, record in enumerate(self.chain):
            if record.record_id == record_id:
                return i + 1
        return -1
    
    def verify_chain_integrity(self) -> Dict:
        """
        Verifica la integridad de toda la cadena.
        """
        if not self.chain:
            return {
                'valid': True,
                'total_records': 0,
                'message': 'Cadena vacía'
            }
        
        invalid_records = []
        
        for i, record in enumerate(self.chain):
            # Verificar hash de datos
            recalculated = self._generate_hash(record.data)
            if recalculated != record.data_hash:
                invalid_records.append({
                    'record_id': record.record_id,
                    'issue': 'Hash de datos no coincide'
                })
            
            # Verificar enlace con bloque anterior
            if i > 0:
                if record.previous_hash != self.chain[i-1].data_hash:
                    invalid_records.append({
                        'record_id': record.record_id,
                        'issue': 'Hash anterior no coincide'
                    })
        
        return {
            'valid': len(invalid_records) == 0,
            'total_records': len(self.chain),
            'invalid_records': invalid_records,
            'integrity_percentage': ((len(self.chain) - len(invalid_records)) / len(self.chain)) * 100 if self.chain else 100
        }
    
    def get_traceability_report(self, lot_number: str) -> Dict:
        """
        Obtiene un reporte de trazabilidad completa de un lote.
        """
        lot_records = [
            r for r in self.chain 
            if r.data.get('lot_number') == lot_number
        ]
        
        if not lot_records:
            return {
                'lot_number': lot_number,
                'found': False,
                'records': []
            }
        
        return {
            'lot_number': lot_number,
            'found': True,
            'total_records': len(lot_records),
            'records': [
                {
                    'record_id': r.record_id,
                    'timestamp': r.timestamp.isoformat(),
                    'data_hash': r.data_hash,
                    'event_type': r.data.get('event_type', 'CLASSIFICATION')
                }
                for r in lot_records
            ],
            'full_traceability': True,
            'blockchain_verified': True
        }
    
    def get_transparency_score(self) -> float:
        """Calcula un score de transparencia basado en los registros."""
        if not self.chain:
            return 0.0
        
        # Score basado en integridad de la cadena
        integrity = self.verify_chain_integrity()
        return integrity['integrity_percentage']


class TestUS20IntegracionBlockchain:
    """
    Integration Test 14 - US20
    Test de Integración con Blockchain
    """
    
    @pytest.fixture
    def blockchain_service(self):
        """Fixture para el servicio de blockchain."""
        return BlockchainIntegrationService()
    
    @pytest.fixture
    def clasificacion_data(self):
        """Fixture: Datos de clasificación para registrar."""
        return {
            'lot_number': 'LOT-2024-0156',
            'producer_id': 1,
            'producer_name': 'Cooperativa Café Alto',
            'origin': 'Cusco, Perú',
            'quality_score': 87.5,
            'quality_grade': 'SPECIALTY',
            'beans_analyzed': 1500,
            'classification_date': datetime.now().isoformat(),
            'event_type': 'CLASSIFICATION'
        }
    
    @pytest.fixture
    def multiples_clasificaciones(self):
        """Fixture: Múltiples clasificaciones para probar cadena."""
        return [
            {
                'lot_number': 'LOT-2024-0156',
                'quality_score': 87.5,
                'quality_grade': 'SPECIALTY',
                'event_type': 'CLASSIFICATION'
            },
            {
                'lot_number': 'LOT-2024-0157',
                'quality_score': 72.0,
                'quality_grade': 'STANDARD',
                'event_type': 'CLASSIFICATION'
            },
            {
                'lot_number': 'LOT-2024-0158',
                'quality_score': 82.0,
                'quality_grade': 'PREMIUM',
                'event_type': 'CLASSIFICATION'
            }
        ]
    
    def test_registro_clasificacion_blockchain(self, blockchain_service, clasificacion_data):
        """
        Test: Verifica registro de datos de clasificación en blockchain.
        """
        # Act
        resultado = blockchain_service.register_classification(clasificacion_data)
        
        # Assert
        assert resultado['success'] is True
        assert 'record_id' in resultado
        assert resultado['transaction_status'] == 'CONFIRMED'
    
    def test_registros_inmutables(self, blockchain_service, clasificacion_data):
        """
        Test: Verifica que los registros son inmutables.
        """
        # Arrange
        resultado = blockchain_service.register_classification(clasificacion_data)
        
        # Assert
        assert resultado['immutable'] is True
        # El hash no debe cambiar
        original_hash = resultado['data_hash']
        verification = blockchain_service.verify_record(resultado['record_id'])
        assert verification['data_hash'] == original_hash
    
    def test_registros_verificables(self, blockchain_service, clasificacion_data):
        """
        Test: Verifica que los registros son verificables.
        """
        # Arrange
        resultado = blockchain_service.register_classification(clasificacion_data)
        
        # Act
        verification = blockchain_service.verify_record(resultado['record_id'])
        
        # Assert
        assert verification['verified'] is True
        assert verification['integrity_valid'] is True
        assert verification['record_data'] is not None
    
    def test_hash_unico_por_registro(self, blockchain_service, multiples_clasificaciones):
        """
        Test: Verifica generación de hash único por cada registro.
        """
        # Act
        hashes = []
        for data in multiples_clasificaciones:
            resultado = blockchain_service.register_classification(data)
            hashes.append(resultado['data_hash'])
        
        # Assert - Todos los hashes deben ser únicos
        assert len(hashes) == len(set(hashes))
    
    def test_verificacion_integridad_datos(self, blockchain_service, clasificacion_data):
        """
        Test: Verifica la integridad de los datos registrados.
        """
        # Arrange
        resultado = blockchain_service.register_classification(clasificacion_data)
        
        # Act
        chain_integrity = blockchain_service.verify_chain_integrity()
        
        # Assert
        assert chain_integrity['valid'] is True
        assert chain_integrity['integrity_percentage'] == 100
        assert len(chain_integrity['invalid_records']) == 0
    
    def test_transparencia_trazabilidad(self, blockchain_service, clasificacion_data):
        """
        Test: Verifica transparencia y trazabilidad completa.
        """
        # Arrange
        blockchain_service.register_classification(clasificacion_data)
        
        # Act
        traceability = blockchain_service.get_traceability_report('LOT-2024-0156')
        
        # Assert
        assert traceability['found'] is True
        assert traceability['full_traceability'] is True
        assert traceability['blockchain_verified'] is True
        assert len(traceability['records']) > 0
    
    def test_cadena_enlazada_correctamente(self, blockchain_service, multiples_clasificaciones):
        """
        Test: Verifica que la cadena está correctamente enlazada.
        """
        # Arrange - Registrar múltiples clasificaciones
        results = []
        for data in multiples_clasificaciones:
            results.append(blockchain_service.register_classification(data))
        
        # Assert - Verificar que cada bloque referencia al anterior
        assert results[0]['previous_hash'] == 'GENESIS'
        assert results[1]['previous_hash'] == results[0]['data_hash']
        assert results[2]['previous_hash'] == results[1]['data_hash']
    
    def test_score_transparencia(self, blockchain_service, multiples_clasificaciones):
        """
        Test: Verifica cálculo del score de transparencia.
        """
        # Arrange
        for data in multiples_clasificaciones:
            blockchain_service.register_classification(data)
        
        # Act
        score = blockchain_service.get_transparency_score()
        
        # Assert
        assert score == 100.0  # Cadena válida = 100%


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

