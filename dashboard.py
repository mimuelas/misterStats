import streamlit as st
import json
import pandas as pd
import altair as alt
from datetime import datetime

# --- Configuración de la página ---
st.set_page_config(
    page_title="Mister Stats Dashboard",
    page_icon="⚽",
    layout="wide"
)

# --- Funciones de ayuda ---
def format_currency(value):
    """Formatea un número como moneda en euros, usando puntos para los miles."""
    if isinstance(value, (int, float)):
        return f"{value:,.0f} €".replace(",", ".")
    return "N/A"

# --- Título del Dashboard ---
st.title("Dashboard de Jugador - Mister Fantasy ⚽")

# --- Carga de datos ---
try:
    with open("player_details_27425.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
except FileNotFoundError:
    st.error("❌ No se encontró el fichero 'player_details_27425.json'.")
    st.info("Asegúrate de ejecutar primero el script: python mister_fetch_players.py")
    st.stop()

# --- Extracción y preparación de datos ---
if json_data.get('status') == 'ok' and 'data' in json_data:
    data = json_data['data']
    player_info = data.get('player', {})
    player_bio = player_info.get('bio', {})
    market_value = player_info.get('value')
    values_summary = data.get('values', [])
    points_history = data.get('points_history', [])
    prices_data = data.get('values_chart', {}).get('points', [])
    next_match_data = data.get('next_match', {}).get(str(player_info.get('id')))
else:
    st.error("El fichero JSON no tiene el formato esperado o el estado no es 'ok'.")
    st.stop()

# --- Barra lateral con información del jugador ---
st.sidebar.image(player_info.get('photoUrl'), width=120)
st.sidebar.header(player_info.get('name', 'N/A'))
st.sidebar.subheader(f"*{player_info.get('team', {}).get('name', 'N/A')}*")
st.sidebar.divider()
st.sidebar.markdown(f"**Edad:** {player_bio.get('age', 'N/A')}")
st.sidebar.markdown(f"**Altura:** {player_bio.get('height', 'N/A')} cm")
st.sidebar.markdown(f"**Peso:** {player_bio.get('weight', 'N/A')} kg")

# --- Cuerpo Principal ---
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
    
    # Mapeo de meses en español a inglés porque el formato en el JSON no es estándar
    # y no puede ser parseado directamente con un locale.
    month_map = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun',
        'jul': 'Jul', 'ago': 'Aug', 'sept': 'Sep', 'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    
    # Usamos .str.replace para cambiar los nombres de los meses
    date_series = df_prices['date'].str.lower()
    for esp, eng in month_map.items():
        date_series = date_series.str.replace(esp, eng, regex=False)
    
    # Convertimos a datetime usando el formato con meses en inglés
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
        # Formateo manual para asegurar el símbolo y los separadores
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
        # Formatear la media a 2 decimales
        df_points['avg'] = df_points['avg'].apply(lambda x: f"{x:.2f}")
        df_points = df_points.rename(columns={'season': 'Temporada', 'points': 'Puntos', 'avg': 'Media'})
        st.dataframe(df_points, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay historial de puntos disponible.")
