import streamlit as st
import pandas as pd
from streamlit_card import card
from backend.services.data_service import DataService
from backend.models.data_models import PlayerSearchFilters

# --- Configuración de la Página y Constantes ---
st.set_page_config(page_title="Mister Stats Dashboard", layout="wide")

POSITION_MAP = {
    1: "Portero",
    2: "Defensa",
    3: "Centrocampista",
    4: "Delantero"
}

# --- Inicialización del Servicio de Datos ---
@st.cache_resource
def get_data_service():
    """Inicializa el servicio de datos con caché."""
    return DataService()

# --- Funciones de Carga de Datos ---
@st.cache_data
def load_standings_data():
    """Obtiene y parsea los datos de la clasificación."""
    data_service = get_data_service()
    return data_service.get_standings()

@st.cache_data
def load_user_details(user_id, user_slug):
    """Obtiene los detalles de un usuario específico."""
    data_service = get_data_service()
    return data_service.get_user_details(user_id, user_slug)

# --- Funciones de Ayuda ---
def process_players(players_data, all_players_map=None):
    """
    Procesa una lista o diccionario de jugadores y devuelve un DataFrame.
    Compatible con los nuevos modelos de datos.
    """
    if not players_data:
        return pd.DataFrame()

    players_list = []
    
    # Si es un diccionario de posiciones (como en 'lineup')
    if isinstance(players_data, dict) and 'positions' in players_data:
        for position_group in players_data['positions'].values():
            for player in position_group.values():
                # Si tenemos el mapa, buscamos el valor del jugador ahí
                if all_players_map and hasattr(player, 'id') and player.id in all_players_map:
                    player.value = all_players_map[player.id].get('value', 0)
                players_list.append(player)
    # Si es un diccionario de jugadores (como en 'bench')
    elif isinstance(players_data, dict):
        players_list = list(players_data.values())
    # Si es una lista de objetos Player
    elif isinstance(players_data, list):
        players_list = players_data

    if not players_list:
        return pd.DataFrame()

    processed_list = []
    for player in players_list:
        # Manejar tanto objetos Player como diccionarios
        if hasattr(player, 'name'):
            # Es un objeto Player
            name = player.name
            position = POSITION_MAP.get(player.position, 'N/A')
            points = str(player.points) if player.points != '?' else '?'
            value = f"{player.value:,} €" if hasattr(player, 'value') and player.value else "N/A"
        else:
            # Es un diccionario
            name = player.get('name', 'N/A')
            position = POSITION_MAP.get(player.get('position'), 'N/A')
            points = str(player.get('points', 0))
            value = f"{player.get('value', player.get('price', 0)):,} €"
        
        processed_list.append({
            "Jugador": name,
            "Posición": position,
            "Puntos": points,
            "Valor": value
        })
    
    return pd.DataFrame(processed_list)

# --- Renderizado de Vistas ---
def render_standings_view(users_list):
    """Muestra la vista principal con la clasificación."""
    st.title("🏆 Clasificación de la Liga")
    
    for user in users_list:
        user_card = card(
            title=f"{user.position}. {user.name}",
            text=[
                f"Puntos: {user.points}",
                f"Valor Equipo: {user.team_value:,} €" if user.team_value else "Valor Equipo: N/A"
            ],
            image=user.avatar_url,
            key=f"user_card_{user.id}",
            styles={
                "card": {
                    "width": "100%", "margin": "10px", "border-radius": "10px",
                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, 0.5)"
                }
            }
        )
        if user_card:
            st.session_state.selected_user_id = user.id
            st.rerun()

def render_user_details_view(user):
    """Muestra la vista de detalle para un usuario seleccionado."""
    if st.button("⬅️ Volver a la clasificación"):
        st.session_state.selected_user_id = None
        st.rerun()

    user_details = load_user_details(user.id, user.slug)

    if user_details:
        # --- Cabecera del Usuario ---
        col1, col2 = st.columns([1, 4])
        with col1:
            if user_details.user.avatar and user_details.user.avatar.pic:
                st.image(user_details.user.avatar.pic, width=120)
        with col2:
            st.title(user_details.user.name or user.name)

        # --- Información General ---
        st.header("Información General")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(label="Balance", value=f"{user_details.balance or 0:,} €")
        col2.metric(label="Valor del Equipo", value=f"{user_details.value or 0:,} €")
        col3.metric(label="Puntos Totales", value=user_details.season.points)
        col4.metric(label="Ranking", value=f"#{user_details.season.rank}")
        col5.metric(label="Media Puntos", value=f"{user_details.season.avg:.2f}")

        # --- Rendimiento por Jornada ---
        st.header("Rendimiento por Jornada")
        if user_details.gameweeks:
            gameweeks_list = [
                {
                    "Jornada": gw.gameweek,
                    "Puntos": gw.points,
                    "Ranking": f"#{gw.rank}",
                    "Formación": gw.formation
                }
                for gw in user_details.gameweeks.values()
            ]
            gameweeks_df = pd.DataFrame(gameweeks_list)
            st.dataframe(gameweeks_df.sort_values(by="Jornada").set_index("Jornada"), use_container_width=True)
        else:
            st.info("No hay datos de rendimiento por jornada disponibles.")

        # --- Alineación y Banquillo ---
        st.header("Alineación")
        lineup_df = process_players(user_details.lineup.positions)
        if not lineup_df.empty:
            st.dataframe(lineup_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de alineación disponibles.")
            
        st.header("Banquillo")
        bench_df = process_players(user_details.bench)
        if not bench_df.empty:
            st.dataframe(bench_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos del banquillo disponibles.")
            
    else:
        st.error("No se pudieron cargar los detalles para este usuario.")

# --- Aplicación Principal ---
def main():
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None

    users_data = load_standings_data()

    if not users_data:
        st.error("No se pudieron cargar los datos de la clasificación.")
        return

    if st.session_state.selected_user_id:
        selected_user = next((user for user in users_data if user.id == st.session_state.selected_user_id), None)
        if selected_user:
            render_user_details_view(selected_user)
        else:
            st.session_state.selected_user_id = None
            render_standings_view(users_data)
    else:
        render_standings_view(users_data)

if __name__ == "__main__":
    main()
