#define ROLL 27
#define PITCH 14
#define THROTTLE 12
#define YAW 13 

int roll_val;
int pitch_val;
int throttle_val;
int yaw_val;


void setup() {
  Serial.begin(9600);
  pinMode(ROLL, INPUT);
  pinMode(PITCH, INPUT);
  pinMode(THROTTLE, INPUT);
  pinMode(YAW, INPUT);
}

void loop() {
  roll_val = pulseIn(ROLL, HIGH);
  Serial.print("Roll:"); Serial.println(roll_val);
  pitch_val = pulseIn(PITCH, HIGH);
  Serial.print("Pitch:"); Serial.println(pitch_val);
  throttle_val = pulseIn(THROTTLE, HIGH);
  Serial.print("Throttle:"); Serial.println(throttle_val);
  yaw_val = pulseIn(YAW, HIGH);
  Serial.print("Yaw:"); Serial.println(yaw_val);
  delay(1000);
  
}
