#include <SoftwareSerial.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// The serial connection to the GPS module
SoftwareSerial ss(1,0);//16, 17);


#define RXPin 1//16  // Connected to GPS
#define TXPin 0//17  // Connected to GPS
#define GPSBaud 9600


HardwareSerial gpsSerial(1);
TinyGPSPlus gps;

void setup(){
  Serial.begin(9600);
  ss.begin(9600);

  // Initialize the gps communication
  gpsSerial.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);
}

void loop(){
  
  while (ss.available() > 0){
    //get the byte data from the GPS
    byte gpsData = ss.read();
    Serial.write(gpsData);    
  }
  
/*
  // Read GPS data
  if (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
        double latitude, longitude;
        unsigned long age;
        latitude = gps.location.lat();
        longitude = gps.location.lng();
        age = gps.location.age();

        Serial.print("Latitude: "); Serial.println(latitude);
        Serial.print("Longitude: "); Serial.println(longitude);
        Serial.print("Age: "); Serial.println(age);
    }
  }

  */
}
