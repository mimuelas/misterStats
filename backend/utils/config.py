"""
Configuración centralizada para la aplicación Mister Fantasy.
"""

import os
from typing import Dict, Any

# Configuración de la API
API_CONFIG = {
    'base_url': 'https://mister.mundodeportivo.com',
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 1
}

# Configuración de caché
CACHE_CONFIG = {
    'cache_dir': 'data/cache',
    'memory_cache_size': 1000,
    'file_cache_enabled': True,
    'durations': {
        'balance': 300,  # 5 minutos
        'standings': 600,  # 10 minutos
        'user_details': 1800,  # 30 minutos
        'player_details': 3600,  # 1 hora
        'market': 1800,  # 30 minutos
        'team': 1800,  # 30 minutos
        'search': 300,  # 5 minutos
        'feed': 600  # 10 minutos
    }
}

# Configuración de la aplicación
APP_CONFIG = {
    'title': 'Mister Stats Dashboard',
    'layout': 'wide',
    'theme': 'light',
    'debug': os.getenv('DEBUG', 'False').lower() == 'true'
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/mister_stats.log'
}

# Headers por defecto para las peticiones
DEFAULT_HEADERS = {
    "accept": "*/*",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "origin": "https://mister.mundodeportivo.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-auth": "596bd4e0ffacb9c557238afd0c58845c",
    "x-requested-with": "XMLHttpRequest",
    "partial-request": "true"
}

# Cookies por defecto
DEFAULT_COOKIES = {
    'PHPSESSID': '1abd2bafbb07652f780d8527477e83e4',
    'token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiIxNzU1MDQxOTk1IiwidXNlcmlkIjoiMjE0ODgzMiIsImFsZyI6IkVTMjU2In0.etY2S42q6vx6HdUfEtf1sDcD4iVWt4O_KG85hltMjoQsxKbm7Taiik2OvYzb0isCkBBzC58GKbUn4Ya517mcbA',
    'refresh-token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiI0OTEwNzE1Mjk1IiwicmVmcmVzaCI6ImZjT1oxV3pqQmNXMVI5RHA0akVnMiIsImlkX3Rva2VuX2xpZmV0aW1lX2luX21pbiI6IjUiLCJhbGciOiJFUzI1NiJ9.nrsEDmi0TKd0gdhl-AYYIHHdX-dLf6_k-AgDQoJElE5hVtFqmI-VAkNjhqIKh5OQtoh-yRG5ztabpY76azDVTw'
}

# Mapeo de posiciones
POSITION_MAP = {
    1: "Portero",
    2: "Defensa", 
    3: "Centrocampista",
    4: "Delantero"
}

# Configuración de filtros de búsqueda
SEARCH_FILTERS = {
    'positions': {
        0: 'Todas las posiciones',
        1: 'Portero',
        2: 'Defensa',
        3: 'Centrocampista',
        4: 'Delantero'
    },
    'value_ranges': {
        0: 'Todos los valores',
        1: 'Menos de 1M',
        2: '1M - 5M',
        3: '5M - 10M',
        4: '10M - 20M',
        5: 'Más de 20M'
    },
    'sort_options': {
        0: 'Puntos',
        1: 'Media',
        2: 'Racha',
        3: 'Valor',
        4: 'Cláusula'
    }
}

def get_config(section: str) -> Dict[str, Any]:
    """Obtiene la configuración de una sección específica."""
    configs = {
        'api': API_CONFIG,
        'cache': CACHE_CONFIG,
        'app': APP_CONFIG,
        'logging': LOGGING_CONFIG,
        'headers': DEFAULT_HEADERS,
        'cookies': DEFAULT_COOKIES,
        'positions': POSITION_MAP,
        'search': SEARCH_FILTERS
    }
    return configs.get(section, {})
