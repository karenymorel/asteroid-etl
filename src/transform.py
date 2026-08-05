import json
from pydantic import ValidationError
from src.schemas import AsteroidSchema, CloseApproachSchema

def run_transformation():
    print("Cargando datos crudos...")
    try:
        with open("asteroides_2025_crudo.json", "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'asteroides_2025_crudo.json'. ¿Corriste la extracción primero?")
        return

    asteroids_db = {}
    close_approaches_db = []

    print("Iniciando transformación y validación de datos con Pydantic...")

    for date_str, asteroid_list in raw_data.items():
        for ast in asteroid_list:
            ast_id = str(ast.get("id"))
            
            # 1. Procesar y Validar Asteroide
            if ast_id not in asteroids_db:
                meters_diameter = ast.get("estimated_diameter", {}).get("meters", {})
                
                try:
                    asteroid_obj = AsteroidSchema(
                        id=ast_id,
                        name=ast.get("name", "Unknown"),
                        absolute_magnitude=ast.get("absolute_magnitude_h"),
                        diameter_min_meters=meters_diameter.get("estimated_diameter_min"),
                        diameter_max_meters=meters_diameter.get("estimated_diameter_max"),
                        is_potentially_hazardous=ast.get("is_potentially_hazardous_asteroid", False),
                        is_sentry_object=ast.get("is_sentry_object", False)
                    )

                    asteroids_db[ast_id] = asteroid_obj.model_dump(mode="json")
                except ValidationError as e:
                    print(f"⚠️ Error de validación en Asteroide ID {ast_id}: {e}")
                    continue

            # 2. Procesar y Validar Aproximaciones 
            for approach in ast.get("close_approach_data", []):
                relative_velocity = approach.get("relative_velocity", {})
                miss_distance = approach.get("miss_distance", {})
                
                try:
                    approach_obj = CloseApproachSchema(
                        asteroid_id=ast_id,
                        approach_date=approach.get("close_approach_date"),
                        velocity_kmh=relative_velocity.get("kilometers_per_hour", 0.0),
                        miss_distance_km=miss_distance.get("kilometers", 0.0),
                        orbiting_body=approach.get("orbiting_body", "Earth")
                    )
                    close_approaches_db.append(approach_obj.model_dump(mode="json"))
                except ValidationError as e:
                    print(f"⚠️ Error de validación en Aproximación de Asteroide {ast_id}: {e}")
                    continue

    print("\nTransformación y Validación finalizadas con éxito.")

    asteroids_list = list(asteroids_db.values())

    print(f"-> Total de asteroides únicos validados: {len(asteroids_list)}")
    print(f"-> Total de eventos de aproximación validados: {len(close_approaches_db)}")

    with open("asteroids_limpio.json", "w") as f:
        json.dump(asteroids_list, f, indent=4)

    with open("approaches_limpio.json", "w") as f:
        json.dump(close_approaches_db, f, indent=4)

    print("\nArchivos limpios y validados guardados correctamente.")

if __name__ == "__main__":
    run_transformation()