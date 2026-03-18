import paho.mqtt.client as mqtt
import json
import os
from datetime import datetime
from ..models import db, SensorData
from datetime import datetime
from ..models import db, SensorData


# MQTT Constants
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = "farm/sensors/data"

def on_connect(client, userdata, flags, rc):
    print(f"📡 MQTT Subscriber connected with code: {rc}")
    client.subscribe(MQTT_TOPIC)

_app_ref = None

def on_message(client, userdata, msg):
    """
    Handles incoming MQTT payload with Anomaly Detection.
    """
    try:
        data = json.loads(msg.payload.decode())
        farm_id = data.get('farm_id')
        moisture = data.get('soil_moisture')
        temperature = data.get('temperature')
        
        # 🚨 Anomaly Detection Logic
        if moisture < 15:
            print(f"⚠️ [ANOMALY] Critical drought detected at Farm {farm_id}! Moisture: {moisture}%")
        elif moisture > 85:
            print(f"⚠️ [ANOMALY] Flooding/Waterlogging detected at Farm {farm_id}! Moisture: {moisture}%")

        # Persistence to PostgreSQL
        if _app_ref:
            with _app_ref.app_context():
                new_log = SensorData(
                    farm_id=data.get('farm_id'),
                    temperature=temperature,
                    humidity=data.get('humidity'),
                    soil_moisture=moisture,
                    ph_level=data.get('ph_level')
                )
                db.session.add(new_log)
                db.session.commit()
                print(f"✅ Logged sensor data for {farm_id}")

    except Exception as e:
        print(f"❌ MQTT Service Error: {str(e)}")

def start_mqtt_listener(app):
    global _app_ref
    _app_ref = app
    print(f"🚀 Initializing MQTT Listener on {MQTT_BROKER}:{MQTT_PORT}...")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Handle Reconnection
    client.reconnect_delay_set(min_delay=1, max_delay=60)
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start() 
    except Exception as e:
        print(f"⚠️ Could not start MQTT listener: {e}")


if __name__ == "__main__":
    start_mqtt_listener()
