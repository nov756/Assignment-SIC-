from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB Atlas
MONGO_URI = "mongodb+srv://nadin8258:ezW1Q5AU1DZARM59@cluster0.i7o4s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Inisialisasi koneksi ke MongoDB
client = MongoClient(MONGO_URI)

# Pilih database
db = client["data_sensor"]

# Koleksi untuk sensor DHT11 dan MQ135
collection_one = db["data_collect_inov"]

# Endpoint untuk menerima data dari ESP32
@app.route('/receive_data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Memisahkan data berdasarkan jenis sensor
        if 'temperature' in data and 'humidity' in data and 'gas' in data:
            # Simpan data DHT11
            result = collection_one.insert_one(data)
            return jsonify({"message": "Data Stored Successfullys", "id": str(result.inserted_id)}), 201
        
        else:
            return jsonify({"error": "Invalid data format"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
