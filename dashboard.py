import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from bs4 import BeautifulSoup
import re
from mister_fetch_players import MisterAPI

# --- Configuración de la página ---
st.set_page_config(
    page_title="Mister Stats Dashboard",
    page_icon="⚽",
    layout="wide"
)

# --- Instancia de la API ---
api = MisterAPI()

# --- Funciones de ayuda ---
def format_currency(value):
    """Formatea un número como moneda en euros, usando puntos para los miles."""
    if isinstance(value, (int, float)):
        return f"{value:,.0f} €".replace(",", ".")
    return "N/A"

def parse_team_html(html_content):
    """Parsea el HTML del equipo para extraer la información de los jugadores."""
    soup = BeautifulSoup(html_content, 'html.parser')
    players = []
    
    player_list = soup.find('ul', class_='list-team')
    if not player_list:
        return []

    for player_item in player_list.find_all('li'):
        player_id = player_item.get('id', '').replace('player-', '')
        if not player_id:
            continue

        name_div = player_item.find('div', class_='name')
        name = name_div.text.strip() if name_div else 'N/A'
        
        img_tag = player_item.find('div', class_='player-avatar').find('img')
        photo_url = img_tag['src'] if img_tag else ''

        position_div = player_item.find('div', class_='player-position')
        position_map = {'1': 'PT', '2': 'DF', '3': 'MC', '4': 'DL'}
        position = position_map.get(position_div['data-position'], 'N/A') if position_div else 'N/A'
        
        value_span = player_item.find('div', class_='underName')
        market_value = 0
        if value_span:
            # Use regex to find the first sequence of digits and dots (the value)
            numeric_match = re.search(r'[\d\.]+', value_span.text)
            if numeric_match:
                # Remove dots used as thousands separators and convert to int
                value_text = numeric_match.group(0).replace('.', '')
                if value_text.isdigit():
                    market_value = int(value_text)

        points_div = player_item.find('div', class_='points')
        points = points_div.text.strip() if points_div else 'N/A'

        avg_div = player_item.find('div', class_='avg')
        avg_points = avg_div.text.strip() if avg_div else 'N/A'
        
        team_logo_img = player_item.find('img', class_='team-logo')
        team_logo = team_logo_img['src'] if team_logo_img else ''

        players.append({
            'id': player_id,
            'name': name,
            'photoUrl': photo_url,
            'position': position,
            'value': market_value,
            'points': points,
            'avg_points': avg_points,
            'team_logo': team_logo
        })
    return players


def show_team_view(players):
    """Muestra la vista de la plantilla completa."""
    st.title("Mi Plantilla - Mister Fantasy ⚽")

    positions = {'PT': 'Porteros', 'DF': 'Defensas', 'MC': 'Centrocampistas', 'DL': 'Delanteros'}
    
    for pos_code, pos_name in positions.items():
        st.subheader(pos_name)
        
        position_players = [p for p in players if p['position'] == pos_code]
        
        if not position_players:
            st.info(f"No tienes {pos_name.lower()}.")
            continue

        cols = st.columns(4) 
        
        for i, player in enumerate(position_players):
            with cols[i % 4]:
                st.image(player['photoUrl'], width=100)
                st.markdown(f"**{player['name']}**")
                
                # Info de equipo y puntos
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(player['team_logo'], width=24)
                with col2:
                    st.markdown(f"**Pts:** {player['points']} | **Media:** {player['avg_points']}")

                st.caption(f"Valor: {format_currency(player['value'])}")

                if st.button("Ver detalles", key=f"btn_{player['id']}"):
                    st.session_state.selected_player_id = player['id']
                    st.rerun()
        
        st.divider()


