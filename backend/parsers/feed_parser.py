"""
Parser específico para el feed JSON de Mister Fantasy.
Maneja la estructura JSON del endpoint /ajax/feed.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class FeedParser:
    """Parser para el feed JSON de Mister Fantasy."""
    
    @staticmethod
    def parse_feed_data(feed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea los datos del feed JSON.
        
        Args:
            feed_data: Datos JSON del feed
            
        Returns:
            Dict con datos estructurados del feed
        """
        if not feed_data or 'data' not in feed_data:
            return {}
        
        data = feed_data['data']
        parsed_items = []
        
        for item in data:
            parsed_item = FeedParser._parse_feed_item(item)
            if parsed_item:
                parsed_items.append(parsed_item)
        
        return {
            'items': parsed_items,
            'total_items': len(parsed_items),
            'offset': feed_data.get('offset', 0),
            'status': feed_data.get('status', ''),
            'parsed_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def _parse_feed_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parsea un elemento individual del feed."""
        if not item:
            return None
        
        parsed = {
            'id': item.get('id'),
            'category': item.get('category'),
            'date': item.get('date'),
            'created': item.get('created'),
            'competition_id': item.get('id_competition'),
            'community_id': item.get('id_community'),
            'data': item.get('data', {}),
            'sticky': item.get('sticky', 0),
            'updated': item.get('updated')
        }
        
        # Parsear según la categoría
        data = item.get('data', {})
        
        # Si data es una lista, tomar el primer elemento
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        elif not isinstance(data, dict):
            data = {}
        
        if item.get('category') == 'transfer':
            parsed['transfer_info'] = FeedParser._parse_transfer_data(data)
        elif item.get('category') == 'player_transfer':
            parsed['player_transfer_info'] = FeedParser._parse_player_transfer_data(data)
        elif item.get('category') == 'gameweek_end':
            parsed['gameweek_info'] = FeedParser._parse_gameweek_data(data)
        elif item.get('category') == 'post':
            parsed['post_info'] = FeedParser._parse_post_data(data)
        
        return parsed
    
    @staticmethod
    def _parse_transfer_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de transferencia entre usuarios."""
        return {
            'transfer_id': data.get('id_transfer'),
            'from_user': data.get('from'),
            'to_user': data.get('to'),
            'price': data.get('price'),
            'player_name': data.get('name'),
            'player_position': data.get('position'),
            'player_team': data.get('id_team'),
            'player_points': data.get('points'),
            'player_value': data.get('value'),
            'player_photo': data.get('photoUrl'),
            'avatar_from': data.get('avatar_from', {}),
            'avatar_to': data.get('avatar_to', {})
        }
    
    @staticmethod
    def _parse_player_transfer_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de transferencia de jugador entre equipos."""
        return {
            'player_id': data.get('id'),
            'player_name': data.get('name'),
            'position': data.get('position'),
            'team_from': data.get('from'),
            'team_to': data.get('to'),
            'team_from_id': data.get('id_team_from'),
            'team_to_id': data.get('id_team_to'),
            'value': data.get('value'),
            'prev_value': data.get('prev_value'),
            'photo_url': data.get('photoUrl'),
            'team_logo_from': data.get('teamLogoUrl'),
            'team_logo_to': data.get('toLogoUrl')
        }
    
    @staticmethod
    def _parse_gameweek_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de final de jornada."""
        return {
            'gameweek_id': data.get('id_gameweek'),
            'gameweek_number': data.get('gameweek'),
            'ranking': data.get('ranking', {}),
            'me': data.get('ranking', {}).get('me', {}) if data.get('ranking') else {}
        }
    
    @staticmethod
    def _parse_post_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de posts/mensajes."""
        return {
            'text': data.get('text'),
            'name': data.get('name'),
            'user_id': data.get('id_uc'),
            'segment_id': data.get('id_segment'),
            'expiration_date': data.get('expiration_date')
        }
