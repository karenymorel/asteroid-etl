from src.transform import run_transformation

@transformer
def transform_data(data, *args, **kwargs):
    print("⚡ [Mage] Iniciando transformación y validación Pydantic...")
    run_transformation()
    return {}