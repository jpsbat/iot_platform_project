from flask import Blueprint, request, jsonify # type: ignore
from uuid import UUID
from utils import validar_leitura
from datetime import datetime, timedelta

bp = Blueprint("leituras", __name__)

def registrar_rotas(session):

    @bp.route("/leituras", methods=["POST"])
    def inserir_leitura():
        if request.is_json:
            dados = request.get_json()
        else:
            dados = request.form.to_dict()
        try:
            dados = validar_leitura(dados)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        session.execute("""
            INSERT INTO sensor_readings (sensor_id, timestamp, tipo, valores)
            VALUES (%s, %s, %s, %s)
        """, (UUID(dados["sensor_id"]), dados["timestamp"], dados["tipo"], dados["valores"]))
        return jsonify({"status": "inserido", "timestamp": dados["timestamp"].isoformat()})

    @bp.route("/leituras/update", methods=["POST"])
    def atualizar_leitura():
        if request.is_json:
            dados = request.get_json()
        else:
            dados = request.form.to_dict()
        try:
            dados = validar_leitura(dados)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        session.execute("""
            UPDATE sensor_readings SET tipo=%s, valores=%s
            WHERE sensor_id=%s AND timestamp=%s
        """, (dados["tipo"], dados["valores"], UUID(dados["sensor_id"]), dados["timestamp"]))
        return jsonify({"status": "atualizado"})

    @bp.route("/leituras/delete_one", methods=["POST"])
    def deletar_uma_leitura():
        dados = request.get_json()
        try:
            sensor_id = UUID(dados["sensor_id"])
            timestamp = datetime.fromisoformat(dados["timestamp"])
        except Exception as e:
            return jsonify({"erro": str(e)}), 400

        session.execute("""
            DELETE FROM sensor_readings WHERE sensor_id=%s AND timestamp=%s
        """, (sensor_id, timestamp))
        return jsonify({"status": "deletado"})

    @bp.route("/leituras/ultima/<sensor_id>")
    def ultima(sensor_id):
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s LIMIT 1
        """, (sensor_id,))
        result = []
        for row in rows:
            d = dict(row._asdict())
            if "valores" in d and d["valores"] is not None:
                d["valores"] = dict(d["valores"])
            if "timestamp" in d and d["timestamp"] is not None:
                d["timestamp"] = d["timestamp"].isoformat()
            result.append(d)
        return jsonify(result)

    @bp.route("/leituras/intervalo", methods=["GET"])
    def por_intervalo():
        sensor_id = request.args.get("sensor_id")
        inicio = request.args.get("inicio")
        fim = request.args.get("fim")
        try:
            sensor_id = UUID(sensor_id)
            inicio = datetime.fromisoformat(inicio)
            fim = datetime.fromisoformat(fim)
        except Exception as e:
            return jsonify({"erro": str(e)}), 400

        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s AND timestamp >= %s AND timestamp <= %s
        """, (sensor_id, inicio, fim))
        result = []
        for row in rows:
            d = dict(row._asdict())
            if "valores" in d and d["valores"] is not None:
                d["valores"] = dict(d["valores"])
            if "timestamp" in d and d["timestamp"] is not None:
                d["timestamp"] = d["timestamp"].isoformat()
            result.append(d)
        return jsonify(result)

    @bp.route("/leituras/limite", methods=["GET"])
    def leituras_limite():
        sensor_id = request.args.get("sensor_id")
        parametro = request.args.get("parametro", "temperatura")
        limite = float(request.args.get("limite", 0))
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s ALLOW FILTERING
        """, (sensor_id,))
        filtrados = []
        for row in rows:
            d = dict(row._asdict())
            if "valores" in d and d["valores"] is not None:
                valores = dict(d["valores"])
                if parametro in valores and valores[parametro] > limite:
                    d["valores"] = valores
                    if "timestamp" in d and d["timestamp"] is not None:
                        d["timestamp"] = d["timestamp"].isoformat()
                    filtrados.append(d)
        return jsonify(filtrados)

    @bp.route("/sensores", methods=["GET"])
    def listar_sensores():
        rows = session.execute("SELECT DISTINCT sensor_id FROM sensor_readings")
        sensores = [str(row.sensor_id) for row in rows]
        return jsonify(sensores)

    @bp.route("/leituras/alertas", methods=["GET"])
    def alertas():
        sensor_id = request.args.get("sensor_id")
        parametro = request.args.get("parametro", "temperatura")
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        limite = float(request.args.get("limite", 80.0))
        agora = datetime.utcnow()
        ontem = agora - timedelta(days=1)
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s AND timestamp >= %s ALLOW FILTERING
        """, (sensor_id, ontem))
        filtrados = []
        for row in rows:
            d = dict(row._asdict())
            if "valores" in d and d["valores"] is not None:
                valores = dict(d["valores"])
                if parametro in valores and valores[parametro] > limite:
                    d["valores"] = valores
                    if "timestamp" in d and d["timestamp"] is not None:
                        d["timestamp"] = d["timestamp"].isoformat()
                    filtrados.append(d)
        return jsonify(filtrados)

    return bp