def show_player_details_view(player_id):
    """Muestra la vista de detalles de un jugador específico."""
    
    # Botón para volver a la vista del equipo
    if st.button("⬅️ Volver a la plantilla"):
        del st.session_state.selected_player_id
        st.rerun()

    # Cargar datos del jugador desde la API
    json_data = api.get_player_details(player_id)

    if not json_data or json_data.get('status') != 'ok':
        st.error("No se pudieron obtener los datos del jugador.")
        st.stop()

    # --- Extracción y preparación de datos ---
    data = json_data.get('data', {})
    player_info = data.get('player', {})
    player_bio = player_info.get('bio', {})
    market_value = player_info.get('value')
    values_summary = data.get('values', [])
    points_history = data.get('points_history', [])
    prices_data = data.get('values_chart', {}).get('points', [])
    next_match_data = data.get('next_match', {}).get(str(player_info.get('id')))

    # --- Barra lateral con información del jugador ---
    st.sidebar.image(player_info.get('photoUrl'), width=120)
    st.sidebar.header(player_info.get('name', 'N/A'))
    st.sidebar.subheader(f"*{player_info.get('team', {}).get('name', 'N/A')}*")
    st.sidebar.divider()
    st.sidebar.markdown(f"**Edad:** {player_bio.get('age', 'N/A')}")
    st.sidebar.markdown(f"**Altura:** {player_bio.get('height', 'N/A')} cm")
    st.sidebar.markdown(f"**Peso:** {player_bio.get('weight', 'N/A')} kg")

    # --- Cuerpo Principal ---
    st.title(f"Dashboard de {player_info.get('name', 'N/A')} ⚽")
    st.subheader("Datos de Mercado")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Valor de Mercado Actual", value=format_currency(market_value))
    with col2:
        clause_value = player_info.get('clause', {}).get('value')
        st.metric(label="Cláusula de Rescisión", value=format_currency(clause_value))
    with col3:
        if next_match_data:
            home_team = next_match_data.get('home')
            away_team = next_match_data.get('away')
            match_time_ts = next_match_data.get('date', {}).get('ts')
            match_time = datetime.fromtimestamp(match_time_ts).strftime('%d/%m %H:%Mh') if match_time_ts else "N/A"
            st.metric(label="Próximo Partido", value=f"{home_team} vs {away_team}")
            st.caption(match_time)
        else:
            st.metric(label="Próximo Partido", value="No disponible")

    # --- Gráfico ---
    st.subheader("Historial de Valor de Mercado")
    if prices_data:
        df_prices = pd.DataFrame(prices_data)
        
        month_map = {
            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun',
            'jul': 'Jul', 'ago': 'Aug', 'sept': 'Sep', 'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
        }
        
        date_series = df_prices['date'].str.lower()
        for esp, eng in month_map.items():
            date_series = date_series.str.replace(esp, eng, regex=False)
        
        df_prices['date'] = pd.to_datetime(date_series, format='%d %b %Y')

        chart = alt.Chart(df_prices).mark_line(
            point=alt.OverlayMarkDef(color="#1DB954", size=40), color="#1DB954"
        ).encode(
            x=alt.X('date:T', title='Fecha'),
            y=alt.Y('value:Q', title='Valor de Mercado (€)', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('date:T', title='Fecha'), alt.Tooltip('value:Q', title='Valor', format=',.0f')]
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos de historial de precios para mostrar.")

    st.divider()

    # --- Dos columnas para tablas de datos ---
    col_values, col_points = st.columns(2)
    with col_values:
        st.subheader("Historial de Valores")
        if values_summary:
            df_values = pd.DataFrame(values_summary)
            df_values['change_formatted'] = df_values['change'].apply(
                lambda x: f"{x:+,.0f}".replace(",", ".") if isinstance(x, (int, float)) else x
            )
            st.dataframe(df_values[['time', 'change_formatted']],
                         column_config={"time": "Periodo", "change_formatted": "Variación"},
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No hay resumen de valores disponible.")

    with col_points:
        st.subheader("Historial de Puntos")
        if points_history:
            df_points = pd.DataFrame(points_history)
            df_points['avg'] = df_points['avg'].apply(lambda x: f"{x:.2f}")
            df_points = df_points.rename(columns={'season': 'Temporada', 'points': 'Puntos', 'avg': 'Media'})
            st.dataframe(df_points, use_container_width=True, hide_index=True)
        else:
            st.warning("No hay historial de puntos disponible.")


# --- Lógica principal de la aplicación ---
if 'selected_player_id' in st.session_state:
    show_player_details_view(st.session_state.selected_player_id)
else:
    # Cargar y parsear el HTML del equipo
    team_html = api.get_team()
    if team_html:
        players = parse_team_html(team_html)
        if players:
            show_team_view(players)
        else:
            st.error("No se pudieron encontrar jugadores en la página del equipo.")
    else:
        st.error("No se pudo obtener la información del equipo.")
