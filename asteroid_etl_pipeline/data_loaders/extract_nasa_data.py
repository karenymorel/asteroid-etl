from src.extract import run_extraction

@data_loader
def load_data_from_api(*args, **kwargs):
    print("🚀 [Mage] Iniciando extracción desde la API de la NASA...")
    run_extraction()
    return {}
