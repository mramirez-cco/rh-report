"""
Utilidades generales para carga/guardado de datos y cache
"""

import json
import os
import pandas as pd


def load_dataframe(file_path, format_type=None, column_mapping=None):
    """
    Carga un DataFrame desde CSV, Excel o JSON
    
    Args:
        file_path: Ruta al archivo
        format_type: Tipo de formato ('csv', 'json', 'excel'). Si es None, se detecta por extensión
        column_mapping: Diccionario con mapeo de columnas {columna_original: columna_nueva}
        
    Returns:
        DataFrame de pandas
        
    Raises:
        ValueError: Si el formato no es soportado
    """
    # Detectar formato por extensión si no se especifica
    if format_type is None:
        if file_path.endswith(".csv"):
            format_type = "csv"
        elif file_path.endswith(".xlsx"):
            format_type = "excel"
        elif file_path.endswith(".json"):
            format_type = "json"
        else:
            raise ValueError(
                f"Formato no soportado: {file_path}. "
                "Usa archivos .csv, .xlsx o .json"
            )
    
    # Cargar el archivo según el formato
    if format_type == "csv":
        df = pd.read_csv(file_path)
    elif format_type == "excel":
        df = pd.read_excel(file_path)
    elif format_type == "json":
        df = pd.read_json(file_path)
    else:
        raise ValueError(
            f"Formato no válido: {format_type}. "
            "Usa 'csv', 'excel' o 'json'"
        )
    
    # Aplicar mapeo de columnas si se proporciona
    if column_mapping:
        df = apply_column_mapping(df, column_mapping)
    
    return df


def save_cache(cache_file, data):
    """
    Guarda datos en archivo JSON como cache
    
    Args:
        cache_file: Ruta del archivo de cache
        data: Diccionario de datos a guardar
    """
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Error guardando cache: {e}")


def load_cache(cache_file):
    """
    Carga datos desde archivo JSON de cache
    
    Args:
        cache_file: Ruta del archivo de cache
        
    Returns:
        Diccionario con datos o None si falla
    """
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error cargando cache: {e}")
        return None


def validate_dataframe(df):
    """
    Valida que el DataFrame tenga las columnas requeridas
    
    Args:
        df: DataFrame a validar
        
    Returns:
        True si es válido
        
    Raises:
        ValueError: Si faltan columnas requeridas
    """
    required_columns = ["name", "io.openshift.build.image"]
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        raise ValueError(
            f"Columnas requeridas faltantes: {', '.join(missing)}\n"
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
    
    return True


def apply_column_mapping(df, column_mapping):
    """
    Aplica mapeo de columnas al DataFrame.
    Renombra las columnas según el mapeo proporcionado.
    
    Args:
        df: DataFrame original
        column_mapping: Diccionario {columna_original: columna_nueva}
        
    Returns:
        DataFrame con columnas renombradas
    """
    return df.rename(columns=column_mapping)


def load_mapping_config(mapping_file):
    """
    Carga configuración de mapeo de columnas desde archivo JSON.
    
    Ejemplo de archivo mapping.json:
    {
        "nombre_columna_original": "name",
        "imagen_contenedor": "io.openshift.build.image"
    }
    
    Args:
        mapping_file: Ruta al archivo JSON de configuración
        
    Returns:
        Diccionario con mapeo de columnas
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el JSON es inválido
    """
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo de mapeo no encontrado: {mapping_file}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error al parsear JSON de mapeo: {e.msg}",
            e.doc,
            e.pos
        )


def save_dataframe(df, output_file=None, output_format='csv', print_output=False):
    """
    Guarda un DataFrame en el formato especificado.
    Puede guardar en archivo o imprimir a stdout.
    
    Args:
        df: DataFrame a guardar
        output_file: Ruta del archivo de salida (opcional)
        output_format: Formato de salida ('csv', 'excel', 'json')
        print_output: Si True, imprime a stdout en lugar de guardar (solo para csv/json)
        
    Returns:
        Información sobre lo que se hizo
        
    Raises:
        ValueError: Si el formato no es válido
        IOError: Si hay error guardando el archivo
    """
    if output_format not in ['csv', 'excel', 'json']:
        raise ValueError(
            f"Formato no válido: {output_format}. "
            "Usa 'csv', 'excel' o 'json'"
        )
    
    # Excel siempre debe guardarse en archivo
    if output_format == 'excel':
        if not output_file:
            output_file = 'full_image_report.xlsx'
        
        if os.path.exists(output_file):
            os.remove(output_file)
        
        try:
            df.to_excel(output_file, index=False)
            return {
                'success': True,
                'format': 'excel',
                'mode': 'file',
                'output_file': output_file,
                'message': f'Reporte guardado en {output_file}'
            }
        except Exception as e:
            raise IOError(f"Error guardando archivo Excel: {e}")
    
    # CSV y JSON pueden imprimirse o guardarse
    if output_format == 'csv':
        if print_output:
            return {
                'success': True,
                'format': 'csv',
                'mode': 'stdout',
                'data': df.to_csv(index=False, sep=';'),
                'message': 'Datos impresos en stdout'
            }
        else:
            if not output_file:
                output_file = 'full_image_report.csv'
            
            if os.path.exists(output_file):
                os.remove(output_file)
            
            try:
                df.to_csv(output_file, index=False, sep=';')
                return {
                    'success': True,
                    'format': 'csv',
                    'mode': 'file',
                    'output_file': output_file,
                    'message': f'Reporte guardado en {output_file}'
                }
            except Exception as e:
                raise IOError(f"Error guardando archivo CSV: {e}")
    
    # JSON
    if output_format == 'json':
        if print_output:
            return {
                'success': True,
                'format': 'json',
                'mode': 'stdout',
                'data': df.to_json(orient='records', indent=2),
                'message': 'Datos impresos en stdout'
            }
        else:
            if not output_file:
                output_file = 'full_image_report.json'
            
            if os.path.exists(output_file):
                os.remove(output_file)
            
            try:
                df.to_json(output_file, orient='records', indent=2)
                return {
                    'success': True,
                    'format': 'json',
                    'mode': 'file',
                    'output_file': output_file,
                    'message': f'Reporte guardado en {output_file}'
                }
            except Exception as e:
                raise IOError(f"Error guardando archivo JSON: {e}")

