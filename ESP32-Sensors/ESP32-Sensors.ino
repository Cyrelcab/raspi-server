#include <DHT.h>

#define DHTPIN 14       // DHT11 Data pin
#define DHTTYPE DHT11  // Sensor type
DHT dht(DHTPIN, DHTTYPE);

#define TRIG_PIN 12  // Ultrasonic Sensor TRIG
#define ECHO_PIN 13 // Ultrasonic Sensor ECHO

#define FLOW_SENSOR_PIN 15 // Flow Sensor signal pin
volatile int pulseCount = 0;
float flowRate = 0.0;

// GSM Module (Use Hardware Serial)
#define TX_PIN 16  // ESP32 TX connected to SIM900A RX
#define RX_PIN 17  // ESP32 RX connected to SIM900A TX
HardwareSerial sim900(1);

void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);
  sim900.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);  // Initialize SIM900A on Serial1

  // DHT11 Sensor
  dht.begin();

  // Ultrasonic Sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Flow Sensor
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, FALLING);

  delay(1000);
  Serial.println("Initializing GSM Module...");
  sim900.println("AT");
  delay(1000);
  sim900.println("AT+CMGF=1");  // Set SMS mode to text
  delay(1000);
}

void sendSMS(float humidity, float distance, float flowRate) {
  sim900.println("AT+CMGS=\"+1234567890\""); // Replace with actual recipient's number
  delay(1000);
  sim900.print("Humidity: ");
  sim900.print(humidity);
  sim900.print("%\nDistance: ");
  sim900.print(distance);
  sim900.print(" cm\nFlow Rate: ");
  sim900.print(flowRate);
  sim900.print(" L/min");
  delay(100);
  sim900.write(26);  // End SMS with CTRL+Z
  delay(5000);
}

void loop() {
  // Read Humidity from DHT11
  float humidity = dht.readHumidity();
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println("%");

  // Read Ultrasonic Sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2;
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Calculate Flow Rate
  flowRate = (pulseCount / 7.5);  // Convert pulses to liters per minute
  Serial.print("Flow Rate: ");
  Serial.print(flowRate);
  Serial.println(" L/min");

  // Send SMS with sensor data
  sendSMS(humidity, distance, flowRate);

  // Reset pulse count every cycle
  pulseCount = 0;
  delay(5000);
}
