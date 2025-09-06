"""
Modelos de datos estructurados para Mister Fantasy API.
Basados en el análisis exhaustivo del archivo .har.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Team:
    """Modelo para equipos de fútbol."""
    id: int
    name: str
    logo_url: Optional[str] = None


@dataclass
class UserAvatar:
    """Modelo para avatar de usuario."""
    color: Optional[int] = None
    initials: Optional[str] = None
    pic: Optional[str] = None


@dataclass
class User:
    """Modelo para usuarios de Mister Fantasy."""
    id: int
    name: str
    id_community: Optional[int] = None
    avatar: Optional[UserAvatar] = None


@dataclass
class Transfer:
    """Modelo para transferencias de jugadores."""
    date: str
    origin: str  # "normal", "auction", etc.
    price: int


@dataclass
class Clause:
    """Modelo para cláusulas de jugadores."""
    floor: float
    multiplier: float
    default: int
    shield: int
    tier: int
    shield2WeeksSku: Optional[str] = None
    shield1MonthSku: Optional[str] = None


@dataclass
class Player:
    """Modelo principal para jugadores."""
    id: int
    name: str
    position: int  # 1: Portero, 2: Defensa, 3: Centrocampista, 4: Delantero
    points: int
    avg: float
    status: Optional[str]
    id_competition: int
    injury: List[str]
    photo_url: str
    is_favorite: int
    value: int
    previous_value: int
    team: Team
    owner: Optional[User] = None
    transfer: Optional[Transfer] = None
    clause: Optional[Clause] = None
    video_frame: Optional[str] = None
    streak: Optional[List[int]] = None
    streak_sum: Optional[int] = None
    id_uc: Optional[int] = None
    uc_name: Optional[str] = None
    shield: Optional[int] = None
    fav: Optional[int] = None
    id_market: Optional[int] = None
    is_mine: Optional[int] = None
    team_logo_url: Optional[str] = None
    clauses_rank: Optional[int] = None
    match_info: Optional[Dict[str, Any]] = None


@dataclass
class SeasonStats:
    """Modelo para estadísticas de temporada."""
    rank: int
    points: int
    avg: float


@dataclass
class Gameweek:
    """Modelo para jornadas."""
    id_gameweek: int
    gameweek: int
    type: str  # "regular", "special", etc.
    status: str  # "closed", "open", "partially-closed"
    points: int
    rank: int
    negative: int
    formation: str


@dataclass
class PlayerInLineup:
    """Modelo para jugadores en alineación."""
    id: int
    name: str
    points: str  # Puede ser "?" si no se han calculado
    slot: int
    position: int
    id_team: int
    status: Optional[str]
    ts_pic: Optional[int] = None


@dataclass
class Lineup:
    """Modelo para alineación de equipo."""
    positions: Dict[str, Dict[str, PlayerInLineup]]  # positions[position][slot] = player


@dataclass
class UserDetails:
    """Modelo completo para detalles de usuario."""
    id: int
    user: User
    season: SeasonStats
    gameweeks: Dict[str, Gameweek]
    lineup: Lineup
    bench: Dict[str, PlayerInLineup]
    team_now: List[Player]
    balance: Optional[int] = None
    value: Optional[int] = None


@dataclass
class Balance:
    """Modelo para balance de cuenta."""
    current: int
    future: int
    max_debt: int


@dataclass
class PlayerSearchFilters:
    """Modelo para filtros de búsqueda de jugadores."""
    position: int = 0  # 0: Todas, 1: Portero, 2: Defensa, 3: Centrocampista, 4: Delantero
    value: int = 0  # 0: Todas, 1: <1M, 2: 1-5M, etc.
    team: int = 0  # 0: Todos, ID específico del equipo
    injured: int = 0  # 0: Todos, 1: Solo lesionados
    favs: int = 0  # 0: Todos, 1: Solo favoritos
    owner: int = 0  # 0: Todos, 1: Solo míos
    benched: int = 0  # 0: Todos, 1: Solo en banquillo
    stealable: int = 0  # 0: Todos, 1: Solo robables
    offset: int = 0
    order: int = 0  # 0: Puntos, 1: Media, 2: Racha, 3: Valor, 4: Cláusula
    name: str = ""


@dataclass
class PlayerSearchResult:
    """Modelo para resultados de búsqueda de jugadores."""
    id: bool
    gameweek_is_active: bool
    players: List[Player]
    teams: List[Team]


@dataclass
class StandingsUser:
    """Modelo para usuarios en clasificación."""
    position: int
    name: str
    id: str
    slug: str
    avatar_url: Optional[str]
    points: int
    points_diff: Optional[str]
    num_players: Optional[int]
    team_value: Optional[int]


@dataclass
class MarketOptions:
    """Modelo para opciones del mercado."""
    credits: int
    show_bids: bool
    filters: Dict[str, Any]


@dataclass
class APIResponse:
    """Modelo genérico para respuestas de la API."""
    status: str
    data: Any
    error: Optional[str] = None
