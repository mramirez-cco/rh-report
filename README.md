# Red Hat Catalog Image Reporter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Herramienta CLI optimizada para consultar y reportar información de imágenes de contenedores desde el Red Hat Catalog.

## ✨ Características

- 🚀 **Requests concurrentes** con ThreadPoolExecutor (5-10x más rápido)
- 💾 **Sistema de cache** para evitar reconsultas innecesarias
- 🔄 **Reintentos automáticos** en caso de fallos de red
- 📊 **Procesamiento optimizado** de DataFrames
- 🎯 **CLI intuitiva** con Click
- 🏗️ **Código modular** y mantenible
- 📦 **Instalable con pip** como paquete Python

## 📁 Estructura del Proyecto

```
rh-report/
├── src/
│   └── rh_report/
│       ├── __init__.py
│       ├── cli.py              # CLI principal
│       ├── api_client.py       # Cliente API con concurrencia
│       ├── data_enrichment.py  # Enriquecimiento de datos
│       └── utils.py            # Utilidades generales
├── tests/                      # Tests unitarios
├── Makefile                    # Automatización de tareas
├── setup.py                    # Configuración del paquete
├── pyproject.toml             # Configuración moderna
├── requirements.txt           # Dependencias
├── MANIFEST.in               # Archivos adicionales
├── LICENSE                   # Licencia MIT
└── README.md                # Este archivo
```

## 🚀 Instalación

### Opción 1: Desde el repositorio (desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/mramirez-cco/rh-report.git
cd rh-report

# Instalar usando Make
make install

# O manualmente
pip install -e .
```

### Opción 2: Desde PyPI (cuando esté publicado)

```bash
pip install git+https://github.com/mramirez-cco/rh-report.git
```

### Opción 3: Crear entorno virtual

```bash
# Crear entorno virtual
make venv
source venv/bin/activate

# Instalar
make install
```

## 📖 Uso

### Uso básico

```bash
rh-report reporte.xlsx
```

### Opciones disponibles

```bash
rh-report [OPCIONES] INPUT_FILE

Opciones:
  -o, --output TEXT       Archivo de salida CSV (default: full_image_report.csv)
  -w, --workers INTEGER   Número de workers concurrentes (default: 10)
  --version              Muestra la versión
  --help                 Muestra este mensaje
```

### Ejemplos

```bash
# Con 20 workers concurrentes (más rápido)
rh-report --workers 20 reporte.xlsx

# Especificar archivo de salida
rh-report -o mi_reporte.csv reporte.xlsx

# Combinando opciones
rh-report -w 15 -o output.csv reporte.xlsx
```

## 🛠️ Makefile - Comandos disponibles

```bash
# Ver todos los comandos disponibles
make help

# Instalación y configuración
make install          # Instala en modo editable
make install-dev      # Instala con dependencias de desarrollo
make uninstall        # Desinstala el paquete
make venv            # Crea entorno virtual

# Limpieza
make clean           # Limpia archivos temporales y cache

# Desarrollo
make format          # Formatea código con black
make lint           # Ejecuta linter (flake8)
make typecheck      # Verifica tipos con mypy
make test           # Ejecuta tests
make check          # Ejecuta lint + typecheck

# Construcción y publicación
make build          # Construye el paquete
make publish        # Publica a PyPI
make publish-test   # Publica a TestPyPI

# Utilidades
make run            # Ejecuta con archivo de ejemplo
make stats          # Muestra estadísticas del código
make upgrade-deps   # Actualiza dependencias
```

## 📊 Formato de entrada

El archivo de entrada (Excel o CSV) debe contener al menos estas columnas:

- `name`: Nombre del repositorio
- `io.openshift.build.image`: Hash de la imagen (formato: `registry/repo@sha256:...`)

## 📝 Formato de salida

El CSV de salida incluye todas las columnas originales más:

| Columna | Descripción |
|---------|-------------|
| `current_repo_url` | URL del repositorio actual |
| `replace_repo_url` | URL del repositorio de reemplazo (si aplica) |
| `current_release_category` | Categoría de lanzamiento |
| `current_image_url` | URL de la imagen actual |
| `latest_image_url` | URL de la última imagen disponible |
| `current_image_creation_date` | Fecha de creación de la imagen actual |
| `current_image_grade` | Grade de salud de la imagen actual |
| `current_image_tag` | Tag de la imagen actual |
| `latest_image_tag` | Tag de la última imagen |
| `latest_image_brew_build` | Brew build de la última imagen |
| `latest_image_creation_date` | Fecha de la última imagen |
| `latest_image_grade` | Grade de la última imagen |


## 🔧 Configuración avanzada

### Ajustar timeout de requests

Edita `src/rh_report/api_client.py`:

```python
client = CatalogAPIClient(max_workers=10, timeout=20)  # 20 segundos
```

### Modificar estrategia de reintentos

Edita el método `_create_session()` en `api_client.py`:

```python
retry_strategy = Retry(
    total=5,           # Intentos totales
    backoff_factor=2,  # Factor de backoff
    status_forcelist=[429, 500, 502, 503, 504]
)
```

## 🐛 Troubleshooting

### Error: "Columnas requeridas faltantes"

Verifica que tu archivo tenga las columnas `name` y `io.openshift.build.image`.

### Timeout frecuentes

Aumenta el timeout o reduce el número de workers:

```bash
rh-report --workers 5 reporte.xlsx
```

### Comando no encontrado después de instalar

Verifica que la instalación fue exitosa:

```bash
pip show rh-report
```

Si está instalado pero no funciona, intenta:

```bash
python -m rh_report.cli --help
```

## 📈 Desarrollo

### Configurar entorno de desarrollo

```bash
# Instalar con dependencias de desarrollo
make install-dev

# Ejecutar tests
make test

# Formatear código
make format

# Verificar código
make check
```

### Estructura de tests

```bash
tests/
├── __init__.py
├── test_api_client.py
├── test_data_enrichment.py
└── test_utils.py
```

### Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📊 Performance

### Benchmarks

Asumiendo ~100 repositorios y ~100 imágenes:

- **Original**: ~200 requests secuenciales = 200-300 segundos
- **Optimizado**: ~200 requests con 10 workers = 20-40 segundos

**Mejora: 5-10x más rápido** ⚡

### Recomendaciones

- Para datasets pequeños (<50 items): `--workers 5`
- Para datasets medianos (50-200 items): `--workers 10` (default)
- Para datasets grandes (>200 items): `--workers 20`

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Créditos

Desarrollado usando:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Requests](https://requests.readthedocs.io/) - HTTP library
- [tqdm](https://tqdm.github.io/) - Progress bars

## 📞 Soporte

- 🐛 [Reportar un bug](https://github.com/tuusuario/rh-report/issues)
- 💡 [Solicitar una feature](https://github.com/tuusuario/rh-report/issues)
- 📧 Email: tu@email.com

---

Hecho con 🚀 por [Tu Nombre](https://github.com/tuusuario)
