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

# CSS personalizado profesional
st.markdown("""
<style>
/* Importar fuentes de Google */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Variables CSS */
:root {
    --primary-color: #1e40af;
    --secondary-color: #3b82f6;
    --accent-color: #f59e0b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --dark-bg: #0f172a;
    --card-bg: #ffffff;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --border-color: #e5e7eb;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --border-radius: 12px;
    --border-radius-lg: 16px;
}

/* Reset y base */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Header principal */
.main-header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    padding: 2rem;
    border-radius: var(--border-radius-lg);
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: var(--shadow-xl);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}

.main-header h1 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    margin: 0;
    position: relative;
    z-index: 1;
}

.main-header p {
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 1.1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}

/* Pestañas personalizadas */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    margin-bottom: 2rem;
}

.stTabs [data-baseweb="tab"] {
    background: var(--card-bg);
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 0.75rem 1.5rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 1rem;
    color: var(--text-secondary);
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.stTabs [aria-selected="true"] {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
    box-shadow: var(--shadow-lg);
}

/* Métricas del feed */
.feed-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-color);
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.metric-value {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: var(--primary-color);
    margin: 0;
}

.metric-label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: 0.5rem 0 0 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Elementos del feed */
.feed-container {
    background: var(--card-bg);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-color);
    overflow: hidden;
}

.feed-item {
    background: var(--card-bg);
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    transition: all 0.3s ease;
    position: relative;
}

.feed-item:last-child {
    border-bottom: none;
}

.feed-item:hover {
    background: #f8fafc;
    transform: translateX(4px);
}

.feed-item-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.feed-category {
    background: var(--primary-color);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.feed-date {
    color: var(--text-secondary);
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 0.9rem;
}

.feed-content {
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
}

.feed-content h3 {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
}

.feed-content p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin: 0;
}

/* Botones personalizados */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 0.75rem 1.5rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-md);
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

/* Spinner personalizado */
.stSpinner {
    color: var(--primary-color);
}

/* Alertas personalizadas */
.stSuccess {
    background: linear-gradient(135deg, var(--success-color), #34d399);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

.stInfo {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

.stWarning {
    background: linear-gradient(135deg, var(--warning-color), #fbbf24);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

/* Scroll personalizado */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary-color);
}

/* Estilos para nuevas categorías de noticias */
.market-item {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.25rem 0;
    border-left: 3px solid #28a745;
}

.blog-item {
    background: #fff3cd;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.25rem 0;
    border-left: 3px solid #ffc107;
}

.clauses-item {
    background: #f8d7da;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.25rem 0;
    border-left: 3px solid #dc3545;
}

.porra-item {
    background: #d1ecf1;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.25rem 0;
    border-left: 3px solid #17a2b8;
}

.change-name-item {
    background: #e2e3e5;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.25rem 0;
    border-left: 3px solid #6c757d;
}

/* Responsive */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2rem;
    }
    
    .feed-metrics {
        grid-template-columns: 1fr;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .feed-item {
        padding: 1rem;
    }
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
        
        # Mostrar métricas del feed con estilos personalizados
        st.markdown('<div class="feed-metrics">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.all_feed_items)}</div>
                <div class="metric-label">Total Elementos</div>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            transfers = len([item for item in st.session_state.all_feed_items if item.get('category') == 'transfer'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{transfers}</div>
                <div class="metric-label">Transferencias</div>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            market_items = len([item for item in st.session_state.all_feed_items if item.get('category') == 'market_unified'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{market_items}</div>
                <div class="metric-label">Mercado</div>
            </div>
            ''', unsafe_allow_html=True)
        with col4:
            posts = len([item for item in st.session_state.all_feed_items if item.get('category') == 'post'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{posts}</div>
                <div class="metric-label">Mensajes</div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Segunda fila de métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            player_transfers = len([item for item in st.session_state.all_feed_items if item.get('category') == 'player_transfer'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{player_transfers}</div>
                <div class="metric-label">Cambios de Equipo</div>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            blog_posts = len([item for item in st.session_state.all_feed_items if item.get('category') == 'blog'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{blog_posts}</div>
                <div class="metric-label">Blog</div>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            clauses_drops = len([item for item in st.session_state.all_feed_items if item.get('category') == 'clauses_drops'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{clauses_drops}</div>
                <div class="metric-label">Bajas por Cláusulas</div>
            </div>
            ''', unsafe_allow_html=True)
        with col4:
            porras = len([item for item in st.session_state.all_feed_items if item.get('category') == 'porra'])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{porras}</div>
                <div class="metric-label">Apuestas</div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ===== FEED CRONOLÓGICO =====
        st.subheader("📰 Feed de Actividad")
        
        # Contenedor del feed con estilos
        st.markdown('<div class="feed-container">', unsafe_allow_html=True)
        
        # Mostrar todos los elementos en orden cronológico
        for item in st.session_state.all_feed_items:
            category = item.get('category', 'unknown')
            date = item.get('date', 'N/A')
            
            # Crear elemento del feed con estilos
            st.markdown(f'''
            <div class="feed-item">
                <div class="feed-item-header">
                    <span class="feed-category">{category.replace('_', ' ').title()}</span>
                    <span class="feed-date">{date}</span>
                </div>
                <div class="feed-content">
            ''', unsafe_allow_html=True)
            
            if category == 'transfer':
                transfer_info = item.get('transfer_info', {})
                if transfer_info:
                    st.markdown(f'''
                    <h3>💰 Transferencia de Jugador</h3>
                    <p><strong>{transfer_info.get('from_user', 'N/A')}</strong> → <strong>{transfer_info.get('to_user', 'N/A')}</strong></p>
                    <p>💵 Precio: {transfer_info.get('price', 0):,} €</p>
                    <p>⚽ Jugador: {transfer_info.get('player_name', 'N/A')}</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'player_transfer':
                transfer_info = item.get('player_transfer_info', {})
                if transfer_info:
                    st.markdown(f'''
                    <h3>🔄 Cambio de Equipo</h3>
                    <p><strong>{transfer_info.get('team_from', 'N/A')}</strong> → <strong>{transfer_info.get('team_to', 'N/A')}</strong></p>
                    <p>⚽ Jugador: {transfer_info.get('player_name', 'N/A')}</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'gameweek_end':
                gameweek_info = item.get('gameweek_info', {})
                if gameweek_info:
                    st.markdown(f'''
                    <h3>🏁 Jornada Finalizada</h3>
                    <p>Jornada {gameweek_info.get('gameweek_number', 'N/A')} ha terminado</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'post':
                post_info = item.get('post_info', {})
                if post_info:
                    st.markdown(f'''
                    <h3>💬 Mensaje de {post_info.get('name', 'Usuario')}</h3>
                    <p>{post_info.get('text', '')[:200]}{'...' if len(post_info.get('text', '')) > 200 else ''}</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'market_unified':
                market_info = item.get('market_info', {})
                if market_info and 'market_items' in market_info:
                    st.markdown(f'''
                    <h3>🏪 Novedades del Mercado</h3>
                    <p>📊 {market_info.get('total_items', 0)} jugadores en el mercado</p>
                    ''', unsafe_allow_html=True)
                    # Mostrar algunos jugadores destacados
                    for i, market_item in enumerate(market_info.get('market_items', [])[:3]):
                        st.markdown(f'''
                        <div class="market-item">
                            <p>⚽ {market_item.get('player_name', 'N/A')} - {market_item.get('player_position', 'N/A')}</p>
                            <p>💰 Valor: {market_item.get('player_value', 0):,} € | Puntos: {market_item.get('player_points', 0)}</p>
                        </div>
                        ''', unsafe_allow_html=True)
            
            elif category == 'change_name':
                change_info = item.get('change_name_info', {})
                if change_info:
                    st.markdown(f'''
                    <h3>✏️ Cambio de Nombre</h3>
                    <p><strong>{change_info.get('old_name', 'N/A')}</strong> → <strong>{change_info.get('new_name', 'N/A')}</strong></p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'blog':
                blog_info = item.get('blog_info', {})
                if blog_info:
                    st.markdown(f'''
                    <h3>📝 Entrada de Blog</h3>
                    <p><strong>{blog_info.get('title', 'Sin título')}</strong></p>
                    <p>👤 Autor: {blog_info.get('author', 'N/A')}</p>
                    <p>{blog_info.get('excerpt', '')[:150]}{'...' if len(blog_info.get('excerpt', '')) > 150 else ''}</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'clauses_drops':
                clauses_info = item.get('clauses_drops_info', {})
                if clauses_info:
                    st.markdown(f'''
                    <h3>📉 Baja por Cláusula</h3>
                    <p>⚽ Jugador: {clauses_info.get('player_name', 'N/A')}</p>
                    <p>🏢 Equipo: {clauses_info.get('team_name', 'N/A')}</p>
                    <p>💰 Valor: {clauses_info.get('player_value', 0):,} €</p>
                    <p>📊 Puntos: {clauses_info.get('player_points', 0)}</p>
                    ''', unsafe_allow_html=True)
            
            elif category == 'porra':
                porra_info = item.get('porra_info', {})
                if porra_info:
                    st.markdown(f'''
                    <h3>🎲 Apuesta/Porra</h3>
                    <p><strong>{porra_info.get('title', 'Sin título')}</strong></p>
                    <p>👤 Creador: {porra_info.get('creator', 'N/A')}</p>
                    <p>📝 {porra_info.get('description', '')[:100]}{'...' if len(porra_info.get('description', '')) > 100 else ''}</p>
                    ''', unsafe_allow_html=True)
            
            else:
                st.markdown(f'''
                <h3>📋 {category.replace('_', ' ').title()}</h3>
                <p>Información adicional disponible</p>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
