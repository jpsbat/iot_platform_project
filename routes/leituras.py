from flask import Blueprint, request, jsonify, render_template, redirect, url_for # type: ignore
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
            INSERT INTO sensor_readings (sensor_id, timestamp, tipo, temperatura, umidade, pressao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (UUID(dados["sensor_id"]), dados["timestamp"], dados["tipo"],
              dados["temperatura"], dados["umidade"], dados["pressao"]))
        return redirect(url_for('home'))

    @bp.route("/leituras/update", methods=["POST"])
    def atualizar_leitura():
        dados = request.form.to_dict()
        try:
            dados = validar_leitura(dados)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        session.execute("""
            UPDATE sensor_readings SET tipo=%s, temperatura=%s, umidade=%s, pressao=%s
            WHERE sensor_id=%s AND timestamp=%s
        """, (dados["tipo"], dados["temperatura"], dados["umidade"], dados["pressao"],
              UUID(dados["sensor_id"]), dados["timestamp"]))
        return redirect(url_for('home'))

    @bp.route("/leituras/delete", methods=["POST"])
    def deletar_leitura():
        sensor_id = request.form.get("sensor_id")
        timestamp = request.form.get("timestamp")
        try:
            sensor_id = UUID(sensor_id)
            timestamp = datetime.fromisoformat(timestamp)
        except Exception as e:
            return jsonify({"erro": str(e)}), 400

        session.execute("""
            DELETE FROM sensor_readings WHERE sensor_id=%s AND timestamp=%s
        """, (sensor_id, timestamp))
        return redirect(url_for('home'))

    @bp.route("/leituras/ultima/<sensor_id>")
    def ultima(sensor_id):
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s LIMIT 1
        """, (sensor_id,))
        return jsonify([dict(row._asdict()) for row in rows])

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
        return jsonify([dict(row._asdict()) for row in rows])

    @bp.route("/leituras/limite", methods=["GET"])
    def leituras_limite():
        sensor_id = request.args.get("sensor_id")
        limite = float(request.args.get("limite", 0))
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s AND temperatura > %s ALLOW FILTERING
        """, (sensor_id, limite))
        return jsonify([dict(row._asdict()) for row in rows])

    @bp.route("/sensores", methods=["GET"])
    def listar_sensores():
        rows = session.execute("SELECT DISTINCT sensor_id FROM sensor_readings")
        sensores = [str(row.sensor_id) for row in rows]
        return jsonify(sensores)

    @bp.route("/leituras/alertas", methods=["GET"])
    def alertas():
        sensor_id = request.args.get("sensor_id")
        try:
            sensor_id = UUID(sensor_id)
        except Exception:
            return jsonify([])
        limite = float(request.args.get("limite", 80.0))
        agora = datetime.utcnow()
        ontem = agora - timedelta(days=1)
        rows = session.execute("""
            SELECT * FROM sensor_readings WHERE sensor_id=%s AND timestamp >= %s AND temperatura > %s ALLOW FILTERING
        """, (sensor_id, ontem, limite))
        return jsonify([dict(row._asdict()) for row in rows])

    return bp