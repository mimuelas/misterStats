from mister_fetch_players import MisterAPI
import json

def test_endpoints():
    """
    Prueba los endpoints de la API de Mister y muestra la información que devuelven.
    """
    api = MisterAPI()
    
    print("--- Probando get_balance() ---")
    balance = api.get_balance()
    if balance:
        print("Formato: JSON")
        print("Datos relevantes:")
        print(json.dumps(balance, indent=2))
    else:
        print("No se pudo obtener el balance.")
    print("-" * 30)

    print("--- Probando get_team() ---")
    team = api.get_team()
    if team:
        print("Formato: HTML")
        print("Datos relevantes (primeros 500 caracteres):")
        print(team[:500])
    else:
        print("No se pudo obtener la información del equipo.")
    print("-" * 30)
    
    print("--- Probando get_market() ---")
    market = api.get_market()
    if market:
        print("Formato: HTML")
        print("Datos relevantes (primeros 500 caracteres):")
        print(market[:500])
    else:
        print("No se pudo obtener la información del mercado.")
    print("-" * 30)

    print("--- Probando get_standings() ---")
    standings = api.get_standings()
    if standings:
        print("Formato: HTML")
        print("Datos relevantes (primeros 500 caracteres):")
        print(standings[:500])
    else:
        print("No se pudo obtener la clasificación.")
    print("-" * 30)

    print("--- Probando get_feed() ---")
    feed = api.get_feed()
    if feed:
        # El feed puede devolver JSON o HTML dependiendo del contenido
        try:
            feed_json = json.loads(feed)
            print("Formato: JSON")
            print("Datos relevantes:")
            print(json.dumps(feed_json, indent=2))
        except (json.JSONDecodeError, TypeError):
            print("Formato: HTML")
            print("Datos relevantes (primeros 500 caracteres):")
            print(str(feed)[:500])
    else:
        print("No se pudo obtener el feed.")
    print("-" * 30)


if __name__ == "__main__":
    test_endpoints()
