import os
from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
import time
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

# Config for connect DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
# Inisialisasi library database
db = SQLAlchemy(app)

# Inisialisasi function mqtt
mqtt = Mqtt()
mqtt.init_app(app)
csrf.init_app(app)

# Membuat Class Model Database
class MonitoringData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_serial = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    value = db.Column(db.Float)

    def __init__(self, device_serial, created_at, updated_at, value):
        self.device_serial = device_serial
        self.created_at = created_at
        self.updated_at = updated_at
        self.value = value

# Membuat Koneksi Ke MQTT
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)

# Mengambil Pesan/Subscribe data dari Mqtt
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = json.loads(message.payload)
    print(data)
    # Memasukan data dari MQTT ke database
    with app.app_context():
        insertData = MonitoringData(data.get("device_serial"), datetime.now(), datetime.now(), data.get("value"))
        db.session.add(insertData)
        db.session.commit()
        print("Status : Data monitoring berhasil ditambahkan!")

if __name__ == '__main__':
    # Memsatikan table pada database ada
    with app.app_context():
        db.create_all()
    # Run the Flask app
    app.run(debug=True)


