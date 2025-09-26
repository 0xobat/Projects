#include <HardwareSerial.h>
#include <TinyGPS++.h>

#define RXPin 16
#define TXPin 17
#define GPSBaud 9600

HardwareSerial gpsSerial(1);
TinyGPSPlus gps;

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);
}

void loop() {
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      double latitude, longitude;
      unsigned long age;
      latitude = gps.location.lat();
      longitude = gps.location.lng();
      age = gps.location.age();

      Serial.print("Latitude: ");
      Serial.print(latitude, 6);
      Serial.print(", Longitude: ");
      Serial.print(longitude, 6);
      Serial.print(", Age: ");
      Serial.println(age);
    }
  }
}
