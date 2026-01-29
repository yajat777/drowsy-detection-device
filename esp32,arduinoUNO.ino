#include <WiFi.h>

const char* ssid = "Aiphone";
const char* password = "987654321";

WiFiServer server(80);

int LED_PIN = 2;  // change if needed

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.println("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;

  String request = client.readStringUntil('\r');
  Serial.println(request);

  if (request.indexOf("/on") != -1) {
    digitalWrite(LED_PIN, HIGH);
  }
  if (request.indexOf("/off") != -1) {
    digitalWrite(LED_PIN, LOW);
  }

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println();
  client.println("OK");
}
