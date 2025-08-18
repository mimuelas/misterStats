import requests
import json

class MisterAPI:
    """
    Un cliente para interactuar con la API no oficial de Mister Fantasy.
    Utiliza los headers y cookies extraídas de una sesión de navegador válida.
    """
    def __init__(self):
        self.base_url = "https://mister.mundodeportivo.com"
        self.session = requests.Session()

        # Cabeceras extraídas del cURL proporcionado.
        self.session.headers.update({
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "origin": "https://mister.mundodeportivo.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-auth": "596bd4e0ffacb9c557238afd0c58845c",
            "x-requested-with": "XMLHttpRequest",
            "partial-request": "true"
        })

        # Cookies extraídas.
        self.session.cookies.update({
            'PHPSESSID': '1abd2bafbb07652f780d8527477e83e4',
            'token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiIxNzU1MDQxOTk1IiwidXNlcmlkIjoiMjE0ODgzMiIsImFsZyI6IkVTMjU2In0.etY2S42q6vx6HdUfEtf1sDcD4iVWt4O_KG85hltMjoQsxKbm7Taiik2OvYzb0isCkBBzC58GKbUn4Ya517mcbA',
            'refresh-token': 'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiI0OTEwNzE1Mjk1IiwicmVmcmVzaCI6ImZjT1oxV3pqQmNXMVI5RHA0akVnMiIsImlkX3Rva2VuX2xpZmV0aW1lX2luX21pbiI6IjUiLCJhbGciOiJFUzI1NiJ9.nrsEDmi0TKd0gdhl-AYYIHHdX-dLf6_k-AgDQoJElE5hVtFqmI-VAkNjhqIKh5OQtoh-yRG5ztabpY76azDVTw',
        })

    def _request(self, method, endpoint, post_data=None):
        """
        Método base para realizar una petición a la API.
        Soporta tanto GET como POST.
        """
        url = f"{self.base_url}{endpoint}"
        self.session.headers['referer'] = f"{self.base_url}/" 

        try:
            if method.upper() == 'POST':
                response = self.session.post(url, data=post_data)
            else:
                response = self.session.get(url)
            
            print(f"Request to {url} completed with status: {response.status_code}") # DEBUG
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text

        except requests.exceptions.RequestException as e:
            print(f"Error en la petición a {url}: {e}")
            return None

    def get_balance(self):
        """Obtiene el balance de la cuenta."""
        return self._request("GET", "/ajax/balance")

    def get_team(self):
        """Obtiene la información del equipo del usuario. Devuelve HTML."""
        return self._request("GET", "/team")

    def get_market(self):
        """Obtiene la información del mercado. Devuelve HTML."""
        return self._request("GET", "/market")

    def get_standings(self):
        """Obtiene la clasificación de la liga. Devuelve HTML."""
        return self._request("GET", "/standings")

    def get_feed(self):
        """Obtiene el feed de noticias y eventos. Devuelve HTML o JSON."""
        return self._request("POST", "/feed")

    def get_player_details(self, player_id):
        """
        Obtiene los detalles de un jugador específico por su ID.
        Devuelve JSON.
        """
        post_data = {'post': 'players', 'id': player_id}
        return self._request("POST", "/ajax/sw/players", post_data=post_data)

    def get_team_details(self, team_id, team_slug, comments=0):
        """
        Obtiene los detalles de un equipo específico por su ID y slug.
        Devuelve JSON.
        """
        post_data = {'post': 'teams', 'id': team_id, 'slug': team_slug, 'comments': comments}
        return self._request("POST", "/ajax/sw/teams", post_data=post_data)

    def get_user_details(self, user_id, user_slug, comments=0):
        """
        Obtiene los detalles de un usuario/rival específico por su ID y slug.
        Devuelve JSON.
        """
        post_data = {'post': 'users', 'id': user_id, 'slug': user_slug, 'comments': comments}
        return self._request("POST", "/ajax/sw/users", post_data=post_data)

    def community_check(self):
        """
        Comprueba si hay novedades en la comunidad (nuevos mensajes, pujas, etc).
        Devuelve JSON.
        """
        return self._request("POST", "/ajax/community-check")

