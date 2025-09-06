"""
Definición completa de todos los endpoints disponibles en Mister Fantasy API.
Basado en el análisis del .har y conocimiento de la plataforma.
"""

# Endpoints ya implementados
IMPLEMENTED_ENDPOINTS = {
    # Autenticación y Balance
    'balance': {
        'url': '/ajax/balance',
        'method': 'POST',
        'description': 'Obtiene el balance de la cuenta',
        'response_type': 'json'
    },
    
    # Clasificaciones
    'standings': {
        'url': '/standings',
        'method': 'POST',
        'description': 'Obtiene la clasificación de la liga',
        'response_type': 'html'
    },
    
    # Usuarios
    'user_details': {
        'url': '/ajax/sw/users',
        'method': 'POST',
        'description': 'Obtiene detalles completos de un usuario',
        'response_type': 'json',
        'params': ['id', 'slug', 'comments']
    },
    
    # Jugadores
    'player_details': {
        'url': '/ajax/sw/players',
        'method': 'POST',
        'description': 'Obtiene detalles de un jugador específico',
        'response_type': 'json',
        'params': ['id', 'slug', 'comments']
    },
    
    'player_search': {
        'url': '/ajax/sw/players',
        'method': 'POST',
        'description': 'Busca jugadores con filtros',
        'response_type': 'json',
        'params': ['filters', 'offset', 'order', 'name']
    },
    
    # Mercado
    'market': {
        'url': '/market',
        'method': 'POST',
        'description': 'Obtiene la página del mercado',
        'response_type': 'html'
    },
    
    # Equipo
    'team': {
        'url': '/team',
        'method': 'POST',
        'description': 'Obtiene la página del equipo del usuario',
        'response_type': 'html'
    },
    
    # Búsqueda
    'search': {
        'url': '/search',
        'method': 'POST',
        'description': 'Página de búsqueda general',
        'response_type': 'html'
    },
    
    # Feed
    'feed': {
        'url': '/feed',
        'method': 'POST',
        'description': 'Feed de noticias y eventos',
        'response_type': 'html'
    }
}

# Endpoints adicionales que podríamos implementar
ADDITIONAL_ENDPOINTS = {
    # Transacciones y Mercado
    'transfers': {
        'url': '/transfers',
        'method': 'GET',
        'description': 'Historial de transferencias',
        'response_type': 'html'
    },
    
    'market_history': {
        'url': '/market/history',
        'method': 'GET',
        'description': 'Historial del mercado',
        'response_type': 'html'
    },
    
    'auctions': {
        'url': '/auctions',
        'method': 'GET',
        'description': 'Subastas activas',
        'response_type': 'html'
    },
    
    'bids': {
        'url': '/bids',
        'method': 'GET',
        'description': 'Pujas del usuario',
        'response_type': 'html'
    },
    
    # Estadísticas y Análisis
    'stats': {
        'url': '/stats',
        'method': 'GET',
        'description': 'Estadísticas generales',
        'response_type': 'html'
    },
    
    'analytics': {
        'url': '/analytics',
        'method': 'GET',
        'description': 'Análisis avanzados',
        'response_type': 'html'
    },
    
    'leaderboard': {
        'url': '/leaderboard',
        'method': 'GET',
        'description': 'Ranking de jugadores',
        'response_type': 'html'
    },
    
    # Ligas y Comunidades
    'leagues': {
        'url': '/leagues',
        'method': 'GET',
        'description': 'Lista de ligas',
        'response_type': 'html'
    },
    
    'league_details': {
        'url': '/league/{id}',
        'method': 'GET',
        'description': 'Detalles de una liga específica',
        'response_type': 'html',
        'params': ['id']
    },
    
    'community': {
        'url': '/community',
        'method': 'GET',
        'description': 'Información de la comunidad',
        'response_type': 'html'
    },
    
    # Notificaciones
    'notifications': {
        'url': '/notifications',
        'method': 'GET',
        'description': 'Notificaciones del usuario',
        'response_type': 'html'
    },
    
    'alerts': {
        'url': '/alerts',
        'method': 'GET',
        'description': 'Alertas de mercado',
        'response_type': 'html'
    },
    
    # Configuración
    'settings': {
        'url': '/settings',
        'method': 'GET',
        'description': 'Configuración del usuario',
        'response_type': 'html'
    },
    
    'profile': {
        'url': '/profile',
        'method': 'GET',
        'description': 'Perfil del usuario',
        'response_type': 'html'
    },
    
    # Jornadas y Partidos
    'fixtures': {
        'url': '/fixtures',
        'method': 'GET',
        'description': 'Calendario de partidos',
        'response_type': 'html'
    },
    
    'gameweek': {
        'url': '/gameweek/{id}',
        'method': 'GET',
        'description': 'Detalles de una jornada específica',
        'response_type': 'html',
        'params': ['id']
    },
    
    # Equipos de Fútbol
    'teams': {
        'url': '/teams',
        'method': 'GET',
        'description': 'Lista de equipos de fútbol',
        'response_type': 'html'
    },
    
    'team_squad': {
        'url': '/team/{id}/squad',
        'method': 'GET',
        'description': 'Plantilla de un equipo de fútbol',
        'response_type': 'html',
        'params': ['id']
    },
    
    # API Endpoints adicionales
    'ajax_teams': {
        'url': '/ajax/sw/teams',
        'method': 'POST',
        'description': 'API de equipos de fútbol',
        'response_type': 'json',
        'params': ['id', 'slug', 'comments']
    },
    
    'ajax_community_check': {
        'url': '/ajax/community-check',
        'method': 'POST',
        'description': 'Verificar novedades en la comunidad',
        'response_type': 'json'
    },
    
    'ajax_feed': {
        'url': '/ajax/feed',
        'method': 'POST',
        'description': 'API del feed',
        'response_type': 'json'
    },
    
    'ajax_market': {
        'url': '/ajax/market',
        'method': 'POST',
        'description': 'API del mercado',
        'response_type': 'json'
    },
    
    'ajax_transfers': {
        'url': '/ajax/transfers',
        'method': 'POST',
        'description': 'API de transferencias',
        'response_type': 'json'
    },
    
    'ajax_stats': {
        'url': '/ajax/stats',
        'method': 'POST',
        'description': 'API de estadísticas',
        'response_type': 'json'
    }
}

# Endpoints prioritarios para implementar
PRIORITY_ENDPOINTS = [
    'ajax_teams',           # Detalles de equipos de fútbol
    'ajax_community_check', # Verificar novedades
    'ajax_feed',           # Feed en JSON
    'ajax_market',         # Mercado en JSON
    'transfers',           # Historial de transferencias
    'stats',               # Estadísticas
    'leagues',             # Ligas
    'fixtures',            # Calendario
    'notifications'        # Notificaciones
]

def get_all_endpoints():
    """Retorna todos los endpoints disponibles."""
    return {**IMPLEMENTED_ENDPOINTS, **ADDITIONAL_ENDPOINTS}

def get_priority_endpoints():
    """Retorna los endpoints prioritarios para implementar."""
    all_endpoints = get_all_endpoints()
    return {name: all_endpoints[name] for name in PRIORITY_ENDPOINTS if name in all_endpoints}

def get_endpoint_info(endpoint_name):
    """Retorna información de un endpoint específico."""
    all_endpoints = get_all_endpoints()
    return all_endpoints.get(endpoint_name)
