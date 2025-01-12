#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Ініціалізація датчиків
const int phPin = 34; 
const int tempPin = 4; 

const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0; 
const int daylightOffset_sec = 0; 

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Підключення до Wi-Fi...");
  }
  Serial.println("Wi-Fi підключено!");

  // Синхронізація з NTP-сервером
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

String getCurrentTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Помилка отримання часу");
    return "1970-01-01 00:00:00"; // Значення за замовчуванням
  }
  char timeString[20];
  strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(timeString);
}

void loop() {
  // Зчитування даних з датчиків
  int phValue = analogRead(phPin); 
  float tempValue = analogRead(tempPin); 

  String measuredAt = getCurrentTime();
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;
    String url = "http://df07-188-163-52-19.ngrok-free.app/measurements";
    http.begin(client, url);

    http.addHeader("Content-Type", "application/json");
    
    String jsonData = "{\"station_id\": 2, \"parameter_id\": 1, \"value\": " + String(phValue) + ", \"measured_at\": \"" + measuredAt + "\"}";
    int httpResponseCode = http.POST(jsonData);

    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    String response = http.getString();
    Serial.println("Response: ");
    Serial.println(response);

    if (httpResponseCode > 0) {
      Serial.println("Дані відправлено!");
    } else {
      Serial.println("Помилка відправки даних");
    }

    http.end();
  }

  delay(300000); // Затримка між вимірюваннями
}


