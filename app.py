"""API propia del grupo: expone /lenguajes y /tecnologias (mismo formato que la API del profesor)."""
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

BASE = Path(__file__).parent
DATOS = json.loads((BASE / "catalogo_local.json").read_text(encoding="utf-8"))

# Si definís API_KEY en Render, se exige el header Grupo-Access-Key (igual que la v1 del profe).
# Si no la definís, la API queda abierta (como la v0).
API_KEY = os.environ.get("API_KEY")

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)  # permite que el frontend la llame desde el navegador

PREFIJO = "/api/v1"


@app.before_request
def verificar_clave():
    if API_KEY and request.path.startswith(PREFIJO) and request.method != "OPTIONS":
        if request.headers.get("Grupo-Access-Key") != API_KEY:
            return jsonify({"error": "Clave de acceso inválida o faltante"}), 401


def buscar(lista, item_id):
    return next((x for x in lista if x["id"] == item_id), None)


@app.get("/")
def inicio():
    return jsonify({
        "api": "Catálogos del grupo",
        "endpoints": [f"{PREFIJO}/lenguajes", f"{PREFIJO}/lenguajes/<id>",
                      f"{PREFIJO}/tecnologias", f"{PREFIJO}/tecnologias/<id>",
                      f"{PREFIJO}/tecnologias?categoria=framework"],
    })


@app.get(f"{PREFIJO}/lenguajes")
def lenguajes():
    return jsonify(DATOS["lenguajes"])


@app.get(f"{PREFIJO}/lenguajes/<int:item_id>")
def lenguaje(item_id):
    item = buscar(DATOS["lenguajes"], item_id)
    return (jsonify(item), 200) if item else (jsonify({"error": "Lenguaje no encontrado"}), 404)


@app.get(f"{PREFIJO}/tecnologias")
def tecnologias():
    categoria = request.args.get("categoria")
    lista = DATOS["tecnologias"]
    if categoria:
        lista = [t for t in lista if t["categoria"].lower() == categoria.lower()]
    return jsonify(lista)


@app.get(f"{PREFIJO}/tecnologias/<int:item_id>")
def tecnologia(item_id):
    item = buscar(DATOS["tecnologias"], item_id)
    return (jsonify(item), 200) if item else (jsonify({"error": "Tecnología no encontrada"}), 404)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
