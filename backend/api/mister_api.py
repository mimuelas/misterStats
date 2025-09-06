"""
Cliente API expandido para Mister Fantasy.
Incluye todos los endpoints identificados en el análisis del archivo .har.
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union
from backend.models.data_models import (
    PlayerSearchFilters, Balance, Player, UserDetails, 
    StandingsUser, MarketOptions, APIResponse
)
from backend.parsers.json_parsers import JSONParsers
from backend.parsers.html_parsers import HTMLParsers


class MisterAPI:
    """
    Cliente completo para interactuar con la API de Mister Fantasy.
    Incluye todos los endpoints identificados y parsers especializados.
    """
    
    def __init__(self):
        self.base_url = "https://mister.mundodeportivo.com"
        self.session = requests.Session()
        
        # Headers extraídos del análisis del .har
        self.session.headers.update({
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
        })
        
        # Cookies extraídas del análisis del .har
        self.session.cookies.update({
            'PHPSESSID': '1abd2bafbb07652f780d8527477e83e4',
            'token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiIxNzU1MDQxOTk1IiwidXNlcmlkIjoiMjE0ODgzMiIsImFsZyI6IkVTMjU2In0.etY2S42q6vx6HdUfEtf1sDcD4iVWt4O_KG85hltMjoQsxKbm7Taiik2OvYzb0isCkBBzC58GKbUn4Ya517mcbA',
            'refresh-token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiI0OTEwNzE1Mjk1IiwicmVmcmVzaCI6ImZjT1oxV3pqQmNXMVI5RHA0akVnMiIsImlkX3Rva2VuX2xpZmV0aW1lX2luX21pbiI6IjUiLCJhbGciOiJFUzI1NiJ9.nrsEDmi0TKd0gdhl-AYYIHHdX-dLf6_k-AgDQoJElE5hVtFqmI-VAkNjhqIKh5OQtoh-yRG5ztabpY76azDVTw',
        })
    
    def _request(self, method: str, endpoint: str, post_data: Optional[Dict] = None) -> Union[Dict, str, None]:
        """
        Método base para realizar peticiones a la API.
        Soporta tanto GET como POST con manejo de errores.
        """
        url = f"{self.base_url}{endpoint}"
        self.session.headers['referer'] = f"{self.base_url}/"
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, data=post_data)
            else:
                response = self.session.get(url)
            
            response.raise_for_status()
            
            # Intentar parsear como JSON primero
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición a {url}: {e}")
            return None
    
    # ==================== ENDPOINTS DE AUTENTICACIÓN Y BALANCE ====================
    
    def get_balance(self) -> Optional[Balance]:
        """
        Obtiene el balance de la cuenta.
        Returns: Balance object con current, future y max_debt
        """
        response = self._request("POST", "/ajax/balance")
        if response and isinstance(response, dict):
            return JSONParsers.parse_balance_response(response)
        return None
    
    # ==================== ENDPOINTS DE CLASIFICACIONES ====================
    
    def get_standings(self) -> Optional[str]:
        """
        Obtiene la clasificación de la liga.
        Returns: HTML content
        """
        return self._request("POST", "/standings")
    
    def get_standings_parsed(self) -> List[StandingsUser]:
        """
        Obtiene la clasificación parseada.
        Returns: Lista de StandingsUser objects
        """
        html = self.get_standings()
        if html:
            return HTMLParsers.parse_standings_response(html)
        return []
    
    # ==================== ENDPOINTS DE USUARIOS ====================
    
    def get_user_details(self, user_id: str, user_slug: str, comments: int = 0) -> Optional[UserDetails]:
        """
        Obtiene los detalles completos de un usuario.
        Args:
            user_id: ID del usuario
            user_slug: Slug del usuario
            comments: Número de comentarios a incluir (default: 0)
        Returns: UserDetails object
        """
        post_data = {
            'post': 'users',
            'id': user_id,
            'slug': user_slug,
            'comments': comments
        }
        response = self._request("POST", "/ajax/sw/users", post_data)
        if response and isinstance(response, dict):
            return JSONParsers.parse_user_details_response(response)
        return None
    
    # ==================== ENDPOINTS DE JUGADORES ====================
    
    def get_player_details(self, player_id: int, player_slug: str, comments: int = 0) -> Optional[Player]:
        """
        Obtiene los detalles completos de un jugador específico.
        Args:
            player_id: ID del jugador
            player_slug: Slug del jugador
            comments: Número de comentarios a incluir (default: 0)
        Returns: Player object
        """
        post_data = {
            'post': 'players',
            'id': player_id,
            'slug': player_slug,
            'comments': comments
        }
        response = self._request("POST", "/ajax/sw/players", post_data)
        if response and isinstance(response, dict):
            return JSONParsers.parse_player_details_response(response)
        return None
    
    def search_players(self, filters: PlayerSearchFilters) -> Optional[Dict[str, Any]]:
        """
        Busca jugadores con filtros específicos.
        Args:
            filters: PlayerSearchFilters object con todos los filtros
        Returns: PlayerSearchResult object
        """
        post_data = {
            'post': 'players',
            'filters[position]': filters.position,
            'filters[value]': filters.value,
            'filters[team]': filters.team,
            'filters[injured]': filters.injured,
            'filters[favs]': filters.favs,
            'filters[owner]': filters.owner,
            'filters[benched]': filters.benched,
            'filters[stealable]': filters.stealable,
            'offset': filters.offset,
            'order': filters.order,
            'name': filters.name,
            'parentElement': '#fg-content'
        }
        response = self._request("POST", "/ajax/sw/players", post_data)
        if response and isinstance(response, dict):
            return JSONParsers.parse_player_search_response(response)
        return None
    
    def search_players_simple(self, name: str = "", position: int = 0, team: int = 0) -> Optional[Dict[str, Any]]:
        """
        Búsqueda simple de jugadores.
        Args:
            name: Nombre del jugador a buscar
            position: Posición (0: Todas, 1: Portero, 2: Defensa, 3: Centrocampista, 4: Delantero)
            team: ID del equipo (0: Todos)
        Returns: PlayerSearchResult object
        """
        filters = PlayerSearchFilters(
            name=name,
            position=position,
            team=team
        )
        return self.search_players(filters)
    
    # ==================== ENDPOINTS DE MERCADO ====================
    
    def get_market(self) -> Optional[str]:
        """
        Obtiene la página del mercado.
        Returns: HTML content
        """
        return self._request("POST", "/market")
    
    def get_market_parsed(self) -> Optional[MarketOptions]:
        """
        Obtiene el mercado parseado.
        Returns: MarketOptions object
        """
        html = self.get_market()
        if html:
            return HTMLParsers.parse_market_response(html)
        return None
    
    # ==================== ENDPOINTS DE EQUIPO ====================
    
    def get_team(self) -> Optional[str]:
        """
        Obtiene la página del equipo del usuario.
        Returns: HTML content
        """
        return self._request("POST", "/team")
    
    def get_team_parsed(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el equipo parseado.
        Returns: Dict con información del equipo
        """
        html = self.get_team()
        if html:
            return HTMLParsers.parse_team_response(html)
        return None
    
    # ==================== ENDPOINTS DE BÚSQUEDA ====================
    
    def get_search(self) -> Optional[str]:
        """
        Obtiene la página de búsqueda.
        Returns: HTML content
        """
        return self._request("POST", "/search")
    
    def get_search_parsed(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la búsqueda parseada.
        Returns: Dict con opciones de búsqueda
        """
        html = self.get_search()
        if html:
            return HTMLParsers.parse_search_response(html)
        return None
    
    # ==================== ENDPOINTS DE FEED ====================
    
    def get_feed(self) -> Optional[str]:
        """
        Obtiene el feed de noticias y eventos.
        Returns: HTML content
        """
        return self._request("POST", "/feed")
    
    def get_feed_parsed(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el feed parseado.
        Returns: Dict con posts y noticias
        """
        html = self.get_feed()
        if html:
            return HTMLParsers.parse_feed_response(html)
        return None
    
    # ==================== ENDPOINTS ADICIONALES ====================
    
    def get_team_details(self, team_id: int, team_slug: str, comments: int = 0) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un equipo de fútbol específico.
        Args:
            team_id: ID del equipo
            team_slug: Slug del equipo
            comments: Número de comentarios a incluir
        Returns: Dict con detalles del equipo
        """
        post_data = {
            'post': 'teams',
            'id': team_id,
            'slug': team_slug,
            'comments': comments
        }
        return self._request("POST", "/ajax/sw/teams", post_data)
    
    def community_check(self) -> Optional[Dict[str, Any]]:
        """
        Verifica si hay novedades en la comunidad.
        Returns: Dict con información de novedades
        """
        return self._request("POST", "/ajax/community-check")
    
    def get_transfers(self) -> Optional[str]:
        """
        Obtiene el historial de transferencias.
        Returns: HTML content
        """
        return self._request("GET", "/transfers")
    
    def get_stats(self) -> Optional[str]:
        """
        Obtiene estadísticas generales.
        Returns: HTML content
        """
        return self._request("GET", "/stats")
    
    def get_leagues(self) -> Optional[str]:
        """
        Obtiene la lista de ligas.
        Returns: HTML content
        """
        return self._request("GET", "/leagues")
    
    def get_league_details(self, league_id: int) -> Optional[str]:
        """
        Obtiene detalles de una liga específica.
        Args:
            league_id: ID de la liga
        Returns: HTML content
        """
        return self._request("GET", f"/league/{league_id}")
    
    def get_fixtures(self) -> Optional[str]:
        """
        Obtiene el calendario de partidos.
        Returns: HTML content
        """
        return self._request("GET", "/fixtures")
    
    def get_gameweek_details(self, gameweek_id: int) -> Optional[str]:
        """
        Obtiene detalles de una jornada específica.
        Args:
            gameweek_id: ID de la jornada
        Returns: HTML content
        """
        return self._request("GET", f"/gameweek/{gameweek_id}")
    
    def get_notifications(self) -> Optional[str]:
        """
        Obtiene las notificaciones del usuario.
        Returns: HTML content
        """
        return self._request("GET", "/notifications")
    
    def get_teams(self) -> Optional[str]:
        """
        Obtiene la lista de equipos de fútbol.
        Returns: HTML content
        """
        return self._request("GET", "/teams")
    
    def get_team_squad(self, team_id: int) -> Optional[str]:
        """
        Obtiene la plantilla de un equipo de fútbol.
        Args:
            team_id: ID del equipo
        Returns: HTML content
        """
        return self._request("GET", f"/team/{team_id}/squad")
    
    def get_auctions(self) -> Optional[str]:
        """
        Obtiene las subastas activas.
        Returns: HTML content
        """
        return self._request("GET", "/auctions")
    
    def get_bids(self) -> Optional[str]:
        """
        Obtiene las pujas del usuario.
        Returns: HTML content
        """
        return self._request("GET", "/bids")
    
    def get_leaderboard(self) -> Optional[str]:
        """
        Obtiene el ranking de jugadores.
        Returns: HTML content
        """
        return self._request("GET", "/leaderboard")
    
    def get_analytics(self) -> Optional[str]:
        """
        Obtiene análisis avanzados.
        Returns: HTML content
        """
        return self._request("GET", "/analytics")
    
    def get_settings(self) -> Optional[str]:
        """
        Obtiene la configuración del usuario.
        Returns: HTML content
        """
        return self._request("GET", "/settings")
    
    def get_profile(self) -> Optional[str]:
        """
        Obtiene el perfil del usuario.
        Returns: HTML content
        """
        return self._request("GET", "/profile")
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def get_league_standings(self) -> List[StandingsUser]:
        """
        Método de conveniencia para obtener la clasificación de la liga.
        Returns: Lista de usuarios en la clasificación
        """
        return self.get_standings_parsed()
    
    def get_top_players(self, limit: int = 10) -> List[Player]:
        """
        Obtiene los mejores jugadores por puntos.
        Args:
            limit: Número máximo de jugadores a retornar
        Returns: Lista de jugadores ordenados por puntos
        """
        filters = PlayerSearchFilters(order=0)  # Ordenar por puntos
        result = self.search_players(filters)
        if result and hasattr(result, 'players'):
            return result.players[:limit]
        return []
    
    def get_players_by_team(self, team_id: int) -> List[Player]:
        """
        Obtiene todos los jugadores de un equipo específico.
        Args:
            team_id: ID del equipo
        Returns: Lista de jugadores del equipo
        """
        filters = PlayerSearchFilters(team=team_id)
        result = self.search_players(filters)
        if result and hasattr(result, 'players'):
            return result.players
        return []
    
    def get_players_by_position(self, position: int) -> List[Player]:
        """
        Obtiene jugadores por posición.
        Args:
            position: Posición (1: Portero, 2: Defensa, 3: Centrocampista, 4: Delantero)
        Returns: Lista de jugadores de la posición
        """
        filters = PlayerSearchFilters(position=position)
        result = self.search_players(filters)
        if result and hasattr(result, 'players'):
            return result.players
        return []
    
    def get_user_team_value(self, user_id: str, user_slug: str) -> Optional[int]:
        """
        Obtiene el valor del equipo de un usuario específico.
        Args:
            user_id: ID del usuario
            user_slug: Slug del usuario
        Returns: Valor total del equipo o None
        """
        user_details = self.get_user_details(user_id, user_slug)
        if user_details:
            return user_details.value
        return None
    
    def get_team_formation(self, user_id: str, user_slug: str) -> Optional[str]:
        """
        Obtiene la formación del equipo de un usuario.
        Args:
            user_id: ID del usuario
            user_slug: Slug del usuario
        Returns: Formación del equipo o None
        """
        user_details = self.get_user_details(user_id, user_slug)
        if user_details and user_details.gameweeks:
            # Obtener la formación de la última jornada
            latest_gameweek = max(user_details.gameweeks.values(), key=lambda x: x.gameweek)
            return latest_gameweek.formation
        return None
