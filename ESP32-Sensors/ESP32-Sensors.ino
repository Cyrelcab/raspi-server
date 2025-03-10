#include <DHT.h>

#define DHTPIN 14       // DHT11 Data pin
#define DHTTYPE DHT11  // Sensor type
DHT dht(DHTPIN, DHTTYPE);

#define TRIG_PIN 12  // Ultrasonic Sensor TRIG
#define ECHO_PIN 13 // Ultrasonic Sensor ECHO

#define FLOW_SENSOR_PIN 15 // Flow Sensor signal pin
volatile int pulseCount = 0;
float flowRate = 0.0;

void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  // DHT11 Sensor
  dht.begin();

  // Ultrasonic Sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Flow Sensor
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, FALLING);
}

void loop() {
  // Read DHT11
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  Serial.print("Temp: ");
  Serial.print(temperature);
  Serial.print("°C, Humidity: ");
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
  
  // Reset pulse count every second
  pulseCount = 0;
  delay(5000);
}
