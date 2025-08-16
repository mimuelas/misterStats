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
    """
    Parsea el HTML del equipo para extraer la información de los jugadores y los datos del resumen del footer.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # --- Extraer jugadores ---
    players = []
    player_list = soup.find('ul', class_='list-team')
    if player_list:
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
                numeric_match = re.search(r'[\d\.]+', value_span.text)
                if numeric_match:
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

    # --- Extraer resumen del footer ---
    summary_data = {
        'player_count': 'N/A',
        'team_value': 'N/A',
        'balance': 'N/A'
    }
    footer_info = soup.find('div', class_='live-balance')
    if footer_info:
        items = footer_info.find_all('div', class_='item')
        if len(items) == 3:
            summary_data['player_count'] = items[0].find('div', class_='value').text.strip()
            summary_data['team_value'] = items[1].find('div', class_='value').text.strip()
            summary_data['balance'] = items[2].find('div', class_='value').text.strip()

    return {'players': players, 'summary': summary_data}


def show_rebuilt_team_view(players, summary, team_html_content):
    """
    Muestra una vista del equipo reconstruida 100% con componentes de Streamlit
    y CSS personalizado para imitar el diseño original de forma robusta.
    """
    soup = BeautifulSoup(team_html_content, 'html.parser')

    # --- 1. Mostrar métricas del equipo ---
    variations = get_daily_variations(players)
    total_variation = sum(variations.values())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saldo Actual", summary['balance'])
    col2.metric("Valor del Equipo", summary['team_value'])
    col3.metric("Jugadores", summary['player_count'])
    col4.metric("Variación Hoy", format_currency(total_variation),
                delta=f"{total_variation:,.0f}".replace(",", "."),
                delta_color=("inverse" if total_variation < 0 else "normal"))
    st.divider()

    # --- 2. Recrear el campo de fútbol y la alineación ---
    st.subheader("Alineación Titular")

    # Extraer IDs de jugadores titulares
    lineup_players_ids = [btn.get('data-id_player') for btn in soup.select('.lineup-starting .lineup-player')]

    # Extraer la formación (líneas)
    lines = {}
    for i in range(4, 0, -1):
        line_div = soup.find('div', class_=f'line-{i}')
        if line_div:
            player_ids_in_line = [btn.get('data-id_player') for btn in line_div.find_all('button')]
            # Mapear IDs a los datos completos del jugador que ya tenemos
            lines[i] = [p for p in players if p['id'] in player_ids_in_line]
    
    # Renderizar campo y jugadores con CSS personalizado
    st.markdown("""
    <style>
        .field {
            background: linear-gradient(to bottom, #006400, #004d00);
            border-radius: 10px;
            padding: 20px 10px;
            border: 2px solid #C8E6C9;
            position: relative;
        }
        .field::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            border-top: 2px solid rgba(255, 255, 255, 0.3);
        }
        .field-circle {
            width: 120px;
            height: 120px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .player-card {
            text-align: center;
            color: white;
            margin-bottom: 10px;
        }
        .player-card img {
            border-radius: 50%;
            border: 2px solid white;
            background-color: rgba(255, 255, 255, 0.1);
        }
        .player-card .name {
            font-size: 0.8rem;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.6);
            padding: 2px 6px;
            border-radius: 5px;
            display: inline-block;
            margin-top: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="field"><div class="field-circle"></div>', unsafe_allow_html=True)
        # Iterar en orden inverso para que los delanteros aparezcan arriba
        for i in sorted(lines.keys(), reverse=True):
            players_in_line = lines[i]
            if not players_in_line: continue
            
            cols = st.columns(len(players_in_line))
            for idx, player in enumerate(players_in_line):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="player-card">
                        <img src="{player['photoUrl']}" width="70">
                        <div class="name">{player['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver", key=f"btn_lineup_{player['id']}"):
                        st.query_params['player_id'] = player['id']
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # --- 3. Mostrar la lista completa de la plantilla ---
    st.subheader("Plantilla Completa")
    
    for i in range(0, len(players), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(players):
                player = players[i+j]
                with cols[j]:
                    st.image(player['photoUrl'], width=80)
                    st.markdown(f"**{player['name']}**")
                    variation = variations.get(player['id'], 0)
                    delta_text = f"{format_currency(variation)}"
                    
                    st.metric(
                        label=f"{format_currency(player['value'])}",
                        value=f"Pts: {player['points']} | Media: {player['avg_points']}",
                        delta=delta_text,
                        delta_color=("inverse" if variation < 0 else "normal")
                    )
                    if st.button("Ver Detalles", key=f"btn_squad_{player['id']}"):
                        st.query_params['player_id'] = player['id']
                        st.rerun()


def show_player_details_view(player_id):
    """Muestra la vista de detalles de un jugador específico."""
    
    # Botón para volver a la vista del equipo
    if st.button("⬅️ Volver a la plantilla"):
        st.query_params.clear()
        st.rerun()

    with st.spinner(f"Cargando detalles del jugador ID: {player_id}..."):
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


def get_daily_variations(players):
    """
    Obtiene la variación de valor de mercado del último día para una lista de jugadores.
    Muestra un spinner en Streamlit durante la carga.
    """
    variations = {}
    with st.spinner('Calculando variaciones de mercado...'):
        for player in players:
            player_id = player['id']
            details = api.get_player_details(player_id)
            if details and details.get('status') == 'ok':
                values_summary = details.get('data', {}).get('values', [])
                # Buscar la variación de 'Un día'
                daily_change = next((item['change'] for item in values_summary if item.get('time') == 'Un día'), 0)
                variations[player_id] = daily_change
    return variations


# --- Lógica principal de la aplicación ---
if "player_id" in st.query_params:
    show_player_details_view(st.query_params["player_id"])
else:
    st.title("Mi Equipo - Mister Fantasy ⚽")
    team_html_content = api.get_team()
    
    if not team_html_content:
        st.error("No se pudo obtener la información del equipo.")
        st.stop()
        
    parsed_data = parse_team_html(team_html_content)
    players = parsed_data['players']
    summary = parsed_data['summary']
    
    if not players:
        st.error("No se pudieron encontrar jugadores en la página del equipo.")
        st.stop()

    show_rebuilt_team_view(players, summary, team_html_content)
