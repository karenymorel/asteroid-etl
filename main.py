import time
from src.extract import run_extraction
from src.transform import run_transformation
from src.load import run_loading

def main():
    start_time = time.time()
    
    print("==================================================")
    print("      INICIANDO PIPELINE ETL DE LA NASA 🚀        ")
    print("==================================================\n")
    
    try:
        # Fase 1: Extracción
        print("[ETL] Fase 1: Extrayendo datos desde la API...")
        run_extraction()
        
        # Fase 2: Transformación
        print("\n[ETL] Fase 2: Transformando y limpiando datos...")
        run_transformation()
        
        # Fase 3: Carga
        print("\n[ETL] Fase 3: Cargando datos estructurados a PostgreSQL...")
        run_loading()
        
        # Fin del proceso
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n==================================================")
        print("      ¡PIPELINE FINALIZADO CON ÉXITO! 🎉         ")
        print(f"      Tiempo total de ejecución: {duration:.2f} segundos")
        print("==================================================")
        
    except Exception as e:
        print("\n==================================================")
        print(f"      ❌ ERROR CRÍTICO: El pipeline falló")
        print(f"      Detalle: {e}")
        print("==================================================")

if __name__ == "__main__":
    main()