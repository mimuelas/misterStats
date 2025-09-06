"""
Servicio de datos para Mister Fantasy API.
Maneja caché, persistencia y optimización de consultas.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from backend.api.mister_api import MisterAPI
from backend.models.data_models import (
    Player, UserDetails, StandingsUser, Balance, 
    PlayerSearchFilters, MarketOptions
)
from backend.parsers.feed_parser import FeedParser


class DataService:
    """
    Servicio principal para manejo de datos de Mister Fantasy.
    Incluye caché inteligente y persistencia local.
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.api = MisterAPI()
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_duration = {
            'balance': 300,  # 5 minutos
            'standings': 600,  # 10 minutos
            'user_details': 1800,  # 30 minutos
            'player_details': 3600,  # 1 hora
            'market': 1800,  # 30 minutos
            'team': 1800,  # 30 minutos
            'search': 300,  # 5 minutos
            'feed': 600  # 10 minutos
        }
        
        # Crear directorio de caché si no existe
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, endpoint: str, **kwargs) -> str:
        """Genera una clave única para el caché."""
        key_parts = [endpoint]
        for k, v in sorted(kwargs.items()):
            # Limitar la longitud de los valores para evitar nombres de archivo muy largos
            value_str = str(v)[:20] if len(str(v)) > 20 else str(v)
            # Reemplazar caracteres problemáticos para Windows
            value_str = value_str.replace(':', '_').replace('\\', '_').replace('/', '_')
            key_parts.append(f"{k}_{value_str}")
        
        # Limitar la longitud total del nombre del archivo
        cache_key = "_".join(key_parts)
        if len(cache_key) > 200:
            # Usar hash para nombres muy largos
            import hashlib
            hash_key = hashlib.md5(cache_key.encode()).hexdigest()[:16]
            cache_key = f"{endpoint}_{hash_key}"
        
        return cache_key
    
    def _is_cache_valid(self, cache_key: str, cache_type: str) -> bool:
        """Verifica si el caché es válido."""
        if cache_key in self.memory_cache:
            cache_time = self.memory_cache[cache_key].get('timestamp', 0)
            duration = self.cache_duration.get(cache_type, 300)
            return time.time() - cache_time < duration
        return False
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Obtiene datos del caché en memoria."""
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]['data']
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any, cache_type: str):
        """Guarda datos en el caché en memoria."""
        self.memory_cache[cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'type': cache_type
        }
    
    def _get_from_file_cache(self, cache_key: str) -> Optional[Any]:
        """Obtiene datos del caché en archivo."""
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Verificar si el caché es válido
                    cache_time = cache_data.get('timestamp', 0)
                    cache_type = cache_data.get('type', 'default')
                    duration = self.cache_duration.get(cache_type, 300)
                    if time.time() - cache_time < duration:
                        return cache_data.get('data')
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def _save_to_file_cache(self, cache_key: str, data: Any, cache_type: str):
        """Guarda datos en el caché en archivo."""
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'type': cache_type
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando caché en archivo: {e}")
    
    def _get_cached_data(self, cache_key: str, cache_type: str) -> Optional[Any]:
        """Obtiene datos del caché (memoria o archivo)."""
        # Intentar primero el caché en memoria
        if self._is_cache_valid(cache_key, cache_type):
            return self._get_from_cache(cache_key)
        
        # Intentar el caché en archivo
        data = self._get_from_file_cache(cache_key)
        if data:
            # Guardar en caché en memoria para acceso rápido
            self._save_to_cache(cache_key, data, cache_type)
            return data
        
        return None
    
    def _save_data(self, cache_key: str, data: Any, cache_type: str):
        """Guarda datos en ambos cachés."""
        self._save_to_cache(cache_key, data, cache_type)
        self._save_to_file_cache(cache_key, data, cache_type)
    
    # ==================== MÉTODOS DE DATOS CON CACHÉ ====================
    
    def get_balance(self, use_cache: bool = True) -> Optional[Balance]:
        """Obtiene el balance con caché."""
        cache_key = self._get_cache_key('balance')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'balance')
            if cached_data:
                return Balance(**cached_data)
        
        balance = self.api.get_balance()
        if balance:
            balance_dict = {
                'current': balance.current,
                'future': balance.future,
                'max_debt': balance.max_debt
            }
            self._save_data(cache_key, balance_dict, 'balance')
            return balance
        
        return None
    
    def get_standings(self, use_cache: bool = True) -> Optional[str]:
        """Obtiene la clasificación HTML con caché."""
        cache_key = self._get_cache_key('standings')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'standings')
            if cached_data:
                return cached_data
        
        standings_html = self.api.get_standings()
        if standings_html:
            self._save_data(cache_key, standings_html, 'standings')
            return standings_html
        
        return None
    
    def get_standings_parsed(self, use_cache: bool = True) -> List[StandingsUser]:
        """Obtiene la clasificación parseada con caché."""
        cache_key = self._get_cache_key('standings_parsed')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'standings')
            if cached_data:
                return [StandingsUser(**user) for user in cached_data]
        
        standings = self.api.get_standings_parsed()
        if standings:
            standings_dict = [
                {
                    'position': user.position,
                    'name': user.name,
                    'id': user.id,
                    'slug': user.slug,
                    'avatar_url': user.avatar_url,
                    'points': user.points,
                    'points_diff': user.points_diff,
                    'num_players': user.num_players,
                    'team_value': user.team_value
                }
                for user in standings
            ]
            self._save_data(cache_key, standings_dict, 'standings')
            return standings
        
        return []
    
    def get_user_details(self, user_id: str, user_slug: str, use_cache: bool = True) -> Optional[UserDetails]:
        """Obtiene detalles de usuario con caché."""
        cache_key = self._get_cache_key('user_details', user_id=user_id, user_slug=user_slug)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'user_details')
            if cached_data:
                return UserDetails(**cached_data)
        
        user_details = self.api.get_user_details(user_id, user_slug)
        if user_details:
            # Convertir a dict para serialización
            try:
                user_dict = self._user_details_to_dict(user_details)
                self._save_data(cache_key, user_dict, 'user_details')
            except Exception as e:
                print(f"Error serializando user_details: {e}")
            return user_details
        
        return None
    
    def get_player_details(self, player_id: int, player_slug: str, use_cache: bool = True) -> Optional[Player]:
        """Obtiene detalles de jugador con caché."""
        cache_key = self._get_cache_key('player_details', player_id=player_id, player_slug=player_slug)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'player_details')
            if cached_data:
                return Player(**cached_data)
        
        player = self.api.get_player_details(player_id, player_slug)
        if player:
            player_dict = self._player_to_dict(player)
            self._save_data(cache_key, player_dict, 'player_details')
            return player
        
        return None
    
    def search_players(self, filters: PlayerSearchFilters, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Busca jugadores con caché."""
        cache_key = self._get_cache_key('search_players', **filters.__dict__)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'search')
            if cached_data:
                return cached_data
        
        result = self.api.search_players(filters)
        if result:
            result_dict = {
                'id': result.id,
                'gameweek_is_active': result.gameweek_is_active,
                'players': [self._player_to_dict(p) for p in result.players],
                'teams': [{'id': t.id, 'name': t.name, 'logo_url': t.logo_url} for t in result.teams]
            }
            self._save_data(cache_key, result_dict, 'search')
            return result_dict
        
        return None
    
    def get_market(self, use_cache: bool = True) -> Optional[str]:
        """Obtiene el mercado HTML con caché."""
        cache_key = self._get_cache_key('market')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'market')
            if cached_data:
                return cached_data
        
        market_html = self.api.get_market()
        if market_html:
            self._save_data(cache_key, market_html, 'market')
            return market_html
        
        return None
    
    def get_feed(self, offset: int = 0, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Obtiene el feed de noticias con caché."""
        cache_key = self._get_cache_key('feed', offset=offset)
        
        if use_cache and offset == 0:  # Solo cachear la primera página
            cached_data = self._get_cached_data(cache_key, 'feed')
            if cached_data:
                return cached_data
        
        feed = self.api.get_feed(offset)
        if feed and offset == 0:  # Solo cachear la primera página
            self._save_data(cache_key, feed, 'feed')
        return feed
        
        return None
    
    def get_team(self, use_cache: bool = True) -> Optional[str]:
        """Obtiene el equipo HTML con caché."""
        cache_key = self._get_cache_key('team')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'team')
            if cached_data:
                return cached_data
        
        team_html = self.api.get_team()
        if team_html:
            self._save_data(cache_key, team_html, 'team')
            return team_html
        
        return None
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def get_top_players(self, limit: int = 10, use_cache: bool = True) -> List[Player]:
        """Obtiene los mejores jugadores con caché."""
        cache_key = self._get_cache_key('top_players', limit=limit)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'search')
            if cached_data:
                return [Player(**p) for p in cached_data]
        
        players = self.api.get_top_players(limit)
        if players:
            players_dict = [self._player_to_dict(p) for p in players]
            self._save_data(cache_key, players_dict, 'search')
            return players
        
        return []
    
    def get_players_by_team(self, team_id: int, use_cache: bool = True) -> List[Player]:
        """Obtiene jugadores por equipo con caché."""
        cache_key = self._get_cache_key('players_by_team', team_id=team_id)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'search')
            if cached_data:
                return [Player(**p) for p in cached_data]
        
        players = self.api.get_players_by_team(team_id)
        if players:
            players_dict = [self._player_to_dict(p) for p in players]
            self._save_data(cache_key, players_dict, 'search')
            return players
        
        return []
    
    def get_players_by_position(self, position: int, use_cache: bool = True) -> List[Player]:
        """Obtiene jugadores por posición con caché."""
        cache_key = self._get_cache_key('players_by_position', position=position)
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'search')
            if cached_data:
                return [Player(**p) for p in cached_data]
        
        players = self.api.get_players_by_position(position)
        if players:
            players_dict = [self._player_to_dict(p) for p in players]
            self._save_data(cache_key, players_dict, 'search')
            return players
        
        return []
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Limpia el caché."""
        if cache_type:
            # Limpiar solo un tipo específico
            keys_to_remove = [k for k, v in self.memory_cache.items() if v.get('type') == cache_type]
            for key in keys_to_remove:
                del self.memory_cache[key]
        else:
            # Limpiar todo el caché
            self.memory_cache.clear()
        
        # Limpiar archivos de caché
        if cache_type:
            pattern = f"*_{cache_type}_*.json"
        else:
            pattern = "*.json"
        
        import glob
        for file_path in glob.glob(os.path.join(self.cache_dir, pattern)):
            try:
                os.remove(file_path)
            except OSError:
                pass
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        memory_items = len(self.memory_cache)
        file_items = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        
        cache_types = {}
        for item in self.memory_cache.values():
            cache_type = item.get('type', 'unknown')
            cache_types[cache_type] = cache_types.get(cache_type, 0) + 1
        
        return {
            'memory_items': memory_items,
            'file_items': file_items,
            'cache_types': cache_types,
            'cache_dir': self.cache_dir
        }
    
    # ==================== MÉTODOS PRIVADOS DE SERIALIZACIÓN ====================
    
    def _player_to_dict(self, player: Player) -> Dict[str, Any]:
        """Convierte un objeto Player a dict para serialización."""
        return {
            'id': player.id,
            'name': player.name,
            'position': player.position,
            'points': player.points,
            'avg': player.avg,
            'status': player.status,
            'id_competition': player.id_competition,
            'injury': player.injury,
            'photo_url': player.photo_url,
            'is_favorite': player.is_favorite,
            'value': player.value,
            'previous_value': player.previous_value,
            'team': {
                'id': player.team.id,
                'name': player.team.name,
                'logo_url': player.team.logo_url
            },
            'owner': {
                'id': player.owner.id,
                'name': player.owner.name,
                'id_community': player.owner.id_community,
                'avatar': {
                    'color': player.owner.avatar.color if player.owner.avatar else None,
                    'initials': player.owner.avatar.initials if player.owner.avatar else None,
                    'pic': player.owner.avatar.pic if player.owner.avatar else None
                } if player.owner and player.owner.avatar else None
            } if player.owner else None,
            'transfer': {
                'date': player.transfer.date,
                'origin': player.transfer.origin,
                'price': player.transfer.price
            } if player.transfer else None,
            'clause': {
                'floor': player.clause.floor,
                'multiplier': player.clause.multiplier,
                'default': player.clause.default,
                'shield': player.clause.shield,
                'tier': player.clause.tier,
                'shield2WeeksSku': player.clause.shield2WeeksSku,
                'shield1MonthSku': player.clause.shield1MonthSku
            } if player.clause else None,
            'video_frame': player.video_frame,
            'streak': player.streak,
            'streak_sum': player.streak_sum,
            'id_uc': player.id_uc,
            'uc_name': player.uc_name,
            'shield': player.shield,
            'fav': player.fav,
            'id_market': player.id_market,
            'is_mine': player.is_mine,
            'team_logo_url': player.team_logo_url,
            'clauses_rank': player.clauses_rank,
            'match_info': player.match_info
        }
    
    def _user_details_to_dict(self, user_details: UserDetails) -> Dict[str, Any]:
        """Convierte un objeto UserDetails a dict para serialización."""
        return {
            'id': user_details.id,
            'user': {
                'id': user_details.user.id,
                'name': user_details.user.name,
                'id_community': user_details.user.id_community,
                'avatar': {
                    'color': user_details.user.avatar.color if user_details.user.avatar else None,
                    'initials': user_details.user.avatar.initials if user_details.user.avatar else None,
                    'pic': user_details.user.avatar.pic if user_details.user.avatar else None
                } if user_details.user.avatar else None
            },
            'season': {
                'rank': user_details.season.rank,
                'points': user_details.season.points,
                'avg': user_details.season.avg
            },
            'gameweeks': {
                gw_id: {
                    'id_gameweek': gw.id_gameweek,
                    'gameweek': gw.gameweek,
                    'type': gw.type,
                    'status': gw.status,
                    'points': gw.points,
                    'rank': gw.rank,
                    'negative': gw.negative,
                    'formation': gw.formation
                }
                for gw_id, gw in user_details.gameweeks.items()
            },
            'lineup': {
                'positions': {
                    pos_id: {
                        slot_id: {
                            'id': player.id,
                            'name': player.name,
                            'points': player.points,
                            'slot': player.slot,
                            'position': player.position,
                            'id_team': player.id_team,
                            'status': player.status,
                            'ts_pic': player.ts_pic
                        }
                        for slot_id, player in pos_players.items()
                    }
                    for pos_id, pos_players in user_details.lineup.positions.items()
                }
            },
            'bench': {
                bench_id: {
                    'id': player.id,
                    'name': player.name,
                    'points': player.points,
                    'slot': player.slot,
                    'position': player.position,
                    'id_team': player.id_team,
                    'status': player.status,
                    'ts_pic': player.ts_pic
                }
                for bench_id, player in user_details.bench.items()
            },
            'team_now': [self._player_to_dict(p) for p in user_details.team_now],
            'balance': user_details.balance,
            'value': user_details.value
        }
    
    def get_market_parsed(self, use_cache: bool = True) -> Optional[MarketOptions]:
        """Obtiene el mercado parseado con caché."""
        cache_key = self._get_cache_key('market_parsed')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'market')
            if cached_data:
                return MarketOptions(**cached_data)
        
        market_data = self.api.get_market_parsed()
        if market_data:
            # Convertir a dict para serialización
            market_dict = {
                'credits': market_data.credits,
                'show_bids': market_data.show_bids,
                'filters': market_data.filters
            }
            self._save_data(cache_key, market_dict, 'market')
            return market_data
        
        return None
    
    def get_team_parsed(self, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Obtiene el equipo parseado con caché."""
        cache_key = self._get_cache_key('team_parsed')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'team')
            if cached_data:
                return cached_data
        
        team_data = self.api.get_team_parsed()
        if team_data:
            self._save_data(cache_key, team_data, 'team')
            return team_data
        
        return None
    
    def get_feed_parsed(self, offset: int = 0, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Obtiene el feed parseado con caché."""
        cache_key = self._get_cache_key('feed_parsed', offset=offset)
        
        if use_cache and offset == 0:  # Solo cachear la primera página
            cached_data = self._get_cached_data(cache_key, 'feed')
            if cached_data:
                return cached_data
        
        # El feed ahora devuelve JSON directamente
        feed_json = self.api.get_feed_parsed(offset)
        if feed_json:
            # Parsear los datos del feed
            parsed_feed = FeedParser.parse_feed_data({
                'data': feed_json.get('data', []),
                'status': feed_json.get('status', ''),
                'offset': offset
            })
            
            if offset == 0:  # Solo cachear la primera página
                self._save_data(cache_key, parsed_feed, 'feed')
            return parsed_feed
        
        return None
    
    def get_search_parsed(self, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Obtiene la búsqueda parseada con caché."""
        cache_key = self._get_cache_key('search_parsed')
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key, 'search')
            if cached_data:
                return cached_data
        
        search_data = self.api.get_search_parsed()
        if search_data:
            self._save_data(cache_key, search_data, 'search')
            return search_data
        
        return None
