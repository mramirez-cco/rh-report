"""
Funciones para enriquecer el DataFrame con información del API
Optimizado para procesar múltiples columnas en una sola pasada
"""

import pandas as pd
from datetime import datetime, timezone


def enrich_dataframe(df, results, current_image_results):
    """
    Enriquece el DataFrame con información de repositorios e imágenes
    Procesa todas las columnas en una sola pasada para optimizar rendimiento
    """

    def enrich_row(row):
        """Procesa una fila y retorna todas las columnas nuevas"""
        name = row['name']
        img_name = row['io.openshift.build.image']

        # URLs del repositorio actual
        current_repo_url = get_current_repo_url(results, name)
        replace_repo_url = get_replace_repo_url(results, name)

        # Información de la imagen actual
        current_image_data = current_image_results.get(img_name, {})

        return pd.Series({
            'current_repo_url': current_repo_url,
            'current_image_url': get_current_image_url(current_image_data, current_repo_url),
            'current_image_creation_date': current_image_data.get("creation_date", "not_found"),
            'current_image_grade': get_health_index_grade(
                current_image_data.get("freshness_grades", "not_found")
            ),
            'current_image_brew_build': current_image_data.get("brew", {}).get("build", "not_found"),
            'current_image_tag': get_latest_tag(
                current_image_data.get("repositories", "not_found")
            ),
            'current_release_category': get_current_release_category(results, name),
            'replace_repo_url': replace_repo_url,
            'latest_image_url': get_latest_image_url(results, name),
            'latest_image_brew_build': get_latest_image_brew_build(results, name),
            'latest_image_tag': get_latest_image_tag(results, name),
            'latest_image_creation_date': get_latest_image_creation_date(results, name),
            'latest_image_grade': get_latest_image_grade(results, name),
        })

    # Aplicar enriquecimiento a todas las filas
    enriched_data = df.apply(enrich_row, axis=1)

    # Concatenar con el DataFrame original
    return pd.concat([df, enriched_data], axis=1)


def get_health_index_grade(grades):
    """
    Dada una lista de freshness_grades, devuelve el grade
    con la fecha más reciente que NO sea futura.
    """
    if grades == "not_found" or not grades:
        return "not_found"

    now = datetime.now(timezone.utc)

    def parse_date(grade):
        return datetime.fromisoformat(grade["start_date"].replace("Z", "+00:00"))

    # Filtrar solo fechas <= ahora
    valid_grades = [grade for grade in grades if parse_date(grade) <= now]

    if not valid_grades:
        return "not_found"

    latest_grade = max(valid_grades, key=parse_date)
    return latest_grade["grade"]


def get_latest_tag(repositories):
    """Devuelve el nombre del tag más reciente o 'not_found'"""
    if not isinstance(repositories, list):
        return "not_found"

    def parse_date(tag):
        return datetime.fromisoformat(tag["added_date"].replace("Z", "+00:00"))

    try:
        latest_tag = max(
            (
                tag
                for repo in repositories
                if isinstance(repo, dict)
                for tag in repo.get("tags", [])
                if isinstance(tag, dict) and "added_date" in tag and "name" in tag
            ),
            key=parse_date
        )
        return latest_tag["name"]
    except ValueError:
        return "not_found"


def get_current_repo_url(image_name_dict, name):
    """Retorna la URL del repositorio de la imagen actual"""
    image_data = image_name_dict.get(name, {})
    return image_data.get("repository_url", "not_found")


def get_replace_repo_url(image_name_dict, name):
    """Retorna la URL del repositorio que reemplaza a la imagen actual"""
    image_data = image_name_dict.get(name, {})
    return image_data.get("repository_replaced_url", "not_found")


def get_current_release_category(image_name_dict, name):
    """Retorna la categoría de lanzamiento de la imagen actual"""
    image_data = image_name_dict.get(name, {})
    return image_data.get("release_categories", "not_found")


def get_current_image_url(current_image_data, current_repo_url):
    """Retorna la URL de la imagen actual en el catálogo"""
    image_id = current_image_data.get('_id', 'not_found')
    return f"{current_repo_url}?image={image_id}"


def get_latest_image_url(image_name_dict, name):
    """Retorna la URL de la última imagen disponible"""
    repo_data = image_name_dict.get(name, {})
    base_url = repo_data.get('repository_replaced_url', repo_data.get("repository_url"))
    image_id = repo_data.get('latest_image', {}).get('_id', 'not_found')
    return f"{base_url}?image={image_id}"


def get_latest_image_tag(image_name_dict, name):
    """Retorna el tag más reciente de la última imagen"""
    image_entry = image_name_dict.get(name)
    if not image_entry:
        return "not_found"

    image_data = image_entry.get("latest_image", {})
    repositories = image_data.get("repositories")

    if not repositories:
        return "not_found"

    return get_latest_tag(repositories)


def get_latest_image_creation_date(image_name_dict, name):
    """Retorna el creation_date de la última imagen"""
    image_data = image_name_dict.get(name, {}).get("latest_image", {})
    return image_data.get("creation_date", "not_found")

def get_latest_image_brew_build(image_name_dict, name):
    """Retorna el brew build de la última imagen"""
    image_data = image_name_dict.get(name, {}).get("latest_image", {})
    return image_data.get("brew", {}).get("build", "not_found")

def get_latest_image_grade(image_name_dict, name):
    """Retorna el health index grade de la última imagen"""
    image_data = image_name_dict.get(name, {}).get("latest_image", {})
    grades = image_data.get("freshness_grades", "not_found")
    return get_health_index_grade(grades)
