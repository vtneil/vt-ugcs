#define LED_PIN LED_BUILTIN

volatile bool led_state = false;

IntervalTimer tim1;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  tim1.begin(fn, (int)1E6);
}

void loop() {
  // put your main code here, to run repeatedly:
}

void fn() {
  if (led_state) {
    digitalWrite(LED_PIN, LOW);
    String s = "DEV0,1,2,3,4,5,6,7,8\n";
    Serial.print(s);
  } else {
    digitalWrite(LED_PIN, HIGH);
  }
  led_state ^= 1;
}
