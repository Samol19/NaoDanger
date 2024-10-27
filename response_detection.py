from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta para recibir la señal de detección de pose
@app.route('/pose-detected', methods=['POST'])
def pose_detected():
    global pose_detected_status, last_timestamp  # Usar las variables globales
    try:
        # Obtener el valor enviado desde la solicitud
        data = request.get_json()
        pose_detected_status = data.get('pose_detected')
        last_timestamp = data.get('timestamp')

        # Imprimir el valor recibido
        if pose_detected_status == 1:
            print("Pose detectada: ambos brazos levantados.")
            print("Timestamp: ", last_timestamp)
        elif pose_detected_status == 2:
            print("Objeto detectado: cuchillo detectado.")
            print("Timestamp: ", last_timestamp)
        else:
            print("Pose no detectada.")

        # Respuesta al cliente
        return jsonify({"status": "success", "message": "Pose recibida"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Error al procesar la solicitud"}), 400

    
# Ruta para obtener el estado de la pose detectada
@app.route('/pose-detected', methods=['GET'])
def get_pose_status():
    return jsonify({
        "pose_detected": pose_detected_status,
        "timestamp": last_timestamp
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)