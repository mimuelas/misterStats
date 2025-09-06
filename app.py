"""
Aplicación principal de Mister Fantasy con navegación por pestañas.
Incluye 5 pestañas principales: Inicio, Mercado, Equipo, Tabla y Buscar.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.data_service import DataService
from backend.models.data_models import PlayerSearchFilters

# Configuración de la página
st.set_page_config(
    page_title="Mister Fantasy Stats",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para la barra de navegación
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .tab-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
    }
    
    .player-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    
    .player-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .search-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data_service():
    """Obtiene el servicio de datos con caché."""
    return DataService()

def render_header():
    """Renderiza el header principal de la aplicación."""
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Mister Fantasy Stats</h1>
        <p>Análisis completo de tu liga de fantasía</p>
    </div>
    """, unsafe_allow_html=True)

def render_home_tab(data_service):
    """Renderiza la pestaña de Inicio."""
    st.header("🏠 Inicio")
    
    # Obtener datos del feed
    with st.spinner("Cargando noticias..."):
        feed_data = data_service.get_feed()
    
    if feed_data:
        st.subheader("📰 Últimas Noticias")
        st.markdown("""
        <div class="tab-container">
            <p>Feed de noticias cargado correctamente. Aquí se mostrarían las últimas noticias y eventos de la comunidad.</p>
            <p><strong>Tamaño de datos:</strong> {:,} caracteres</p>
        </div>
        """.format(len(feed_data)), unsafe_allow_html=True)
    
    # Obtener balance
    with st.spinner("Cargando balance..."):
        balance = data_service.get_balance()
    
    if balance:
        st.subheader("💰 Balance de Cuenta")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Balance Actual", f"{balance.current:,} €")
        with col2:
            st.metric("Balance Futuro", f"{balance.future:,} €")
        with col3:
            st.metric("Deuda Máxima", f"{balance.max_debt:,} €")

