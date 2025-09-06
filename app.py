"""
Aplicación Streamlit para Mister Fantasy Stats.
Dashboard completo con análisis de liga, jugadores, participantes y más.
"""

import streamlit as st
import sys
import os
from datetime import datetime

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

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f4e79, #2d5a87);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Renderiza el header de la aplicación."""
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Mister Fantasy Stats</h1>
        <p>Análisis completo de tu liga de fantasía</p>
    </div>
    """, unsafe_allow_html=True)

def render_home_tab(data_service):
    """Renderiza la pestaña de inicio con scroll infinito automático."""
    st.header("🏠 Inicio - Feed")
    
    # Inicializar session state para scroll infinito
    if 'feed_offset' not in st.session_state:
        st.session_state.feed_offset = 0
    if 'all_feed_items' not in st.session_state:
        st.session_state.all_feed_items = []
    if 'loading_more' not in st.session_state:
        st.session_state.loading_more = False
    if 'no_more_content' not in st.session_state:
        st.session_state.no_more_content = False
    
    # Cargar datos iniciales si no hay elementos
    if not st.session_state.all_feed_items:
        with st.spinner("Cargando feed inicial..."):
            feed_data = data_service.get_feed_parsed(offset=0)
            if feed_data and 'items' in feed_data:
                st.session_state.all_feed_items = feed_data.get('items', [])
                st.session_state.feed_offset = 20  # Siguiente página
    
    # Mostrar todos los elementos cargados
    if st.session_state.all_feed_items:
        st.success(f"✅ Feed cargado: {len(st.session_state.all_feed_items)} elementos")
        
        # Mostrar resumen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Elementos", len(st.session_state.all_feed_items))
        with col2:
            transfers = len([item for item in st.session_state.all_feed_items if item.get('category') == 'transfer'])
            st.metric("Transferencias", transfers)
        with col3:
            player_transfers = len([item for item in st.session_state.all_feed_items if item.get('category') == 'player_transfer'])
            st.metric("Cambios de Equipo", player_transfers)
        with col4:
            posts = len([item for item in st.session_state.all_feed_items if item.get('category') == 'post'])
            st.metric("Mensajes", posts)
        
        # ===== FEED CRONOLÓGICO =====
        st.subheader("📰 Feed de Actividad")
        
        # Mostrar todos los elementos en orden cronológico
        for item in st.session_state.all_feed_items:
            category = item.get('category', 'unknown')
            date = item.get('date', 'N/A')
            
            # Crear contenedor para cada elemento
            with st.container():
                if category == 'transfer':
                    transfer_info = item.get('transfer_info', {})
                    if transfer_info:
                        col1, col2, col3 = st.columns([2, 1, 2])
                        with col1:
                            st.write(f"**{transfer_info.get('from_user', 'N/A')}**")
                        with col2:
                            st.write(f"→ {transfer_info.get('price', 0):,} €")
                        with col3:
                            st.write(f"**{transfer_info.get('to_user', 'N/A')}**")
                        
                        player_name = transfer_info.get('player_name')
                        if player_name:
                            st.write(f"⚽ {player_name} - {date}")
                        else:
                            st.write(f"💰 Transferencia - {date}")
                
                elif category == 'player_transfer':
                    transfer_info = item.get('player_transfer_info', {})
                    if transfer_info:
                        col1, col2, col3 = st.columns([2, 1, 2])
                        with col1:
                            st.write(f"**{transfer_info.get('team_from', 'N/A')}**")
                        with col2:
                            st.write(f"→")
                        with col3:
                            st.write(f"**{transfer_info.get('team_to', 'N/A')}**")
                        
                        player_name = transfer_info.get('player_name')
                        if player_name:
                            st.write(f"⚽ {player_name} - {date}")
                        else:
                            st.write(f"🔄 Cambio de equipo - {date}")
                
                elif category == 'gameweek_end':
                    gameweek_info = item.get('gameweek_info', {})
                    if gameweek_info:
                        st.write(f"🏁 **Jornada {gameweek_info.get('gameweek_number', 'N/A')} finalizada** - {date}")
                
                elif category == 'post':
                    post_info = item.get('post_info', {})
                    if post_info:
                        st.write(f"💬 **{post_info.get('name', 'Usuario')}**: {post_info.get('text', '')[:100]}... - {date}")
                
                else:
                    st.write(f"📋 **{category.replace('_', ' ').title()}** - {date}")
                
                st.divider()
        
        # ===== SCROLL INFINITO AUTOMÁTICO =====
        # Usar un botón que se activa automáticamente con JavaScript
        if not st.session_state.no_more_content:
            # JavaScript para detectar scroll y activar el botón
            st.markdown("""
            <script>
            // Función para detectar scroll hacia abajo
            function checkScroll() {
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
                    // Buscar el botón de cargar más
                    const button = document.querySelector('button[data-testid="baseButton-secondary"]');
                    if (button && !button.disabled) {
                        button.click();
                    }
                }
            }
            
            // Agregar listener de scroll
            window.addEventListener('scroll', checkScroll);
            
            // Verificar scroll inicial después de un delay
            setTimeout(checkScroll, 2000);
            </script>
            """, unsafe_allow_html=True)
            
            # Botón para cargar más contenido (se activa con JavaScript)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Cargar Más Contenido", type="secondary", use_container_width=True, key="load_more_btn"):
                    st.session_state.loading_more = True
                    st.rerun()
        
        # Procesar carga de más contenido
        if st.session_state.loading_more and not st.session_state.no_more_content:
            with st.spinner("Cargando más contenido..."):
                more_feed_data = data_service.get_feed_parsed(offset=st.session_state.feed_offset, use_cache=False)
                
                if more_feed_data and 'items' in more_feed_data and len(more_feed_data['items']) > 0:
                    # Agregar nuevos elementos a la lista
                    st.session_state.all_feed_items.extend(more_feed_data['items'])
                    st.session_state.feed_offset += 20
                    st.success(f"✅ Cargados {len(more_feed_data['items'])} elementos más")
                    st.session_state.loading_more = False
                    st.rerun()
                else:
                    st.session_state.no_more_content = True
                    st.info("📭 No hay más contenido disponible")
                    st.session_state.loading_more = False
        
        # Mostrar información de estado
        if st.session_state.no_more_content:
            st.info("📭 Has llegado al final del feed")
        else:
            st.info(f"📄 Cargados {len(st.session_state.all_feed_items)} elementos (offset: {st.session_state.feed_offset})")
            
    else:
        st.warning("No se pudieron cargar las noticias.")


def render_market_tab(data_service):
    """Renderiza la pestaña de Mercado."""
    st.header("🛒 Mercado")
    
    try:
        with st.spinner("Cargando datos del mercado..."):
            market_data = data_service.get_market_parsed()
        st.success(f"✅ Datos del mercado cargados: {type(market_data).__name__}")
    except Exception as e:
        st.error(f"❌ Error cargando mercado: {e}")
        market_data = None
    
    if market_data:
        st.subheader("📊 Mercado de Jugadores")
        
        # Mostrar información del mercado
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Créditos Disponibles", f"{market_data.credits:,}")
        with col2:
            st.metric("Mostrar Pujas", "Sí" if market_data.show_bids else "No")
        with col3:
            st.metric("Filtros Activos", len(market_data.filters) if market_data.filters else 0)
        
        # Mostrar jugadores del feed (novedades mercado)
        st.subheader("🆕 Novedades del Mercado")
        st.info("Los jugadores más recientes en el mercado aparecen en el feed de noticias")
        
        # Botón para ir al mercado completo
        if st.button("🔍 Ver Mercado Completo", type="primary"):
            st.info("Redirigiendo al mercado completo...")
    else:
        st.warning("No se pudieron cargar los datos del mercado.")
        
        # Mostrar opciones de filtrado
        st.subheader("🔍 Filtros de Búsqueda")
        
        col1, col2 = st.columns(2)
        with col1:
            position = st.selectbox("Posición", ["Todas", "Portero", "Defensa", "Centrocampista", "Delantero"], key="market_position")
            max_price = st.number_input("Precio máximo (€)", min_value=0, value=50000000, step=1000000, key="market_price")
        with col2:
            team = st.selectbox("Equipo", ["Todos"], key="market_team")
            injured_only = st.checkbox("Solo lesionados", key="market_injured")
        
        if st.button("🔍 Buscar en Mercado", type="primary"):
            st.info("Buscando jugadores en el mercado...")


def render_team_tab(data_service):
    """Renderiza la pestaña de Mi Plantilla."""
    st.header("⚽ Mi Plantilla")
    
    try:
        with st.spinner("Cargando datos del equipo..."):
            team_data = data_service.get_team_parsed()
        st.success(f"✅ Datos del equipo cargados: {type(team_data).__name__}")
    except Exception as e:
        st.error(f"❌ Error cargando equipo: {e}")
        team_data = None
    
    if team_data:
        st.subheader("📊 Información del Equipo")
        
        # Mostrar información básica del equipo
        if 'gameweek_info' in team_data:
            gameweek = team_data['gameweek_info']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jornada", gameweek.get('current_gameweek', 'N/A'))
            with col2:
                st.metric("Estado", gameweek.get('status', 'N/A'))
            with col3:
                st.metric("Próximo Partido", gameweek.get('next_match', 'N/A'))
        
        # Mostrar estadísticas del equipo
        if 'team_stats' in team_data:
            stats = team_data['team_stats']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Puntos Totales", stats.get('total_points', 0))
            with col2:
                st.metric("Promedio", f"{stats.get('average', 0):.1f}")
            with col3:
                st.metric("Valor del Equipo", f"{stats.get('team_value', 0):,} €")
            with col4:
                st.metric("Jugadores", stats.get('num_players', 0))
        
        # Mostrar jugadores
        if 'players' in team_data:
            players = team_data['players']
            st.subheader("👥 Jugadores del Equipo")
            
            for i, player in enumerate(players[:10]):  # Mostrar hasta 10 jugadores
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{player.get('name', 'N/A')}**")
                with col2:
                    st.write(f"Pos: {player.get('position', 'N/A')}")
                with col3:
                    st.write(f"Puntos: {player.get('points', 0)}")
                with col4:
                    st.write(f"Precio: {player.get('price', 0):,} €")
    else:
        st.warning("No se pudieron cargar los datos del equipo.")


def render_standings_tab(data_service):
    """Renderiza la pestaña de Clasificación."""
    st.header("🏆 Clasificación")
    
    try:
        with st.spinner("Cargando clasificación..."):
            standings = data_service.get_standings_parsed()
        st.success(f"✅ Clasificación cargada: {len(standings)} usuarios")
    except Exception as e:
        st.error(f"❌ Error cargando clasificación: {e}")
        standings = []
    
    if standings:
        st.subheader("📊 Tabla de Clasificación")
        
        # Crear DataFrame para la tabla
        import pandas as pd
        
        data = []
        for user in standings:
            data.append({
                'Posición': user.position,
                'Usuario': user.name,
                'Puntos': user.points,
                'Diferencia': user.points_diff,
                'Jugadores': user.num_players,
                'Valor Equipo': f"{user.team_value:,} €"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Mostrar top 3
        st.subheader("🥇 Top 3")
        for i, user in enumerate(standings[:3]):
            medal = ["🥇", "🥈", "🥉"][i]
            st.write(f"{medal} **{user.name}** - {user.points} puntos")
    else:
        st.warning("No se pudieron cargar los datos de clasificación.")


def render_search_tab(data_service):
    """Renderiza la pestaña de Buscar Jugadores."""
    st.header("🔍 Buscar Jugadores")
    
    # Formulario de búsqueda
    st.subheader("🔍 Filtros de Búsqueda")
    
    col1, col2 = st.columns(2)
    with col1:
        player_name = st.text_input("Nombre del jugador", key="search_name")
        position = st.selectbox("Posición", ["Todas", "Portero", "Defensa", "Centrocampista", "Delantero"], key="search_position")
        max_price = st.number_input("Precio máximo (€)", min_value=0, value=50000000, step=1000000, key="search_price")
    with col2:
        team = st.selectbox("Equipo", ["Todos"], key="search_team")
        injured_only = st.checkbox("Solo lesionados", key="search_injured")
    
    if st.button("🔍 Buscar", type="primary"):
        with st.spinner("Buscando jugadores..."):
            # Crear filtros de búsqueda
            filters = PlayerSearchFilters(
                name=player_name if player_name else "",
                position=0,  # 0 = todas las posiciones
                team=0,      # 0 = todos los equipos
                value=max_price,
                injured=1 if injured_only else 0,
                benched=0,
                favs=0,
                owner=0,
                stealable=0,
                offset=0,
                order=0
            )
            
            # Realizar búsqueda
            search_results = data_service.get_search_parsed()
            
            if search_results:
                st.success("✅ Búsqueda completada")
                
                # Mostrar resultados
                st.subheader("📋 Resultados de la Búsqueda")
                
                if 'players' in search_results:
                    players = search_results['players']
                    for i, player in enumerate(players[:10]):  # Mostrar hasta 10 jugadores
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        with col1:
                            st.write(f"**{player.get('name', 'N/A')}**")
                        with col2:
                            st.write(f"Pos: {player.get('position', 'N/A')}")
                        with col3:
                            st.write(f"Puntos: {player.get('points', 0)}")
                        with col4:
                            st.write(f"Precio: {player.get('price', 0):,} €")
            else:
                st.warning("No se encontraron jugadores con esos criterios.")


def main():
    """Función principal de la aplicación."""
    render_header()
    
    # Inicializar DataService
    try:
        data_service = DataService()
        st.success("✅ Servicio de datos inicializado correctamente")
    except Exception as e:
        st.error(f"❌ Error inicializando servicio de datos: {e}")
        return
    
    # Crear pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "🛒 Mercado", "⚽ Equipo", "🏆 Clasificación", "🔍 Buscador"])
    
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

if __name__ == "__main__":
    main()
