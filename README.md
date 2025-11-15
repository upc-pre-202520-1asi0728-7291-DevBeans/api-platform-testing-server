# BeanDetect AI - Backend API Testing Server

Servidor de Pruebas para el Backend desarrollado con FastAPI, Python y PostgreSQL (Supabase) siguiendo los patrones **CQRS** (Command Query Responsibility Segregation) y **DDD** (Domain-Driven Design).

## 🏗️ Arquitectura

El proyecto sigue una arquitectura hexagonal (puertos y adaptadores) con la siguiente estructura:

```
BeanDetectAI/
├── shared/                 # Código compartido y configuración global entre bounded contexts
├── iam_profile/            # Bounded Context: IAM & Profile
├── coffee_lot_management/  # Bounded Context: Coffee Lot Management
├── grain_classification/   # Bounded Context: Grain Classification
├── traceability_certification/ # Bounded Context: Traceability & Certification (TODO)
└── reporting_analytics/    # Bounded Context: Reporting & Analytics (TODO)
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.13
- PostgreSQL (Supabase)
- pip


## 📝 Estructura de Tests

Cada integration test sigue el patrón **AAA (Arrange-Act-Assert)**:

- **ARRANGE**: Preparación de datos y mocks
- **ACT**: Ejecución de la operación a probar
- **ASSERT**: Verificación de resultados esperados

### Pasos para la instalación del proyecto

**Clonar el repositorio**
```bash
git clone <repository-url>
cd BeanDetectAI
```

**Instalar dependencias**
```bash
pip install -r requirements.txt
```


## 🧪 Ejecución de Pruebas

**Primero, ejecutaremos el comando para instalar pytest-mock si no está instalado:**
```bash
pip install pytest pytest-mock
```

### Gestión de Lotes de Café (US06-US11)

**Ejecutar todas las pruebas de un integration test**
```bash
python -m pytest us_06_integration_test.py -v
python -m pytest us_07_integration_test.py -v
python -m pytest us_08_integration_test.py -v
python -m pytest us_09_integration_test.py -v
python -m pytest us_10_integration_test.py -v
python -m pytest us_11_integration_test.py -v
```

**Ejecutar unit test específica**

**Integration Test US-06: Creación de Lotes**

```bash
python -m pytest us_06_integration_test.py::TestUS06CreacionLotes::test_registrar_lote_exitoso -v
```

```bash
python -m pytest us_06_integration_test.py::TestUS06CreacionLotes::test_validacion_fecha_cosecha_futura -v
```

```bash
python -m pytest us_06_integration_test.py::TestUS06CreacionLotes::test_generacion_numero_lote_unico -v
```

**Integration Test US-07: Edición de Información de Lote**

```bash
python -m pytest us_07_integration_test.py::TestUS07EdicionInformacionLote::test_actualizar_cantidad_lote -v
```

```bash
python -m pytest us_07_integration_test.py::TestUS07EdicionInformacionLote::test_no_permitir_edicion_lote_clasificado -v
```

```bash
python -m pytest us_07_integration_test.py::TestUS07EdicionInformacionLote::test_actualizar_metodo_procesamiento -v
```

**Integration Test US-08: Visualización de Lotes por Productor**

```bash
python -m pytest us_08_integration_test.py::TestUS08VisualizacionLotesProductor::test_listar_todos_lotes_productor -v
```

```bash
python -m pytest us_08_integration_test.py::TestUS08VisualizacionLotesProductor::test_filtrar_lotes_por_estado -v
```

```bash
python -m pytest us_08_integration_test.py::TestUS08VisualizacionLotesProductor::test_filtrar_lotes_por_anio_cosecha -v
```

**Integration Test US-09: Visualización de Lotes por Cooperativa**

```bash
python -m pytest us_09_integration_test.py::TestUS09VisualizacionLotesCooperativa::test_agrupar_lotes_por_productor -v
```

```bash
python -m pytest us_09_integration_test.py::TestUS09VisualizacionLotesCooperativa::test_visualizar_estadisticas_por_productor -v
```

```bash
python -m pytest us_09_integration_test.py::TestUS09VisualizacionLotesCooperativa::test_filtrar_lotes_cooperativa_por_variedad -v
```

**Integration Test US-10: Búsqueda Rápida de Lotes**

```bash
python -m pytest us_10_integration_test.py::TestUS10BusquedaRapidaLotes::test_buscar_por_rango_fechas -v
```

```bash
python -m pytest us_10_integration_test.py::TestUS10BusquedaRapidaLotes::test_buscar_por_variedad_cafe -v
```

```bash
python -m pytest us_10_integration_test.py::TestUS10BusquedaRapidaLotes::test_buscar_con_multiples_filtros -v
```

**Integration Test US-11: Eliminación de Lotes**

```bash
python -m pytest us_11_integration_test.py::TestUS11EliminacionLotes::test_eliminar_lote_registrado -v
```

```bash
python -m pytest us_11_integration_test.py::TestUS11EliminacionLotes::test_no_eliminar_lote_clasificado -v
```

```bash
python -m pytest us_11_integration_test.py::TestUS11EliminacionLotes::test_verificar_existencia_antes_eliminar -v
```

### Clasificación de Granos (US12-US14)

**Ejecutar todas las pruebas de un integration test**
```bash
python -m pytest us_12_integration_test.py -v
python -m pytest us_13_integration_test.py -v
python -m pytest us_14_integration_test.py -v
```

**Ejecutar unit test específica**

**Integration Test US-12: Detección de Defectos Críticos**

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_detectar_granos_con_grietas -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_detectar_granos_oscuros_defectuosos -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_detectar_granos_verdes_inmaduros -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_penalizacion_por_forma_irregular -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_reporte_estadistico_defectos_lote -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_manejo_error_imagen_invalida -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_manejo_error_sin_granos_detectados -v
```

**Integration Test US-13: Análisis de Color y Uniformidad**

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_medicion_porcentajes_color_precisa -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_medicion_tamano_grano_area -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_bonificacion_por_tamano_grande -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_penalizacion_por_tamano_pequeno -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_uniformidad_lote_homogeneo -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_almacenamiento_caracteristicas_completas -v
```

```bash
python -m pytest us_13_integration_test.py::TestUS13AnalisisColorUniformidad::test_comparacion_lotes_diferentes_productores -v
```

**Integration Test US-14: Clasificación por Estándares Internacionales**

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_clasificacion_categoria_specialty -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_clasificacion_categoria_premium -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_reporte_lote_calidad_promedio -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_distribucion_categorias_por_lote -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_categoria_predominante_lote -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_almacenamiento_imagen_cloudinary -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_tiempo_procesamiento_registrado -v
```

```bash
python -m pytest us_14_integration_test.py::TestUS14ClasificacionEstandaresInternacionales::test_persistencia_sesion_completa -v
```