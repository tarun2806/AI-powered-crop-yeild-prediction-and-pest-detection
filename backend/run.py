from app import create_app, db
from flask_migrate import Migrate
from app.services.mqtt_service import start_mqtt_listener

app = create_app()
migrate = Migrate(app, db)

# 📡 Start MQTT IoT Listener in background
start_mqtt_listener(app)


if __name__ == '__main__':

    app.run(debug=True)
