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
        elif item.get('category') == 'market_unified':
            parsed['market_info'] = FeedParser._parse_market_data(data)
        elif item.get('category') == 'change_name':
            parsed['change_name_info'] = FeedParser._parse_change_name_data(data)
        elif item.get('category') == 'blog':
            parsed['blog_info'] = FeedParser._parse_blog_data(data)
        elif item.get('category') == 'clauses_drops':
            parsed['clauses_drops_info'] = FeedParser._parse_clauses_drops_data(data)
        elif item.get('category') == 'porra':
            parsed['porra_info'] = FeedParser._parse_porra_data(data)
        
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
    
    @staticmethod
    def _parse_market_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de novedades del mercado."""
        market_items = data.get('market', [])
        parsed_market = []
        
        for item in market_items:
            player = item.get('player', {})
            parsed_market.append({
                'market_id': item.get('id'),
                'player_id': player.get('id'),
                'player_name': player.get('name'),
                'player_position': player.get('position'),
                'player_team': player.get('id_team'),
                'player_photo': player.get('avatar'),
                'player_value': player.get('value'),
                'player_points': player.get('points'),
                'expiration_date': item.get('expirationDate'),
                'date': item.get('date'),
                'community_id': item.get('communityId'),
                'bids': item.get('bids', []),
                'injuries': player.get('injuries', [])
            })
        
        return {
            'market_items': parsed_market,
            'total_items': len(parsed_market)
        }
    
    @staticmethod
    def _parse_change_name_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de cambios de nombre."""
        return {
            'user_id': data.get('id_uc'),
            'old_name': data.get('old_name'),
            'new_name': data.get('new_name'),
            'user_avatar': data.get('avatar', {}),
            'segment_id': data.get('id_segment')
        }
    
    @staticmethod
    def _parse_blog_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de entradas de blog."""
        return {
            'blog_id': data.get('id'),
            'title': data.get('title'),
            'content': data.get('content'),
            'author': data.get('author'),
            'author_id': data.get('id_author'),
            'author_avatar': data.get('avatar', {}),
            'image_url': data.get('imageUrl'),
            'excerpt': data.get('excerpt'),
            'published_date': data.get('published_date'),
            'segment_id': data.get('id_segment')
        }
    
    @staticmethod
    def _parse_clauses_drops_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de bajas por cláusulas."""
        return {
            'player_id': data.get('id'),
            'player_name': data.get('name'),
            'player_position': data.get('position'),
            'player_team': data.get('id_team'),
            'player_photo': data.get('photoUrl'),
            'player_value': data.get('value'),
            'player_points': data.get('points'),
            'clause_type': data.get('clause_type'),
            'clause_value': data.get('clause_value'),
            'team_name': data.get('team_name'),
            'team_logo': data.get('teamLogoUrl')
        }
    
    @staticmethod
    def _parse_porra_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos de apuestas/porras."""
        return {
            'porra_id': data.get('id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'creator': data.get('creator'),
            'creator_id': data.get('id_creator'),
            'creator_avatar': data.get('avatar', {}),
            'expiration_date': data.get('expiration_date'),
            'options': data.get('options', []),
            'participants': data.get('participants', []),
            'segment_id': data.get('id_segment'),
            'status': data.get('status')
        }
