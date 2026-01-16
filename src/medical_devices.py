from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Base de datos simulada de pacientes
PATIENTS = [
    {"id": "monitor_001", "patient": "Jorge Hernandez", "room": "408", "type": "Vital Signs Monitor"},
    {"id": "pump_001", "patient": "Sofia Martinez", "room": "326", "type": "Infusion Pump", "drug": "Solucion Salina"},
    # ... (Se generarían más datos dinámicamente)
]

def generate_vitals():
    """Genera datos médicos aleatorios"""
    return {
        "bpm": random.randint(60, 100),
        "spo2": random.randint(95, 100),
        "pressure": f"{random.randint(110, 130)}/{random.randint(70, 85)}"
    }

@app.route('/device/search', methods=['GET'])
def search_device():
    query_id = request.args.get('id', '')
    
    # VULNERABILIDAD INTENCIONAL: No sanitiza la entrada
    # Si recibe una comilla simple, simula un error o volcado de base de datos
    if "'" in query_id or "OR" in query_id.upper():
        # En una app real vulnerable, esto devolvería todos los datos
        full_dump = {}
        for i in range(1, 51):
            pid = f"monitor_{i:03d}"
            full_dump[pid] = generate_vitals()
            full_dump[pid]["patient"] = random.choice(["Juan Perez", "Maria Gomez", "Luis Diaz"])
            full_dump[pid]["status"] = "Active"
            full_dump[pid]["type"] = "Vital Signs Monitor"
            
        return jsonify({"ALERT": "DATABASE COMPROMISED", "DUMP": full_dump, "TOTAL_RECORDS": len(full_dump)})

    return jsonify({"status": "secure", "message": "No results found"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)