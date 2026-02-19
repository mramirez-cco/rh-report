# Guía de Uso: rh-report

## Soportar Diferentes Formatos de ENTRADA

Tu herramienta ahora soporta **CSV**, **Excel** y **JSON** para entrada:

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

## Formato de SALIDA

Controla el formato de salida con `--output-format`:

### Salida CSV (default)
```bash
rh-report datos.xlsx                           # Default a CSV
rh-report --output-format csv datos.xlsx       # Explícitamente
rh-report --output-format csv -o reporte.csv datos.xlsx
```

### Salida Excel
```bash
rh-report --output-format excel datos.xlsx
rh-report --output-format excel -o reporte.xlsx datos.csv
```

### Salida JSON
```bash
rh-report --output-format json datos.xlsx
rh-report --output-format json -o reporte.json datos.csv
```

## Imprimir a stdout

Para CSV y JSON, puedes imprimir el resultado en stdout en lugar de guardarlo en archivo:

```bash
# Imprimir CSV a stdout
rh-report --output-format csv --print datos.xlsx

# Imprimir JSON a stdout (útil para piping)
rh-report --output-format json --print datos.xlsx | jq '.[] | .name'
```

**Nota**: `--print` solo funciona con CSV y JSON. Excel siempre se guarda en archivo.

## Mapeo de Columnas

Si tus columnas tienen nombres diferentes, usa un archivo de mapeo JSON.

### Estructura del archivo de mapeo

```json
{
  "nombre_columna_original": "nombre_esperado"
}
```

### Ejemplo

Si tu archivo tiene columnas `repo_name` y `container_image`:

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

### Caso 1: CSV con columnas personalizadas → JSON a stdout
```bash
rh-report --format csv --mapping config/my_mapping.json --output-format json --print datos.csv
```

### Caso 2: JSON → Excel guardado
```bash
rh-report --format json --output-format excel -o reporte.xlsx datos.json
```

### Caso 3: Excel → CSV guardado
```bash
rh-report --output-format csv -o resultado.csv datos.xlsx
```

### Caso 4: CSV con 20 workers → JSON a stdout
```bash
rh-report --workers 20 --output-format json --print datos.csv
```

### Caso 5: Entrada con mapeo → Salida con formato específico
```bash
rh-report --mapping mapping.json --output-format excel -o reporte.xlsx datos.csv
```

## Opciones de CLI Completas

```
INPUT_FILE                        Archivo de entrada (requerido)

Opciones de transformación de entrada:
  --format, -f                   Formato de entrada (csv/excel/json, auto-detectado)
  --mapping, -m <archivo>        Archivo JSON con mapeo de columnas

Opciones de salida:
  --output-format <formato>      Formato de salida (csv/excel/json, default: csv)
  --output, -o <archivo>         Archivo de salida (opcional)
  --print                        Imprimir a stdout en lugar de guardar (csv/json)

Opciones de procesamiento:
  --workers, -w <num>            Número de workers concurrentes (default: 10)

Ayuda:
  --help                         Mostrar ayuda
  --version                      Mostrar versión
```

## Estructura de Datos JSON

El archivo JSON debe contener un array de objetos con las columnas requeridas:

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
3. Validar columnas requeridas: `name` e `io.openshift.build.image`
4. Procesar y enriquecer datos consultando Red Hat Catalog API
5. Guardar o imprimir resultado en formato especificado
