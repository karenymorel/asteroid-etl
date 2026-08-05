import os
import json
import psycopg2
from dotenv import load_dotenv

def run_loading():
    load_dotenv(override=True)

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    if DB_HOST in ["localhost", "127.0.0.1", "db"]:
        DB_SSLMODE = "disable"
    else:
        DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

    print(f"Conectando a la base de datos PostgreSQL en: '{DB_HOST}' (Puerto: {DB_PORT}, SSL: {DB_SSLMODE})...")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode=DB_SSLMODE
        )
        cursor = conn.cursor()
        print("¡Conexión exitosa a la base de datos!")

        create_asteroids_table = """
        CREATE TABLE IF NOT EXISTS asteroids (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255),
            absolute_magnitude FLOAT,
            diameter_min_meters FLOAT,
            diameter_max_meters FLOAT,
            is_potentially_hazardous BOOLEAN,
            is_sentry_object BOOLEAN
        );
        """

        create_approaches_table = """
        CREATE TABLE IF NOT EXISTS close_approaches (
            id SERIAL PRIMARY KEY,
            asteroid_id VARCHAR(50),
            approach_date DATE,
            velocity_kmh FLOAT,
            miss_distance_km FLOAT,
            orbiting_body VARCHAR(100),
            FOREIGN KEY (asteroid_id) REFERENCES asteroids(id) ON DELETE CASCADE
        );
        """

        print("Creando tablas si no existen...")
        cursor.execute(create_asteroids_table)
        cursor.execute(create_approaches_table)
        conn.commit()

        print("\nInsertando datos en la tabla 'asteroids'...")
        with open("asteroids_limpio.json", "r") as f:
            asteroids_data = json.load(f)

        insert_asteroid_query = """
        INSERT INTO asteroids (id, name, absolute_magnitude, diameter_min_meters, diameter_max_meters, is_potentially_hazardous, is_sentry_object)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """

        for ast in asteroids_data:
            cursor.execute(insert_asteroid_query, (
                ast["id"],
                ast["name"],
                ast["absolute_magnitude"],
                ast["diameter_min_meters"],
                ast["diameter_max_meters"],
                ast["is_potentially_hazardous"],
                ast["is_sentry_object"]
            ))

        print("Insertando datos en la tabla 'close_approaches'...")
        with open("approaches_limpio.json", "r") as f:
            approaches_data = json.load(f)

        insert_approach_query = """
        INSERT INTO close_approaches (asteroid_id, approach_date, velocity_kmh, miss_distance_km, orbiting_body)
        VALUES (%s, %s, %s, %s, %s);
        """

        for app in approaches_data:
            cursor.execute(insert_approach_query, (
                app["asteroid_id"],
                app["approach_date"],
                app["velocity_kmh"],
                app["miss_distance_km"],
                app["orbiting_body"]
            ))

        conn.commit()
        print("\n¡Carga finalizada con éxito!")
        print(f"Se insertaron {len(asteroids_data)} registros en 'asteroids'.")
        print(f"Se insertaron {len(approaches_data)} registros en 'close_approaches'.")

    except Exception as e:
        print(f"\nOcurrió un error durante el proceso de carga: {e}")
        if 'conn' in locals():
            conn.rollback()

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("Conexión a la base de datos cerrada de forma limpia.")

if __name__ == "__main__":
    run_loading()