import json

def run_transformation():
  print("Cargando datos crudos...")
  try:
      with open("asteroides_2025_crudo.json", "r") as f:
          raw_data = json.load(f)
  except FileNotFoundError:
      print("Error: No se encontró el archivo 'asteroides_2025_crudo.json'. ¿Corriste la extracción primero?")
      exit()


  asteroids_db = {}
  close_approaches_db = []

  print("Iniciando transformación de datos...")

  for date, asteroid_list in raw_data.items():
      for ast in asteroid_list:
          ast_id = ast["id"]
          
          if ast_id not in asteroids_db:
              meters_diameter = ast.get("estimated_diameter", {}).get("meters", {})
              
              asteroids_db[ast_id] = {
                  "id": ast_id,
                  "name": ast.get("name"),
                  "absolute_magnitude": ast.get("absolute_magnitude_h"),
                  "diameter_min_meters": meters_diameter.get("estimated_diameter_min"),
                  "diameter_max_meters": meters_diameter.get("estimated_diameter_max"),
                  "is_potentially_hazardous": ast.get("is_potentially_hazardous_asteroid"),
                  "is_sentry_object": ast.get("is_sentry_object")
              }
              
          for approach in ast.get("close_approach_data", []):
              relative_velocity = approach.get("relative_velocity", {})
              miss_distance = approach.get("miss_distance", {})
              
              try:
                  velocity_kmh = float(relative_velocity.get("kilometers_per_hour", 0))
                  miss_distance_km = float(miss_distance.get("kilometers", 0))
              except (ValueError, TypeError):
                  velocity_kmh = 0.0
                  miss_distance_km = 0.0
              
              approach_event = {
                  "asteroid_id": ast_id,
                  "approach_date": approach.get("close_approach_date"),
                  "velocity_kmh": velocity_kmh,
                  "miss_distance_km": miss_distance_km,
                  "orbiting_body": approach.get("orbiting_body")
              }
              close_approaches_db.append(approach_event)

  print("\nTransformación finalizada.")

  asteroids_list = list(asteroids_db.values())

  print(f"-> Total de asteroides únicos estructurados: {len(asteroids_list)}")
  print(f"-> Total de eventos de aproximación registrados: {len(close_approaches_db)}")

  with open("asteroids_limpio.json", "w") as f:
      json.dump(asteroids_list, f, indent=4)

  with open("approaches_limpio.json", "w") as f:
      json.dump(close_approaches_db, f, indent=4)

  print("\nArchivos transformados guardados como 'asteroids_limpio.json' y 'approaches_limpio.json'.")

if __name__ == "__main__":
    run_transformation()