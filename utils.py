from uuid import UUID
from datetime import datetime

def validar_leitura(dados):
    campos_obrigatorios = ["sensor_id", "timestamp", "tipo", "temperatura", "umidade", "pressao"]

    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ValueError(f"Campo obrigatório ausente: {campo}")

    try:
        sensor_id = UUID(dados["sensor_id"])
        timestamp = datetime.fromisoformat(dados["timestamp"])
        tipo = str(dados["tipo"])
        temperatura = float(dados["temperatura"])
        umidade = float(dados["umidade"])
        pressao = float(dados["pressao"])
    except Exception as e:
        raise ValueError(f"Erro na validação dos campos: {str(e)}")

    return {
        "sensor_id": str(sensor_id),
        "timestamp": timestamp,
        "tipo": tipo,
        "temperatura": temperatura,
        "umidade": umidade,
        "pressao": pressao,
    }
