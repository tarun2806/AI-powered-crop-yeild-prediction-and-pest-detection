#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Configuration
const char* mqtt_server = "YOUR_MQTT_BROKER_IP"; // e.g., 192.168.1.10
const int mqtt_port = 1883;
const char* mqtt_topic = "farm/sensors/data";

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor Pins
const int moisturePin = 34; // Capacitive Soil Moisture Sensor
const int tempPin = 35;     // DHT22 or LM35

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_Agro_Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(500);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read Sensors
  float temperature = analogRead(tempPin) * (3.3 / 4095.0) * 100; // Simplified for LM35
  int moistureRaw = analogRead(moisturePin);
  float moisturePercent = map(moistureRaw, 4095, 0, 0, 100);

  // Create JSON Data
  StaticJsonDocument<200> doc;
  doc["farm_id"] = "FARM-001"; // Unique identifier for the farm
  doc["temperature"] = temperature;
  doc["humidity"] = 65.0; // Simulated or read from DHT
  doc["soil_moisture"] = moisturePercent;
  doc["ph_level"] = 6.5;

  char buffer[256];
  serializeJson(doc, buffer);

  // Publish
  Serial.print("Publishing data: ");
  Serial.println(buffer);
  client.publish(mqtt_topic, buffer);

  delay(60000); // Publish every 1 minute
}
