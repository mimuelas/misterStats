"""
Parsers específicos para respuestas HTML de la API de Mister Fantasy.
"""

from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Any
from backend.models.data_models import StandingsUser, MarketOptions


class HTMLParsers:
    """Clase con parsers específicos para cada tipo de respuesta HTML."""
    
    @staticmethod
    def parse_standings_response(html_content: str) -> List[StandingsUser]:
        """
        Parsea la respuesta HTML del endpoint /standings.
        Basado en el parser existente pero mejorado.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        users = []
        
        general_standings_panel = soup.find('div', class_='panel-total')
        
        if not general_standings_panel:
            return []
        
        user_rows = general_standings_panel.find_all('li')
        
        for row in user_rows:
            user_link = row.find('a', class_='user')
            if not user_link:
                continue
            
            # Extraer posición
            position_div = user_link.find('div', class_='position')
            position = int(position_div.text.strip()) if position_div else None
            
            # Extraer nombre
            name_div = user_link.find('div', class_='name')
            name = name_div.text.strip() if name_div else ''
            
            # Extraer ID y slug del href
            href = user_link.get('href', '')
            user_id, user_slug = None, None
            if href:
                match = re.search(r'users/(\d+)/([\w-]+)', href)
                if match:
                    user_id = match.group(1)
                    user_slug = match.group(2)
            
            # Extraer avatar
            avatar_img = user_link.find('img')
            avatar_url = avatar_img['src'] if avatar_img else None
            
            # Extraer puntos
            points_div = user_link.find('div', class_='points')
            points = int(points_div.contents[0].strip()) if points_div and points_div.contents else None
            
            # Extraer diferencia de puntos
            diff_div = points_div.find('div', class_='diff') if points_div else None
            points_diff = diff_div.text.strip() if diff_div else None
            
            # Extraer información de jugadores y valor del equipo
            played_div = user_link.find('div', class_='played')
            num_players, team_value = None, None
            if played_div:
                played_text = played_div.text.strip()
                # Formato: "17 jugadores · € 51.921.000"
                parts = played_text.split('·')
                if len(parts) == 2:
                    players_part = parts[0]
                    value_part = parts[1]
                    num_players_match = re.search(r'(\d+)', players_part)
                    if num_players_match:
                        num_players = int(num_players_match.group(1))
                    team_value = HTMLParsers._parse_team_value(value_part)
            
            users.append(StandingsUser(
                position=position,
                name=name,
                id=user_id,
                slug=user_slug,
                avatar_url=avatar_url,
                points=points,
                points_diff=points_diff,
                num_players=num_players,
                team_value=team_value
            ))
        
        return users
    
    @staticmethod
    def parse_market_response(html_content: str) -> MarketOptions:
        """
        Parsea la respuesta HTML del endpoint /market.
        Extrae opciones de filtros y configuración del mercado.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extraer créditos disponibles
        credits_btn = soup.find('button', {'data-credits': True})
        credits = int(credits_btn['data-credits']) if credits_btn else 0
        
        # Extraer opciones de mostrar pujas
        show_bids_btn = soup.find('button', {'data-event': 'select_show_bids'})
        show_bids = show_bids_btn is not None
        
        # Extraer filtros disponibles
        filters = {}
        filter_buttons = soup.find_all('button', {'data-popup': 'market/filter'})
        for btn in filter_buttons:
            filter_name = btn.get('data-filter')
            if filter_name:
                filters[filter_name] = btn.text.strip()
        
        return MarketOptions(
            credits=credits,
            show_bids=show_bids,
            filters=filters
        )
    
    @staticmethod
    def parse_team_response(html_content: str) -> Dict[str, Any]:
        """
        Parsea la respuesta HTML del endpoint /team.
        Extrae información del equipo del usuario.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        team_info = {
            'gameweeks': [],
            'formation': None,
            'players': [],
            'stats': {}
        }
        
        # Extraer jornadas disponibles
        gameweek_links = soup.find_all('a', class_='nav__item')
        for link in gameweek_links:
            if 'gameweek' in link.get('href', ''):
                gameweek_text = link.find('div', class_='gameweek__name')
                if gameweek_text:
                    team_info['gameweeks'].append({
                        'name': gameweek_text.text.strip(),
                        'href': link.get('href', '')
                    })
        
        # Extraer formación actual
        formation_div = soup.find('div', class_='formation')
        if formation_div:
            team_info['formation'] = formation_div.text.strip()
        
        # Extraer jugadores de la alineación
        player_cards = soup.find_all('div', class_='player-card')
        for card in player_cards:
            player_info = {
                'name': '',
                'position': '',
                'points': 0,
                'value': 0
            }
            
            name_elem = card.find('div', class_='player-name')
            if name_elem:
                player_info['name'] = name_elem.text.strip()
            
            position_elem = card.find('div', class_='player-position')
            if position_elem:
                player_info['position'] = position_elem.text.strip()
            
            points_elem = card.find('div', class_='player-points')
            if points_elem:
                try:
                    player_info['points'] = int(points_elem.text.strip())
                except ValueError:
                    player_info['points'] = 0
            
            value_elem = card.find('div', class_='player-value')
            if value_elem:
                player_info['value'] = HTMLParsers._parse_team_value(value_elem.text.strip())
            
            team_info['players'].append(player_info)
        
        return team_info
    
    @staticmethod
    def parse_search_response(html_content: str) -> Dict[str, Any]:
        """
        Parsea la respuesta HTML del endpoint /search.
        Extrae opciones de búsqueda y filtros disponibles.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        search_info = {
            'sort_options': [],
            'filters': {},
            'results': []
        }
        
        # Extraer opciones de ordenación
        sort_select = soup.find('select', class_='search-players-sort-hidden')
        if sort_select:
            for option in sort_select.find_all('option'):
                search_info['sort_options'].append({
                    'value': option.get('value', ''),
                    'text': option.text.strip()
                })
        
        # Extraer filtros disponibles
        filter_buttons = soup.find_all('button', {'data-filter': True})
        for btn in filter_buttons:
            filter_name = btn.get('data-filter')
            if filter_name:
                search_info['filters'][filter_name] = btn.text.strip()
        
        return search_info
    
    @staticmethod
    def parse_feed_response(html_content: str) -> Dict[str, Any]:
        """
        Parsea la respuesta HTML del endpoint /feed.
        Extrae noticias y eventos de la comunidad.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        feed_info = {
            'posts': [],
            'community_info': {},
            'notifications': []
        }
        
        # Extraer posts del feed
        post_elements = soup.find_all('div', class_='feed-post')
        for post in post_elements:
            post_info = {
                'content': '',
                'author': '',
                'timestamp': '',
                'type': 'post'
            }
            
            content_elem = post.find('div', class_='post-content')
            if content_elem:
                post_info['content'] = content_elem.text.strip()
            
            author_elem = post.find('div', class_='post-author')
            if author_elem:
                post_info['author'] = author_elem.text.strip()
            
            time_elem = post.find('div', class_='post-time')
            if time_elem:
                post_info['timestamp'] = time_elem.text.strip()
            
            feed_info['posts'].append(post_info)
        
        # Extraer información de la comunidad
        community_elem = soup.find('a', class_='name')
        if community_elem:
            feed_info['community_info']['name'] = community_elem.text.strip()
        
        return feed_info
    
    @staticmethod
    def _parse_team_value(value_str: str) -> int:
        """Limpia y convierte el valor del equipo a un entero."""
        if not value_str:
            return 0
        return int(value_str.replace('€', '').replace('.', '').replace(',', '').strip())
