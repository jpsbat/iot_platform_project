from uuid import UUID
from datetime import datetime

def validar_leitura(dados):
    campos_obrigatorios = ["sensor_id", "timestamp", "tipo", "valores"]

    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ValueError(f"Campo obrigatório ausente: {campo}")

    try:
        sensor_id = UUID(dados["sensor_id"])
        timestamp = datetime.fromisoformat(dados["timestamp"])
        tipo = str(dados["tipo"])
        valores = dados["valores"]
        if isinstance(valores, str):
            import json
            valores = json.loads(valores)
        if not isinstance(valores, dict):
            raise ValueError("O campo 'valores' deve ser um dicionário.")
        # Converte todos os valores para float
        valores = {str(k): float(v) for k, v in valores.items()}
    except Exception as e:
        raise ValueError(f"Erro na validação dos campos: {str(e)}")

    return {
        "sensor_id": str(sensor_id),
        "timestamp": timestamp,
        "tipo": tipo,
        "valores": valores,
    }