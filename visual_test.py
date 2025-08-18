import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

from mister_fetch_players import MisterAPI
from mister_parser import parse_users_from_standings

class UserCard(tk.Frame):
    """
    Una tarjeta para mostrar la información de un usuario.
    """
    def __init__(self, parent, user_data):
        super().__init__(parent, borderwidth=2, relief="groove", padx=10, pady=10)
        self.user_data = user_data
        self.avatar_image = None  # Para evitar que el recolector de basura lo elimine
        self.create_widgets()

    def create_widgets(self):
        # Frame para la imagen
        avatar_frame = tk.Frame(self)
        avatar_frame.pack(side="left", padx=(0, 10))
        self.avatar_label = tk.Label(avatar_frame) # Placeholder
        self.avatar_label.pack()

        # Frame para la información
        info_frame = tk.Frame(self)
        info_frame.pack(side="left")

        name_label = ttk.Label(info_frame, text=self.user_data['name'], font=("Arial", 12, "bold"))
        name_label.pack(anchor="w")

        points_label = ttk.Label(info_frame, text=f"Puntos: {self.user_data['points']}")
        points_label.pack(anchor="w")
        
        value_label = ttk.Label(info_frame, text=f"Valor: {self.user_data['team_value']:,} €")
        value_label.pack(anchor="w")

        # Cargar imagen en un hilo separado
        if self.user_data['avatar_url']:
            threading.Thread(target=self.load_image, daemon=True).start()

    def load_image(self):
        try:
            response = requests.get(self.user_data['avatar_url'])
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((50, 50), Image.LANCZOS)
            self.avatar_image = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_image)
        except Exception as e:
            print(f"Error cargando imagen para {self.user_data['name']}: {e}")


class VisualTestApp(tk.Tk):
    def __init__(self, users):
        super().__init__()
        self.title("Test Visual de Clasificación")
        self.geometry("400x600")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(main_frame, text="Clasificación de la Liga", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))

        for user in users:
            card = UserCard(main_frame, user)
            card.pack(fill="x", pady=5, padx=5)

def main():
    """
    Función principal para obtener datos y lanzar la app.
    """
    print("Obteniendo datos de la API...")
    api = MisterAPI()
    standings_html = api.get_standings()
    
    if not standings_html:
        print("No se pudo obtener la clasificación.")
        return

    print("Parseando datos...")
    users = parse_users_from_standings(standings_html)

    if not users:
        print("No se encontraron usuarios.")
        return

    print("Lanzando aplicación visual...")
    app = VisualTestApp(users)
    app.mainloop()


if __name__ == "__main__":
    main()
