import os
from flask import Flask
from flask_mqtt import Mqtt
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
from flask_pymongo import PyMongo
from uuid import uuid4
import json

# Load environment variables from .env file
load_dotenv()

# Inisiasi Flask app dan Mqtt
app = Flask(__name__)
csrf = CSRFProtect(app)

# Konfigurasi koneksi MQTT
app.config['MQTT_BROKER_URL'] = os.getenv("MQTT_BROKER_URL")
app.config['MQTT_BROKER_PORT'] = int(os.getenv("MQTT_BROKER_PORT"))
app.config['MQTT_USERNAME'] = os.getenv("MQTT_USERNAME")
app.config['MQTT_PASSWORD'] = os.getenv("MQTT_PASSWORD")
app.config['MQTT_KEEPALIVE'] = int(os.getenv("MQTT_KEEPALIVE"))
# app.config['MQTT_TLS_ENABLED'] = False
topic = os.getenv("TOPIC")

# Config for connect MongoDB
app.config['MONGO_URI'] = os.getenv("MONGO_URI")
# Inisialisasi library database
mongo = PyMongo(app)

# Inisialisasi function mqtt
mqtt = Mqtt()
mqtt.init_app(app)
csrf.init_app(app)


# Membuat Koneksi Ke MQTT
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Koneksi Berhasil')
       mqtt.subscribe(topic) # subscribe topic
   else:
       print('Koneksi Gagal. Code:', rc)

# Mengambil Pesan/Subscribe data dari Mqtt
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = json.loads(message.payload)
    print(data)
    # Memasukan data dari MQTT ke MongoDB
    with app.app_context():
        mongo.db.monitoring_data.insert_one({
            "id" : str(uuid4()),
            "device_serial" : data.get("device_serial"),
            "created_at" : datetime.now(),
            "updated_at" : datetime.now(),
            "value" : float(data.get("value"))
        })
        print("Status : Data monitoring berhasil ditambahkan!")

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)


