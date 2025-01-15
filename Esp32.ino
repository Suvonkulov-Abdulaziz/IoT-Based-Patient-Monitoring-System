#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <MAX30105.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// WiFi credentials
const char* ssid = "STAFF";
const char* password = "furor48VDTs";

// Django API endpoint
const char* serverURL = "http://100.40.1.232:8000/api/endpoint/";

// MAX30102 Setup
MAX30105 particleSensor;
long lastBeat = 0;
float beatsPerMinute;
int beatCount = 0;

// DHT11 Setup
#define DHTPIN 5
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// DS18B20 Setup
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  // Serial communication
  Serial.begin(115200);
  while (!Serial);

  // Connect to WiFi
  connectToWiFi();

  // MAX30102 Initialization
  if (!particleSensor.begin()) {
    Serial.println("MAX30102 not detected. Check connections.");
    while (1);
  }
  particleSensor.setup(); // Default settings
  Serial.println("MAX30102 initialized.");

  // DHT11 Initialization
  dht.begin();
  Serial.println(F("DHT11 Sensor initialized."));

  // DS18B20 Initialization
  sensors.begin();
  Serial.println("DS18B20 initialized.");
}

void loop() {
  // Read sensor data
  long red = particleSensor.getRed();
  long ir = particleSensor.getIR();
  float heartRate = 0;
  float SpO2 = 0;

  if (ir > 50000) { // Finger detected
    heartRate = calculateHeartRate(ir);
    SpO2 = calculateSpO2(red, ir);
  }

  float humidity = dht.readHumidity();
  float temperatureDHT = dht.readTemperature();
  sensors.requestTemperatures();
  float temperatureDS = sensors.getTempCByIndex(0)+6;

  // Send data to Django
  sendDataToDjango(heartRate, SpO2, humidity, temperatureDHT, temperatureDS);

  delay(500); // Send data every 5 seconds
}

// WiFi connection function
void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

// Function to send data to Django
void sendDataToDjango(float heartRate, float SpO2, float humidity, float temperatureDHT, float temperatureDS) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    // Create JSON payload
    String jsonPayload = "{\"heart_rate\": " + String(heartRate) +
                         ", \"spo2\": " + String(SpO2) +
                         ", \"humidity\": " + String(humidity) +
                         ", \"temperature_dht\": " + String(temperatureDHT) +
                         ", \"temperature_ds\": " + String(temperatureDS) + "}";

    // Send POST request
    int httpResponseCode = http.POST(jsonPayload);
          Serial.println(jsonPayload);
          Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Data sent successfully: " + response);
    } else {
      Serial.println("Error sending data: " + String(httpResponseCode));
     Serial.println(jsonPayload);
     Serial.println(httpResponseCode);

    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

// MAX30102 Functions
float calculateHeartRate(long ir) {
  static long previousIR = 0;
  static long peakTime = 0;
  static int peakDetected = 0;
  static float bpmBuffer[5] = {0};
  static int bufferIndex = 0;

  long currentTime = millis();
  float heartRate = 0;

  if (ir > previousIR && peakDetected == 0 && (currentTime - peakTime) > 300) { 
    // Peak detected and debounce
    peakTime = currentTime;
    long interval = peakTime - lastBeat; // Time since last beat
    lastBeat = peakTime;

    if (interval > 0) {
      heartRate = 60000.0 / interval; // Calculate BPM
      bpmBuffer[bufferIndex] = heartRate; // Store in buffer
      bufferIndex = (bufferIndex + 1) % 5; // Circular buffer
    }
    peakDetected = 1;
  } else if (ir < previousIR) {
    peakDetected = 0; // Reset for next peak
  }

  previousIR = ir;

  // Calculate smoothed BPM
  float sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += bpmBuffer[i];
  }
  return sum+20 ; // Average BPM
}
float calculateSpO2(long red, long ir) {
  static long redBuffer[50] = {0};
  static long irBuffer[50] = {0};
  static int bufferIndex = 0;

  // Add new readings to buffer
  redBuffer[bufferIndex] = red;
  irBuffer[bufferIndex] = ir;
  bufferIndex = (bufferIndex + 1) % 50;

  // Calculate DC (average) and AC (peak-to-peak)
  long redSum = 0, irSum = 0;
  long redMin = redBuffer[0], redMax = redBuffer[0];
  long irMin = irBuffer[0], irMax = irBuffer[0];

  for (int i = 0; i < 50; i++) {
    redSum += redBuffer[i];
    irSum += irBuffer[i];
    if (redBuffer[i] < redMin) redMin = redBuffer[i];
    if (redBuffer[i] > redMax) redMax = redBuffer[i];
    if (irBuffer[i] < irMin) irMin = irBuffer[i];
    if (irBuffer[i] > irMax) irMax = irBuffer[i];
  }

  float dcRed = redSum / 50.0;
  float dcIR = irSum / 50.0;
  float acRed = redMax - redMin;
  float acIR = irMax - irMin;

  // Calculate R ratio
  float R = (acRed / dcRed) / (acIR / dcIR);

  // Use the calibration formula for SpO2
  return (110.0 - 25.0 * R)+8; // Example formula
}



