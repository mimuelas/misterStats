import streamlit as st
import pandas as pd
from streamlit_card import card
from mister_fetch_players import MisterAPI
from mister_parser import parse_users_from_standings

# --- Configuración de la Página y Constantes ---
st.set_page_config(page_title="Mister Stats Dashboard", layout="wide")

POSITION_MAP = {
    1: "Portero",
    2: "Defensa",
    3: "Centrocampista",
    4: "Delantero"
}

# --- Funciones de Carga de Datos ---
@st.cache_data
def load_standings_data():
    """Obtiene y parsea los datos de la clasificación."""
    api = MisterAPI()
    html = api.get_standings()
    if html:
        return parse_users_from_standings(html)
    return []

@st.cache_data
def load_user_details(user_id, user_slug):
    """Obtiene los detalles de un usuario específico."""
    api = MisterAPI()
    return api.get_user_details(user_id, user_slug)

# --- Funciones de Ayuda ---
def process_players(players_data):
    """Procesa una lista o diccionario de jugadores y devuelve un DataFrame."""
    if not players_data:
        return pd.DataFrame()

    players_list = []
    
    # Si es un diccionario de posiciones (como en 'lineup')
    if isinstance(players_data, dict) and 'positions' in players_data:
        for position_group in players_data['positions'].values():
            for player in position_group.values():
                players_list.append(player)
    # Si es un diccionario de jugadores (como en 'bench')
    elif isinstance(players_data, dict):
        players_list = list(players_data.values())

    if not players_list:
        return pd.DataFrame()

    processed_list = [
        {
            "Jugador": f"{player.get('name', 'N/A')}",
            "Posición": POSITION_MAP.get(player.get('position'), 'N/A'),
            "Puntos": player.get('points', 0),
            "Valor": f"{player.get('value', player.get('price', 0)):,} €"
        }
        for player in players_list
    ]
    
    return pd.DataFrame(processed_list)

# --- Renderizado de Vistas ---
def render_standings_view(users_df):
    """Muestra la vista principal con la clasificación."""
    st.title("🏆 Clasificación de la Liga")
    
    for _, user in users_df.iterrows():
        user_card = card(
            title=f"{user.get('position', '')}. {user['name']}",
            text=[
                f"Puntos: {user.get('points', 'N/A')}",
                f"Valor Equipo: {user.get('team_value', 0):,} €"
            ],
            image=user.get('avatar_url'),
            key=f"user_card_{user['id']}",
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
            st.session_state.selected_user_id = user['id']
            st.rerun()

def render_user_details_view(user):
    """Muestra la vista de detalle para un usuario seleccionado."""
    if st.button("⬅️ Volver a la clasificación"):
        st.session_state.selected_user_id = None
        st.rerun()

    user_details = load_user_details(user['id'], user['slug'])

    if user_details and user_details.get('status') == 'ok':
        data = user_details.get('data', {})
        user_info = data.get('userInfo', {})
        
        # --- Cabecera del Usuario ---
        col1, col2 = st.columns([1, 4])
        with col1:
            avatar = user_info.get('avatar', {})
            if isinstance(avatar, dict) and 'pic' in avatar:
                st.image(avatar['pic'], width=120)
        with col2:
            st.title(user_info.get('name', user['name']))

        # --- Información General ---
        st.header("Información General")
        season_info = data.get('season', {})
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(label="Balance", value=f"{data.get('balance', 0):,} €")
        col2.metric(label="Valor del Equipo", value=f"{data.get('value', 0):,} €")
        col3.metric(label="Puntos Totales", value=season_info.get('points', 0))
        col4.metric(label="Ranking", value=f"#{season_info.get('rank', 'N/A')}")
        col5.metric(label="Media Puntos", value=f"{season_info.get('avg', 0):.2f}")

        # --- Rendimiento por Jornada ---
        st.header("Rendimiento por Jornada")
        gameweeks_data = data.get('gameweeks', {})
        if gameweeks_data:
            gameweeks_list = [
                {
                    "Jornada": gw.get('gameweek', 'N/A'),
                    "Puntos": gw.get('points', 0),
                    "Ranking": f"#{gw.get('rank', 'N/A')}",
                    "Formación": gw.get('formation', 'N/A')
                }
                for gw in gameweeks_data.values()
            ]
            gameweeks_df = pd.DataFrame(gameweeks_list)
            st.dataframe(gameweeks_df.sort_values(by="Jornada").set_index("Jornada"), use_container_width=True)
        else:
            st.info("No hay datos de rendimiento por jornada disponibles.")

        # --- Alineación y Banquillo ---
        st.header("Alineación")
        lineup_df = process_players(data.get('lineup', {}))
        if not lineup_df.empty:
            st.dataframe(lineup_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de alineación disponibles.")
            
        st.header("Banquillo")
        bench_df = process_players(data.get('bench', {}))
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

    users_df = pd.DataFrame(users_data)

    if st.session_state.selected_user_id:
        selected_user_series = users_df[users_df['id'] == st.session_state.selected_user_id]
        if not selected_user_series.empty:
            selected_user = selected_user_series.iloc[0]
            render_user_details_view(selected_user)
        else:
            st.session_state.selected_user_id = None
            render_standings_view(users_df)
    else:
        render_standings_view(users_df)

if __name__ == "__main__":
    main()
