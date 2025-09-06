"""
Archivo de testeo único para probar TODOS los endpoints y guardar respuestas parseadas.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.data_service import DataService
from backend.models.data_models import PlayerSearchFilters

def create_test_directory():
    """Crea el directorio de test si no existe."""
    test_dir = Path("datatest")
    test_dir.mkdir(exist_ok=True)
    return test_dir

def save_test_data(data, filename, test_dir):
    """Guarda los datos de test en un archivo JSON."""
    file_path = test_dir / f"{filename}.json"
    
    try:
        # Si es HTML (string), guardarlo como texto plano
        if isinstance(data, str) and ('<div' in data or '<html' in data or '<script' in data):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
        else:
            # Convertir objetos a diccionarios si es necesario
            if hasattr(data, '__dict__'):
                data_dict = data.__dict__
            elif isinstance(data, list):
                data_dict = []
                for item in data:
                    if hasattr(item, '__dict__'):
                        data_dict.append(item.__dict__)
                    else:
                        data_dict.append(item)
            else:
                data_dict = data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Guardado: {filename}.json")
        return True
    except Exception as e:
        print(f"❌ Error guardando {filename}: {e}")
        return False

def test_all_endpoints():
    """Prueba todos los endpoints y guarda las respuestas."""
    print("🧪 INICIANDO TEST COMPLETO DE ENDPOINTS")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear directorio de test
    test_dir = create_test_directory()
    print(f"📁 Directorio de test: {test_dir.absolute()}")
    print()
    
    # Inicializar servicio de datos
    data_service = DataService()
    
    # Lista de tests a realizar
    tests = [
        {
            'name': 'balance',
            'description': 'Balance de cuenta',
            'function': lambda: data_service.get_balance(),
            'required': True
        },
        {
            'name': 'standings_raw',
            'description': 'Clasificación (HTML)',
            'function': lambda: data_service.get_standings(),
            'required': True
        },
        {
            'name': 'standings_parsed',
            'description': 'Clasificación parseada',
            'function': lambda: data_service.get_standings_parsed(),
            'required': True
        },
        {
            'name': 'market_raw',
            'description': 'Mercado (HTML)',
            'function': lambda: data_service.get_market(),
            'required': True
        },
        {
            'name': 'market_parsed',
            'description': 'Mercado parseado',
            'function': lambda: data_service.get_market_parsed(),
            'required': True
        },
        {
            'name': 'team_raw',
            'description': 'Equipo (HTML)',
            'function': lambda: data_service.get_team(),
            'required': True
        },
        {
            'name': 'team_parsed',
            'description': 'Equipo parseado',
            'function': lambda: data_service.get_team_parsed(),
            'required': True
        },
        {
            'name': 'feed_raw',
            'description': 'Feed (HTML)',
            'function': lambda: data_service.get_feed(),
            'required': True
        },
        {
            'name': 'feed_parsed',
            'description': 'Feed parseado',
            'function': lambda: data_service.get_feed_parsed(),
            'required': False
        },
        {
            'name': 'search_parsed',
            'description': 'Búsqueda parseada',
            'function': lambda: data_service.get_search_parsed(),
            'required': False
        },
        {
            'name': 'player_details_mbappe',
            'description': 'Detalles de Mbappé',
            'function': lambda: data_service.get_player_details(58954, 'kylian-mbappe'),
            'required': True
        },
        {
            'name': 'player_details_budimir',
            'description': 'Detalles de Budimir',
            'function': lambda: data_service.get_player_details(18004, 'ante-budimir'),
            'required': True
        },
        {
            'name': 'user_details_leopoldo',
            'description': 'Detalles de Leopoldo Panero',
            'function': lambda: data_service.get_user_details(14648707, 'leopoldo-panero'),
            'required': True
        },
        {
            'name': 'search_players_all',
            'description': 'Búsqueda de todos los jugadores',
            'function': lambda: data_service.search_players(PlayerSearchFilters()),
            'required': True
        },
        {
            'name': 'search_players_delanteros',
            'description': 'Búsqueda de delanteros',
            'function': lambda: data_service.search_players(PlayerSearchFilters(position=4)),
            'required': True
        },
        {
            'name': 'search_players_mbappe',
            'description': 'Búsqueda de Mbappé',
            'function': lambda: data_service.search_players(PlayerSearchFilters(name='mbappe')),
            'required': True
        }
    ]
    
    # Ejecutar tests
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(tests),
        'successful': 0,
        'failed': 0,
        'results': []
    }
    
    for i, test in enumerate(tests, 1):
        print(f"🔍 {i}/{len(tests)} Probando: {test['description']}")
        
        try:
            # Ejecutar función de test
            data = test['function']()
            
            if data is not None:
                # Guardar datos
                success = save_test_data(data, test['name'], test_dir)
                
                if success:
                    results['successful'] += 1
                    results['results'].append({
                        'name': test['name'],
                        'status': 'success',
                        'description': test['description'],
                        'data_type': type(data).__name__,
                        'file': f"{test['name']}.json"
                    })
                    print(f"   ✅ ÉXITO - {type(data).__name__}")
                else:
                    results['failed'] += 1
                    results['results'].append({
                        'name': test['name'],
                        'status': 'error',
                        'description': test['description'],
                        'error': 'Error guardando archivo'
                    })
                    print(f"   ❌ ERROR - No se pudo guardar")
            else:
                results['failed'] += 1
                results['results'].append({
                    'name': test['name'],
                    'status': 'error',
                    'description': test['description'],
                    'error': 'Datos nulos'
                })
                print(f"   ❌ FALLO - Sin datos")
                
        except Exception as e:
            results['failed'] += 1
            results['results'].append({
                'name': test['name'],
                'status': 'error',
                'description': test['description'],
                'error': str(e)
            })
            print(f"   ❌ ERROR - {str(e)}")
        
        print()
    
    # Guardar resumen de resultados
    results['success_rate'] = (results['successful'] / results['total_tests']) * 100
    results['test_directory'] = str(test_dir.absolute())
    
    with open(test_dir / 'test_summary.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print("📊 RESUMEN DE RESULTADOS:")
    print("-" * 40)
    print(f"✅ Exitosos: {results['successful']}/{results['total_tests']}")
    print(f"❌ Fallidos: {results['failed']}/{results['total_tests']}")
    print(f"📈 Tasa de éxito: {results['success_rate']:.1f}%")
    print(f"📁 Directorio: {test_dir.absolute()}")
    print()
    
    # Mostrar archivos generados
    print("📄 ARCHIVOS GENERADOS:")
    print("-" * 40)
    for file in sorted(test_dir.glob("*.json")):
        size = file.stat().st_size
        print(f"   📄 {file.name} ({size:,} bytes)")
    
    print()
    print(f"⏰ Test finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    test_all_endpoints()
