"""
Parsers específicos para respuestas JSON de la API de Mister Fantasy.
"""

import json
from typing import Dict, List, Optional, Any
from backend.models.data_models import (
    Player, Team, User, UserAvatar, Transfer, Clause, 
    UserDetails, SeasonStats, Gameweek, PlayerInLineup, 
    Lineup, Balance, PlayerSearchResult, APIResponse
)


class JSONParsers:
    """Clase con parsers específicos para cada tipo de respuesta JSON."""
    
    @staticmethod
    def parse_balance_response(response_data: Dict[str, Any]) -> Balance:
        """Parsea la respuesta del endpoint /ajax/balance."""
        data = response_data.get('data', {})
        return Balance(
            current=data.get('current', 0),
            future=data.get('future', 0),
            max_debt=data.get('maxDebt', 0)
        )
    
    @staticmethod
    def parse_player_details_response(response_data: Dict[str, Any]) -> Player:
        """Parsea la respuesta del endpoint /ajax/sw/players para detalles de jugador."""
        player_data = response_data.get('data', {}).get('player', {})
        
        # Parsear equipo
        team_data = player_data.get('team', {})
        team = Team(
            id=team_data.get('id', 0),
            name=team_data.get('name', ''),
            logo_url=team_data.get('logoUrl', '')
        )
        
        # Parsear propietario si existe
        owner_data = player_data.get('owner', {})
        owner = None
        if owner_data:
            avatar_data = owner_data.get('avatar', {})
            avatar = UserAvatar(
                color=avatar_data.get('color'),
                initials=avatar_data.get('initials'),
                pic=avatar_data.get('pic')
            )
            owner = User(
                id=owner_data.get('id', 0),
                name=owner_data.get('name', ''),
                id_community=owner_data.get('id_community'),
                avatar=avatar
            )
        
        # Parsear transferencia si existe
        transfer_data = player_data.get('transfer', {})
        transfer = None
        if transfer_data:
            transfer = Transfer(
                date=transfer_data.get('date', ''),
                origin=transfer_data.get('origin', ''),
                price=transfer_data.get('price', 0)
            )
        
        # Parsear cláusula si existe
        clause_data = player_data.get('clause', {})
        clause = None
        if clause_data:
            clause = Clause(
                floor=clause_data.get('floor', 0),
                multiplier=clause_data.get('multiplier', 0),
                default=clause_data.get('default', 0),
                shield=clause_data.get('shield', 0),
                tier=clause_data.get('tier', 0),
                shield2WeeksSku=clause_data.get('shield2WeeksSku'),
                shield1MonthSku=clause_data.get('shield1MonthSku')
            )
        
        return Player(
            id=player_data.get('id', 0),
            name=player_data.get('name', ''),
            position=player_data.get('position', 0),
            points=player_data.get('points', 0),
            avg=player_data.get('avg', 0),
            status=player_data.get('status'),
            id_competition=player_data.get('id_competition', 0),
            injury=player_data.get('injury', []),
            photo_url=player_data.get('photoUrl', ''),
            is_favorite=player_data.get('isFavorite', 0),
            value=player_data.get('value', 0),
            previous_value=player_data.get('previousValue', 0),
            team=team,
            owner=owner,
            transfer=transfer,
            clause=clause,
            video_frame=player_data.get('videoFrame')
        )
    
    @staticmethod
    def parse_player_search_response(response_data: Dict[str, Any]) -> PlayerSearchResult:
        """Parsea la respuesta del endpoint /ajax/sw/players para búsqueda de jugadores."""
        data = response_data.get('data', {})
        
        # Parsear jugadores
        players = []
        for player_data in data.get('players', []):
            team_data = player_data.get('team', {})
            team = Team(
                id=player_data.get('id_team', 0),
                name=team_data.get('name', ''),
                logo_url=player_data.get('teamLogoUrl', '')
            )
            
            # Parsear propietario si existe
            owner = None
            if player_data.get('id_uc'):
                owner = User(
                    id=player_data.get('id_uc', 0),
                    name=player_data.get('uc_name', '')
                )
            
            player = Player(
                id=player_data.get('id', 0),
                name=player_data.get('name', ''),
                position=player_data.get('position', 0),
                points=player_data.get('points', 0),
                avg=player_data.get('avg', 0),
                status=player_data.get('status'),
                id_competition=player_data.get('id_competition', 0),
                injury=player_data.get('injury', []),
                photo_url=player_data.get('photoUrl', ''),
                is_favorite=player_data.get('fav', 0),
                value=player_data.get('value', 0),
                previous_value=player_data.get('prev_value', 0),
                team=team,
                owner=owner,
                streak=player_data.get('streak', []),
                streak_sum=player_data.get('streak_sum'),
                shield=player_data.get('shield', 0),
                id_market=player_data.get('id_market'),
                is_mine=player_data.get('is_mine', 0),
                team_logo_url=player_data.get('teamLogoUrl', ''),
                clauses_rank=player_data.get('clausesRank'),
                match_info=player_data.get('match_info', {})
            )
            players.append(player)
        
        # Parsear equipos
        teams = []
        for team_data in data.get('teams', []):
            team = Team(
                id=team_data.get('id', 0),
                name=team_data.get('name', '')
            )
            teams.append(team)
        
        return PlayerSearchResult(
            id=data.get('id', False),
            gameweek_is_active=data.get('gameweekIsActive', False),
            players=players,
            teams=teams
        )
    
    @staticmethod
    def parse_user_details_response(response_data: Dict[str, Any]) -> UserDetails:
        """Parsea la respuesta del endpoint /ajax/sw/users para detalles de usuario."""
        data = response_data.get('data', {})
        
        # Parsear información del usuario
        user_data = data.get('user', {})
        avatar_data = user_data.get('avatar', {})
        
        # Manejar caso donde avatar es string en lugar de dict
        if isinstance(avatar_data, str):
            avatar = UserAvatar()
        else:
            avatar = UserAvatar(
                color=avatar_data.get('color'),
                initials=avatar_data.get('initials'),
                pic=avatar_data.get('pic')
            )
        user = User(
            id=data.get('id', 0),
            name=user_data.get('name', '') if isinstance(user_data, dict) and user_data.get('name') else 'Usuario',
            id_community=user_data.get('id_community', 0) if isinstance(user_data, dict) else 0,
            avatar=avatar
        )
        
        # Parsear estadísticas de temporada
        season_data = data.get('season', {})
        season = SeasonStats(
            rank=season_data.get('rank', 0),
            points=season_data.get('points', 0),
            avg=season_data.get('avg', 0)
        )
        
        # Parsear jornadas
        gameweeks = {}
        for gw_id, gw_data in data.get('gameweeks', {}).items():
            gameweek = Gameweek(
                id_gameweek=gw_data.get('id_gameweek', 0),
                gameweek=gw_data.get('gameweek', 0),
                type=gw_data.get('type', ''),
                status=gw_data.get('status', ''),
                points=gw_data.get('points', 0),
                rank=gw_data.get('rank', 0),
                negative=gw_data.get('negative', 0),
                formation=gw_data.get('formation', '')
            )
            gameweeks[gw_id] = gameweek
        
        # Parsear alineación
        lineup_data = data.get('lineup', {})
        positions = {}
        for pos_id, pos_data in lineup_data.get('positions', {}).items():
            position_players = {}
            for slot_id, player_data in pos_data.items():
                player = PlayerInLineup(
                    id=player_data.get('id', 0),
                    name=player_data.get('name', ''),
                    points=player_data.get('points', '0'),
                    slot=player_data.get('slot', 0),
                    position=player_data.get('position', 0),
                    id_team=player_data.get('id_team', 0),
                    status=player_data.get('status'),
                    ts_pic=player_data.get('ts_pic')
                )
                position_players[slot_id] = player
            positions[pos_id] = position_players
        
        lineup = Lineup(positions=positions)
        
        # Parsear banquillo
        bench = {}
        for bench_id, player_data in data.get('bench', {}).items():
            player = PlayerInLineup(
                id=player_data.get('id', 0),
                name=player_data.get('name', ''),
                points=player_data.get('points', '0'),
                slot=player_data.get('slot', 0),
                position=player_data.get('position', 0),
                id_team=player_data.get('id_team', 0),
                status=player_data.get('status'),
                ts_pic=player_data.get('ts_pic')
            )
            bench[bench_id] = player
        
        # Parsear lista completa de jugadores del equipo
        team_now = []
        for player_data in data.get('team_now', []):
            team_data = player_data.get('team', {})
            team = Team(
                id=team_data.get('id', 0),
                name=team_data.get('name', ''),
                logo_url=team_data.get('logoUrl', '')
            )
            
            player = Player(
                id=player_data.get('id', 0),
                name=player_data.get('name', ''),
                position=player_data.get('position', 0),
                points=player_data.get('points', 0),
                avg=player_data.get('avg', 0),
                status=player_data.get('status'),
                id_competition=player_data.get('id_competition', 0),
                injury=player_data.get('injury', []),
                photo_url=player_data.get('photoUrl', ''),
                is_favorite=player_data.get('isFavorite', 0),
                value=player_data.get('value', 0),
                previous_value=player_data.get('previousValue', 0),
                team=team
            )
            team_now.append(player)
        
        return UserDetails(
            id=data.get('id', 0),
            user=user,
            season=season,
            gameweeks=gameweeks,
            lineup=lineup,
            bench=bench,
            team_now=team_now,
            balance=data.get('balance'),
            value=data.get('value')
        )
    
    @staticmethod
    def parse_api_response(response_text: str) -> APIResponse:
        """Parsea una respuesta genérica de la API."""
        try:
            data = json.loads(response_text)
            return APIResponse(
                status=data.get('status', 'error'),
                data=data.get('data'),
                error=data.get('error')
            )
        except json.JSONDecodeError as e:
            return APIResponse(
                status='error',
                data=None,
                error=f"Error parsing JSON: {str(e)}"
            )
