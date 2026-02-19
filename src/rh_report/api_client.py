"""
Cliente para interactuar con el Red Hat Catalog API
Incluye manejo de concurrencia y reintentos automáticos
"""

import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://catalog.redhat.com/api/containers/v1"
CATALOG_WEB_URL = "https://catalog.redhat.com/en/software/containers"


class CatalogAPIClient:
    """Cliente optimizado para Red Hat Catalog API"""
    
    def __init__(self, max_workers=10, timeout=10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self):
        """Crea sesión con reintentos automáticos"""
        session = requests.Session()
        session.headers.update({"Accept": "application/json"})
        
        # Configurar reintentos
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def fetch_repositories(self, repository_names):
        """
        Consulta información de múltiples repositorios concurrentemente
        Incluye consulta de latest_image en la misma pasada
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single_repository, name): name
                for name in repository_names
            }
            
            for future in tqdm(as_completed(futures), total=len(futures), 
                             desc="Consultando repositorios"):
                repository_name = futures[future]
                try:
                    results[repository_name] = future.result()
                except Exception as e:
                    results[repository_name] = {
                        "repository": "not_found",
                        "registry": "not_found",
                        "error": str(e)
                    }
        
        return results
    
    def _fetch_single_repository(self, repository_name):
        """Consulta un solo repositorio y su latest_image"""
        params = {
            "filter": f'repository=="{repository_name}"',
            "include": [
                "data._id",
                "data.registry",
                "data.repository",
                "data.release_categories",
                "data.replaced_by_repository_name"
            ],
        }
        
        # Consultar info básica del repositorio
        repo_info = self._get_repository_info(params)
        
        # Si el repositorio existe, consultar su latest_image
        if repo_info.get("repository") != "not_found":
            latest_image_params = {
                "filter": 'architecture=="amd64"',
                "include": [
                    "data._id",
                    "data.brew.build",
                    "data.creation_date",
                    "data.image_id",
                    "data.freshness_grades.grade",
                    "data.freshness_grades.start_date",
                    "data.repositories.repository",
                    "data.repositories.tags"
                ],
                "page_size": 1,
            }
            
            repo_info["latest_image"] = self._get_repository_images(
                repo_info.get("registry"),
                repo_info.get("replaced_by_repository_name"),
                latest_image_params
            )
        else:
            repo_info["latest_image"] = {"image": "not_found"}
        
        return repo_info
    
    def _get_repository_info(self, params, only_basic=False):
        """Consulta información básica del repositorio"""
        base_url = f"{BASE_URL}/repositories"
        
        try:
            response = self.session.get(base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json().get("data", [])
            
            if not data:
                return {"repository": "not_found", "registry": "not_found"}
            
            if only_basic:
                return {"repository_id": data[0]["_id"]}
            
            data_dict = {
                "repository_id": data[0]["_id"],
                "repository": data[0]["repository"],
                "registry": data[0]["registry"],
                "release_categories": data[0]["release_categories"][0],
                "replaced_by_repository_name": data[0].get(
                    "replaced_by_repository_name", data[0]["repository"]
                ),
                "repository_url": f"{CATALOG_WEB_URL}/{data[0]['repository']}/{quote(data[0]['_id'])}",
            }
            
            # Si está deprecado, buscar el reemplazo
            if data_dict["release_categories"] == "Deprecated":
                temp_params = {
                    "filter": f'repository=="{data_dict["replaced_by_repository_name"]}"',
                    "include": ["data._id"]
                }
                replaced_info = self._get_repository_info(temp_params, only_basic=True)
                data_dict["repository_replaced_id"] = replaced_info.get("repository_id", "not_found")
                data_dict["repository_replaced_url"] = (
                    f"{CATALOG_WEB_URL}/{data_dict['replaced_by_repository_name']}/"
                    f"{quote(data_dict['repository_replaced_id'])}"
                )
            
            return data_dict
            
        except requests.HTTPError as e:
            return {
                "repository": "not_found",
                "registry": "not_found",
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except requests.RequestException as e:
            return {
                "repository": "not_found",
                "registry": "not_found",
                "error": "request_failed",
                "detail": str(e),
            }
    
    def _get_repository_images(self, registry, repository, params):
        """Consulta imágenes de un repositorio"""
        base_url = (
            f"{BASE_URL}/repositories/registry/{quote(registry, safe='')}"
            f"/repository/{quote(repository, safe='')}/tag/latest"
        )
        
        try:
            response = self.session.get(base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json().get("data", [])
            
            if params.get("page_size") == 1:
                return data[0] if data else {"image": "not_found"}
            
            return data
            
        except requests.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except requests.RequestException as e:
            return {"error": "request_failed", "detail": str(e)}
    
    def fetch_images(self, image_names):
        """Consulta información de múltiples imágenes concurrentemente"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single_image, name): name
                for name in image_names
            }

            for future in tqdm(as_completed(futures), total=len(futures),
                             desc="Consultando imágenes"):
                image_name = futures[future]
                try:
                    results[image_name] = future.result()
                except Exception as e:
                    results[image_name] = {
                        "image": "not_found",
                        "error": str(e)
                    }

        return results

    def _fetch_single_image(self, image_name):
        """Consulta una sola imagen por su hash"""
        _, _, digest = image_name.partition("sha256:")
        hash_value = f"sha256:{digest}" if digest else "not_found"

        if hash_value == "not_found":
            return {"image": "not_found"}

        params = {
            "filter": f'image_id=="{hash_value}"',
            "include": [
                "data._id",
                "data.brew.build",
                "data.creation_date",
                "data.image_id",
                "data.freshness_grades.grade",
                "data.freshness_grades.start_date",
                "data.repositories.tags",
            ],
            "page_size": 1,
        }

        return self._get_image_info(params)

    def _get_image_info(self, params):
        """Consulta información de una imagen"""
        base_url = f"{BASE_URL}/images"

        try:
            response = self.session.get(base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json().get("data", [])

            if params.get("page_size") == 1:
                return data[0] if data else {"image": "not_found"}

            return data if data else {}

        except requests.HTTPError as e:
            return {
                "image": "not_found",
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except requests.RequestException as e:
            return {
                "image": "not_found",
                "error": "request_failed",
                "detail": str(e)
            }

    def __del__(self):
        """Cerrar sesión al destruir el objeto"""
        if hasattr(self, 'session'):
            self.session.close()
