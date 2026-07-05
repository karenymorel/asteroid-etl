import requests
import json
import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIG
API_KEY = os.getenv("NASA_API_KEY")

if not API_KEY:
    raise ValueError("¡Error! No se encontró la variable NASA_API_KEY en el archivo .env")

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

def run_extraction():

  current_start = datetime.datetime.strptime(START_DATE, "%Y-%m-%d").date()
  final_end = datetime.datetime.strptime(END_DATE, "%Y-%m-%d").date()

  all_asteroids = {}

  print("Iniciando la extracción del año 2025...")

  while current_start <= final_end:
    current_end = min(current_start + datetime.timedelta(days=6), final_end)

    print(f"Descargando rango: {current_start} al {current_end}...")
    
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={current_start}&end_date={current_end}&api_key={API_KEY}"

    try:
      response = requests.get(url)
      response.raise_for_status()
      data = response.json()

      weekly_asteroids = data.get("near_earth_objects", {})

      all_asteroids.update(weekly_asteroids)

    except requests.exceptions.RequestException as e:
        print(f"Error en el rango {current_start} - {current_end}: {e}")
        print("Deteniendo la extracción para evitar pérdida de consistencia.")
        break

    current_start = current_end + datetime.timedelta(days=1)

    time.sleep(1)

  print(f"\nExtracción finalizada. Se obtuvieron datos de {len(all_asteroids)} días diferentes.")

  with open("asteroides_2025_crudo.json", "w") as f:
      json.dump(all_asteroids, f, indent=4)

  print("Datos guardados con éxito en asteroides_2025_crudo.json")

if __name__ == "__main__":
    run_extraction()