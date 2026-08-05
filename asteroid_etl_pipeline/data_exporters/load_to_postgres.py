from src.load import run_loading

@data_exporter
def export_data(data, *args, **kwargs):
    print("🛢️ [Mage] Iniciando carga a la base de datos PostgreSQL...")
    run_loading()