def render_market_tab(data_service):
    """Renderiza la pestaña de Mercado."""
    st.header("🛒 Mercado")
    
    try:
        st.info("🔄 Cargando datos del mercado...")
        market_data = data_service.get_market()
        st.success(f"✅ Datos del mercado cargados: {type(market_data).__name__}")
    except Exception as e:
        st.error(f"❌ Error cargando mercado: {e}")
        market_data = None
    
    if market_data:
        st.subheader("📊 Mercado de Jugadores")
        st.markdown("""
        <div class="tab-container">
            <p>Mercado cargado correctamente. Aquí se mostrarían los jugadores disponibles para compra.</p>
            <p><strong>Tipo de datos:</strong> MarketOptions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar opciones de filtrado
        st.subheader("🔍 Filtros de Búsqueda")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position = st.selectbox("Posición", ["Todas", "Portero", "Defensa", "Centrocampista", "Delantero"], key="market_position")
        with col2:
            team = st.selectbox("Equipo", ["Todos", "Real Madrid", "Barcelona", "Atlético Madrid"], key="market_team")
        with col3:
            max_price = st.number_input("Precio Máximo", min_value=0, value=10000000, step=1000000, key="market_max_price")
        
        if st.button("🔍 Buscar Jugadores", key="market_search_btn"):
            st.success("Búsqueda realizada (funcionalidad en desarrollo)")

def render_team_tab(data_service):
    """Renderiza la pestaña de Equipo."""
    st.header("⚽ Mi Equipo")
    
    with st.spinner("Cargando equipo..."):
        team_data = data_service.get_team()
    
    if team_data:
        st.subheader("👥 Formación Actual")
        st.markdown("""
        <div class="tab-container">
            <p>Equipo cargado correctamente. Aquí se mostraría la formación actual del usuario.</p>
            <p><strong>Tipo de datos:</strong> Dict</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simular formación
        st.subheader("🏟️ Alineación")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
                <h4>Formación 1-3-4-3</h4>
                <p>Formación típica del Mister Fantasy</p>
            </div>
            """, unsafe_allow_html=True)

def render_standings_tab(data_service):
    """Renderiza la pestaña de Tabla/Clasificación."""
    st.header("🏆 Clasificación")
    
    try:
        st.info("🔄 Cargando datos de clasificación...")
        standings_data = data_service.get_standings_parsed()
        st.success(f"✅ Datos cargados: {len(standings_data) if standings_data else 0} usuarios")
        
        if standings_data:
            st.write(f"📊 Primer usuario: {standings_data[0].name if standings_data[0] else 'N/A'}")
    except Exception as e:
        st.error(f"❌ Error cargando clasificación: {e}")
        standings_data = None
    
    if standings_data:
        st.subheader("📊 Tabla de Posiciones")
        
        # Crear DataFrame para la tabla
        df_data = []
        for user in standings_data:
            df_data.append({
                'Posición': user.position,
                'Usuario': user.name,
                'Puntos': user.points,
                'Diferencia': user.points_diff or 'N/A',
                'Jugadores': user.num_players or 'N/A',
                'Valor Equipo': f"{user.team_value:,} €" if user.team_value else 'N/A',
                'ID': user.id,
                'Slug': user.slug
            })
        
        df = pd.DataFrame(df_data)
        
        # Mostrar tabla con enlaces a detalles
        for idx, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**#{row['Posición']}**")
                with col2:
                    if st.button(f"👤 {row['Usuario']}", key=f"user_{row['ID']}"):
                        st.session_state.selected_user_id = row['ID']
                        st.session_state.selected_user_slug = row['Slug']
                        st.rerun()
                with col3:
                    st.markdown(f"**{row['Puntos']} pts**")
                with col4:
                    st.markdown(f"**{row['Diferencia']}**")
                with col5:
                    st.markdown("📈")
                
                st.divider()
        
        # Gráfico de puntos
        if len(df) > 1:
            st.subheader("📈 Gráfico de Puntos")
            fig = px.bar(df.head(10), x='Usuario', y='Puntos', 
                        title="Top 10 - Puntos por Usuario",
                        color='Puntos',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def render_search_tab(data_service):
    """Renderiza la pestaña de Búsqueda."""
    st.header("🔍 Buscar Jugadores")
    
    st.markdown("""
    <div class="search-container">
        <h3>🔍 Búsqueda Avanzada de Jugadores</h3>
        <p>Utiliza los filtros para encontrar el jugador perfecto para tu equipo.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de búsqueda
    col1, col2 = st.columns(2)
    
    with col1:
        player_name = st.text_input("Nombre del jugador", placeholder="Ej: Mbappé", key="search_name")
        position = st.selectbox("Posición", ["Todas", "Portero", "Defensa", "Centrocampista", "Delantero"], key="search_position")
        team = st.selectbox("Equipo", ["Todos", "Real Madrid", "Barcelona", "Atlético Madrid"], key="search_team")
    
    with col2:
        max_price = st.number_input("Precio Máximo", min_value=0, value=50000000, step=1000000, key="search_max_price")
        min_points = st.number_input("Puntos Mínimos", min_value=0, value=0, key="search_min_points")
        injured_only = st.checkbox("Solo lesionados", key="search_injured")
    
    if st.button("🔍 Buscar", type="primary"):
        with st.spinner("Buscando jugadores..."):
            # Crear filtros de búsqueda
            filters = PlayerSearchFilters(
                name=player_name if player_name else "",
                position=0,  # 0 = todas las posiciones
                team=0,      # 0 = todos los equipos
                value=max_price,
                points=min_points,
                injured=1 if injured_only else 0,
                benched=0,
                favs=0,
                owner=0,
                stealable=0,
                offset=0,
                order=0
            )
            
            # Realizar búsqueda
            search_result = data_service.search_players(filters)
            
            if search_result and search_result.get('players'):
                st.subheader(f"🎯 Resultados de Búsqueda ({len(search_result['players'])} jugadores)")
                
                for player in search_result['players'][:10]:  # Mostrar solo los primeros 10
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{player['name']}**")
                        with col2:
                            st.markdown(f"*{player['position']}*")
                        with col3:
                            st.markdown(f"**{player['points']} pts**")
                        with col4:
                            st.markdown(f"**{player['value']:,} €**")
                        with col5:
                            if st.button("👁️", key=f"view_{player['id']}"):
                                st.session_state.selected_player_id = player['id']
                                st.session_state.selected_player_slug = player.get('slug', '')
                                st.rerun()
                        
                        st.divider()
            else:
                st.warning("No se encontraron jugadores con esos criterios.")

def render_user_detail(user_id, user_slug, data_service):
    """Renderiza la página de detalle de usuario."""
    st.header("👤 Detalle de Usuario")
    
    with st.spinner("Cargando detalles del usuario..."):
        user_details = data_service.get_user_details(user_id, user_slug)
    
    if user_details:
        # Información del usuario
        st.markdown(f"""
        <div class="user-card">
            <h2>👤 {user_details.user.name or 'Usuario'}</h2>
            <p><strong>ID:</strong> {user_details.id}</p>
            <p><strong>Comunidad:</strong> {user_details.user.id_community}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas de temporada
        st.subheader("📊 Estadísticas de Temporada")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Posición", f"#{user_details.season.rank}")
        with col2:
            st.metric("Puntos Totales", f"{user_details.season.points}")
        with col3:
            st.metric("Promedio", f"{user_details.season.avg:.1f}")
        
        # Gráfico de puntos por jornada
        if user_details.gameweeks:
            st.subheader("📈 Puntos por Jornada")
            gameweeks_data = []
            for gw in user_details.gameweeks.values():
                gameweeks_data.append({
                    'Jornada': gw.gameweek,
                    'Puntos': gw.points,
                    'Posición': gw.rank
                })
            
            df_gw = pd.DataFrame(gameweeks_data)
            fig = px.line(df_gw, x='Jornada', y='Puntos', 
                         title="Evolución de Puntos por Jornada",
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # Equipo actual
        if user_details.team_now:
            st.subheader("⚽ Equipo Actual")
            for player in user_details.team_now[:5]:  # Mostrar solo los primeros 5
                st.markdown(f"• **{player.name}** ({player.position}) - {player.points} pts - {player.value:,} €")
    
    # Botón para volver
    if st.button("← Volver a la Clasificación"):
        st.session_state.selected_user_id = None
        st.session_state.selected_user_slug = None
        st.rerun()

def render_player_detail(player_id, player_slug, data_service):
    """Renderiza la página de detalle de jugador."""
    st.header("⚽ Detalle de Jugador")
    
    with st.spinner("Cargando detalles del jugador..."):
        player = data_service.get_player_details(player_id, player_slug)
    
    if player:
        # Información del jugador
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if hasattr(player, 'photo_url') and player.photo_url:
                st.image(player.photo_url, width=200)
            else:
                st.markdown("🖼️ *Sin foto disponible*")
        
        with col2:
            st.markdown(f"""
            <div class="user-card">
                <h2>⚽ {player.name}</h2>
                <p><strong>Posición:</strong> {player.position}</p>
                <p><strong>Puntos:</strong> {player.points}</p>
                <p><strong>Promedio:</strong> {player.avg}</p>
                <p><strong>Valor:</strong> {player.value:,} €</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Información del equipo
        if hasattr(player, 'team') and player.team:
            st.subheader("🏟️ Equipo")
            st.markdown(f"**{player.team.name}**")
            if hasattr(player.team, 'logo_url') and player.team.logo_url:
                st.image(player.team.logo_url, width=100)
        
        # Información de transferencia
        if hasattr(player, 'transfer') and player.transfer:
            st.subheader("💰 Información de Transferencia")
            st.markdown(f"**Precio:** {player.transfer.price:,} €")
            st.markdown(f"**Fecha:** {player.transfer.date}")
            st.markdown(f"**Origen:** {player.transfer.origin}")
    
    # Botón para volver
    if st.button("← Volver a la Búsqueda"):
        st.session_state.selected_player_id = None
        st.session_state.selected_player_slug = None
        st.rerun()

def main():
    """Función principal de la aplicación."""
    try:
        st.info("🚀 Iniciando aplicación Mister Fantasy Stats...")
        # Inicializar el servicio de datos
        data_service = get_data_service()
        st.success("✅ Servicio de datos inicializado")
        
        # Renderizar header
        render_header()
        
        # Verificar si hay una página de detalle seleccionada
        if st.session_state.get('selected_user_id'):
            st.info(f"👤 Mostrando detalles del usuario: {st.session_state.selected_user_id}")
            render_user_detail(st.session_state.selected_user_id, 
                             st.session_state.selected_user_slug, 
                             data_service)
            return
        
        if st.session_state.get('selected_player_id'):
            st.info(f"⚽ Mostrando detalles del jugador: {st.session_state.selected_player_id}")
            render_player_detail(st.session_state.selected_player_id, 
                               st.session_state.selected_player_slug, 
                               data_service)
            return
    except Exception as e:
        st.error(f"❌ Error en la aplicación: {e}")
        st.exception(e)
        return
    
    # Crear las pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "🛒 Mercado", "⚽ Equipo", "🏆 Tabla", "🔍 Buscar"])
    
    with tab1:
        render_home_tab(data_service)
    
    with tab2:
        render_market_tab(data_service)
    
    with tab3:
        render_team_tab(data_service)
    
    with tab4:
        render_standings_tab(data_service)
    
    with tab5:
        render_search_tab(data_service)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>⚽ Mister Fantasy Stats - Análisis completo de tu liga de fantasía</p>
        <p>Desarrollado con ❤️ usando Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
