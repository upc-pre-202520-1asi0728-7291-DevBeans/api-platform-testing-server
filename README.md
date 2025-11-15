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

### Pasos de instalación

**Clonar el repositorio**
```bash
git clone <repository-url>
cd BeanDetectAI
```

**Instalar dependencias**
```bash
pip install -r requirements.txt
```

**Inicializar el proyecto**
```bash
# Las tablas se crean automáticamente al iniciar la aplicación
python main.py
```

## 🧪 Ejecución de Pruebas

**Primero, ejecutaremos el comando para instalar pytest-mock si no está instalado:**
```bash
pip install pytest pytest-mock
```

**Ejecutar todas las pruebas de un integration test**
```bash
python -m pytest us_12_integration_test.py -v
```

```bash
python -m pytest us_13_integration_test.py -v
```

```bash
python -m pytest us_14_integration_test.py -v```
```

**Ejecutar unit test específica**

Integration Test US-12

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
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_reporte_estadistico_defectos_lot -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_manejo_error_imagen_invalida -v
```

```bash
python -m pytest us_12_integration_test.py::TestUS12DeteccionDefectosCriticos::test_manejo_error_sin_granos_detectados -v
```

Integration Test US-13

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

Integration Test US-14

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