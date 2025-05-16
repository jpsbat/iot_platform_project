from flask import Flask, render_template, request # type: ignore
from cassandra.cluster import Cluster # type: ignore
from routes.leituras import registrar_rotas

app = Flask(__name__)
cluster = Cluster(['cassandra'])
session = cluster.connect('fintech')

app.register_blueprint(registrar_rotas(session))

@app.route("/visualizar")
def visualizar():
    sensor_id = request.args.get("sensor_id")
    leituras = []

    if sensor_id:
        try:
            from uuid import UUID
            sensor_id = UUID(sensor_id)
            rows = session.execute("SELECT * FROM sensor_readings WHERE sensor_id = %s LIMIT 10", (sensor_id,))
            leituras = list(rows)
        except:
            pass

    return render_template("index.html", leituras=leituras)

@app.route("/")
def home():
    return render_template("index.html", leituras=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
