#define LED_PIN LED_BUILTIN
#define MICROSECONDS(SECONDS) (SECONDS * 1E6)
#define SEED 1759

volatile uint8_t led_state = 0;

typedef struct {
  uint8_t dev_id;
  uint32_t counter;
  float latitude;
  float longitude;
  float altitude;
  float temperature;
  float humidity;
  float pressure;
} data_t;

data_t data = { 0 };

void setup() {
  pinMode(LED_PIN, OUTPUT);
  randomSeed(SEED);
  Serial.begin(115200);
}

void loop() {
  uart_tx();
  delay(750);
}

void uart_tx() {
  String packet;
  packet.reserve(100);
  ++data.counter;
  data.latitude = 13.f + (float)random(-5000, 5000) / 100000;
  data.longitude = 100.f + (float)random(-5000, 5000) / 100000;
  data.altitude += (float)random(-10, 100) / 10;

  data.temperature = 25.f + (float)random(-50, 50) / 10;
  data.humidity = 50.f + (float)random(-50, 50) / 10;
  data.pressure = 1013.25f - (float)random(40, 100) / 10;

  packet += "DEV" + String(data.dev_id) + ",";
  packet += String(data.counter) + ",";
  packet += String(data.latitude, 6) + ",";
  packet += String(data.longitude, 6) + ",";
  packet += String(data.altitude, 2) + ",";
  packet += String(data.temperature, 2) + ",";
  packet += String(data.humidity, 2) + ",";
  packet += String(data.pressure, 2) + "\n";

  Serial.print(packet);
  digitalWrite(LED_PIN, led_state ^= 1);
}
