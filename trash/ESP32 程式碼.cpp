#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>

// ---- 設定你的 Wi-Fi ----
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 建立伺服器，監聽 Port 80
AsyncWebServer server(80);

// 模擬感測器數據
float getSensorValue() {
  return random(200, 800) / 10.0;  // 模擬 20.0 ~ 80.0 的數值
}

void setup() {
  Serial.begin(115200);

  // 連接 Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());  // <-- 記住這個 IP，RPi 需要用到

  // ---- 路由設定 ----

  // GET /data -> 回傳 JSON 感測器數據
  server.on("/data", HTTP_GET, [](AsyncWebServerRequest *request) {
    StaticJsonDocument<128> doc;
    doc["device"]      = "ESP32";
    doc["temperature"] = getSensorValue();
    doc["status"]      = "ok";

    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });

  // POST /command -> 接收 RPi 發來的指令
  server.on("/command", HTTP_POST, 
    [](AsyncWebServerRequest *request) {},
    NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
      StaticJsonDocument<128> doc;
      DeserializationError error = deserializeJson(doc, data, len);

      if (error) {
        request->send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
        return;
      }

      const char* cmd = doc["command"];
      Serial.print("Received command from RPi: ");
      Serial.println(cmd);

      // 根據指令執行動作（可自行擴充）
      if (strcmp(cmd, "LED_ON") == 0) {
        digitalWrite(2, HIGH);  // 假設 LED 接在 GPIO 2
        request->send(200, "application/json", "{\"result\":\"LED turned ON\"}");
      } else if (strcmp(cmd, "LED_OFF") == 0) {
        digitalWrite(2, LOW);
        request->send(200, "application/json", "{\"result\":\"LED turned OFF\"}");
      } else {
        request->send(200, "application/json", "{\"result\":\"Unknown command\"}");
      }
    }
  );

  // 啟動伺服器
  server.begin();
  Serial.println("Server started.");
  pinMode(2, OUTPUT);
}

void loop() {
  // 非同步伺服器不需要在 loop 做任何事
}
