#include <SPI.h>
#include <MFRC522.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <DHT.h>
#include "DHT.h"
#define DHTTYPE DHT11
#define SS_PIN D8
#define RST_PIN D0
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;
// Init array that will store new NUID
byte nuidPICC[4];
const int DHTPin = D4;
DHT dht(DHTPin, DHTTYPE);

//Timers auxiliar variables
long now = millis();
long lastMeasure = 0;

//const char* ssid = "MAifon";
//const char* password = "connectNow";
//const char* mqtt_server = "172.20.10.13";

const char* ssid = "VIRGIN305";
const char* password = "CAF6D225";
const char* mqtt_server = "192.168.2.85";

;


WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }

}
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP8266Client")) {
      Serial.println("connected");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(15000);
    }
  }
}
void setup() {
dht.begin();
Serial.begin(115200);
setup_wifi();
client.setServer(mqtt_server, 1883);
client.setCallback(callback);
SPI.begin(); // Init SPI bus
rfid.PCD_Init(); // Init MFRC522
Serial.println();
Serial.print(F("Reader :"));
rfid.PCD_DumpVersionToSerial();
for (byte i = 0; i < 6; i++) {
 key.keyByte[i] = 0xFF;
}

Serial.println();
Serial.println(F("This code scan the MIFARE Classic NUID."));
Serial.print(F("Using the following key:"));
printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}
void loop() {
  float pResistor = analogRead(A0);
  String dataString = String(pResistor);
  
  delay(1500);
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("ESP8266Client");
 now = millis();

 if (now - lastMeasure > 1000) {
    lastMeasure = now;

    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float f = dht.readTemperature(true);

    if (isnan(h) || isnan(t) || isnan(f)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }

    static char temperatureTemp[8];
    dtostrf(t, 6, 2, temperatureTemp);

    static char humidityTemp[8];
    dtostrf(h, 6, 2, humidityTemp);

    client.publish("/esp8266/temperature", temperatureTemp);
    client.publish("/esp8266/humidity", humidityTemp);
    
    Serial.println(pResistor);
    Serial.print("Humidity: ");
    Serial.print(h);
    Serial.print("\t Temperature: ");
    Serial.print(t);
    Serial.print(" *C ");
    Serial.print("");
  }

  static char photoresist[8];
  dtostrf(pResistor, 6, 2, photoresist);
  client.publish("/esp8266/resistor", photoresist);
  
// Reset the loop if no new card present on the sensor/reader. This saves the entire process when

if ( ! rfid.PICC_IsNewCardPresent())
 return;
// Verify if the NUID has been readed
if ( ! rfid.PICC_ReadCardSerial())
 return;
Serial.print(F("PICC type: "));
MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
Serial.println(rfid.PICC_GetTypeName(piccType));
// Check is the PICC of Classic MIFARE type
if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
 piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
 piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
 Serial.println(F("Your tag is not of type MIFARE Classic."));
 return;
}

 Serial.println(F("A new card has been detected."));
 // Store NUID into nuidPICC array
 for (byte i = 0; i < 4; i++) {
 nuidPICC[i] = rfid.uid.uidByte[i];
 }
 Serial.println(F("The NUID tag is:"));
 Serial.print(F("In hex: "));
 String hex = printHex(rfid.uid.uidByte, rfid.uid.size);
 Serial.print(hex);
 Serial.println();
 Serial.print(F("In dec: "));
 printDec(rfid.uid.uidByte, rfid.uid.size);
/// Serial.print("the hex" + hexo);
 static char tagnum[14];
// Halt PICC
rfid.PICC_HaltA();
// Stop encryption on PCD
rfid.PCD_StopCrypto1();
if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("ESP8266Client");
 Serial.println();
hex.toCharArray(tagnum, 14);
client.publish("/esp8266/data", tagnum);
delay(5000);
}
/**
 Helper routine to dump a byte array as hex values to Serial.
*/
String printHex(byte *buffer, byte bufferSize) {
String tagnum;
for (byte i = 0; i < bufferSize; i++) {
String space = (buffer[i] < 0x10 ? " 0" : " ");
String hexo = String(buffer[i], HEX);
tagnum += space;
tagnum += hexo;
}
return tagnum;
}
/**
 Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte *buffer, byte bufferSize) {
for (byte i = 0; i < bufferSize; i++) {
 Serial.print(buffer[i] < 0x10 ? " 0" : " ");
 Serial.print(buffer[i], DEC);
}
}
