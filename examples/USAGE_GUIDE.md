# Guía de Uso: Mapeo de Columnas y Formatos

## Soportar Diferentes Formatos

Tu herramienta ahora soporta **CSV**, **Excel** y **JSON**:

### Usar CSV
```bash
rh-report datos.csv
rh-report --format csv datos.csv
```

### Usar Excel
```bash
rh-report datos.xlsx
rh-report --format excel datos.xlsx
```

### Usar JSON
```bash
rh-report datos.json
rh-report --format json datos.json
```

## Mapeo de Columnas

Si tus columnas tienen nombres diferentes, usa un archivo de mapeo JSON.

### Estructura del archivo de mapeo

```json
{
  "nombre_columna_original": "nombre_esperado"
}
```

### Ejemplo

Si tu archivo tiene columnas `repo_name` y `container_image`, pero la herramienta espera `name` e `io.openshift.build.image`:

**mapping.json:**
```json
{
  "repo_name": "name",
  "container_image": "io.openshift.build.image"
}
```

**Uso:**
```bash
rh-report --mapping mapping.json datos.csv
```

## Casos de Uso Completos

### Caso 1: CSV con columnas personalizadas
```bash
rh-report --format csv --mapping config/my_mapping.json datos.csv -o resultado.csv
```

### Caso 2: JSON con mapeo
```bash
rh-report --format json --mapping mapping.json datos.json --workers 20
```

### Caso 3: Excel estándar (sin mapeo)
```bash
rh-report datos.xlsx
```

## Estructura de Datos JSON

El archivo JSON debe contener un array de objetos con al menos las columnas requeridas:

```json
[
  {
    "name": "rhel8/rhel",
    "io.openshift.build.image": "quay.io/rhel8/rhel:latest"
  },
  {
    "name": "rhel9/rhel",
    "io.openshift.build.image": "quay.io/rhel9/rhel:latest"
  }
]
```

## Flujo de Procesamiento

1. Cargar archivo (auto-detecta formato o usa `--format`)
2. Aplicar mapeo de columnas (si se proporciona con `--mapping`)
3. Validar que existan columnas requeridas: `name` e `io.openshift.build.image`
4. Procesar y enriquecer datos
5. Guardar resultado en CSV

## Ejemplos en el Repositorio

- `examples/column_mapping.json` - Configuración de mapeo básica
- `examples/data_example.json` - Datos de ejemplo en formato JSON
- `examples/mapping_alternate.json` - Mapeo alternativo
