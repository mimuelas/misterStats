from bs4 import BeautifulSoup
import re

def parse_team_value(value_str):
    """Limpia y convierte el valor del equipo a un entero."""
    return int(value_str.replace('€', '').replace('.', '').strip())

def parse_users_from_standings(html_content):
    """
    Parsea el HTML de la página de clasificación para extraer todos los
    datos relevantes de los usuarios.

    Args:
        html_content (str): El contenido HTML de la página /standings.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa
              a un usuario con todos sus datos.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    users = []
    
    general_standings_panel = soup.find('div', class_='panel-total')

    if not general_standings_panel:
        return []

    user_rows = general_standings_panel.find_all('li')

    for row in user_rows:
        user_link = row.find('a', class_='user')
        if not user_link:
            continue

        position_div = user_link.find('div', class_='position')
        position = int(position_div.text.strip()) if position_div else None

        name_div = user_link.find('div', class_='name')
        name = name_div.text.strip()

        href = user_link.get('href')
        user_id, user_slug = None, None
        if href:
            match = re.search(r'users/(\d+)/([\w-]+)', href)
            if match:
                user_id = match.group(1)
                user_slug = match.group(2)

        avatar_img = user_link.find('img')
        avatar_url = avatar_img['src'] if avatar_img else None

        points_div = user_link.find('div', class_='points')
        points = int(points_div.contents[0].strip()) if points_div else None
        
        diff_div = points_div.find('div', class_='diff') if points_div else None
        points_diff = diff_div.text.strip() if diff_div else None

        played_div = user_link.find('div', class_='played')
        num_players, team_value = None, None
        if played_div:
            played_text = played_div.text.strip()
            # "17 jugadores · € 51.921.000"
            parts = played_text.split('·')
            if len(parts) == 2:
                players_part = parts[0]
                value_part = parts[1]
                num_players_match = re.search(r'(\d+)', players_part)
                if num_players_match:
                    num_players = int(num_players_match.group(1))
                team_value = parse_team_value(value_part)

        users.append({
            'position': position,
            'name': name,
            'id': user_id,
            'slug': user_slug,
            'avatar_url': avatar_url,
            'points': points,
            'points_diff': points_diff,
            'num_players': num_players,
            'team_value': team_value,
        })
                
    return users

def parse_first_player_id_from_team(html_content):
    """
    Parsea el HTML de la página del equipo para extraer el ID del primer jugador.
    
    Args:
        html_content (str): El contenido HTML de la página /team.

    Returns:
        str: El ID del primer jugador encontrado, o None si no se encuentra.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    player_link = soup.find('a', class_='player-link')
    if player_link and player_link.get('data-id'):
        return player_link.get('data-id')
    return None
