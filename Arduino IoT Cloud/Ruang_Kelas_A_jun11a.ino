#include "arduino_secrets.h"
#include <PZEM004Tv30.h>
#include "thingProperties.h"

#define device1 32
#define device2 33
#define device3 25
#define device4 26

#define button1 18
#define button2 5
#define button3 4
#define button4 2

// Gunakan HardwareSerial (misalnya Serial1)
HardwareSerial mySerial(2); // Port serial hardware 1

PZEM004Tv30 pzem(mySerial, 16, 17); // RX=16, TX=17 untuk PZEM

boolean sta1, sta2, sta3, sta4;
float totalWh = 0;  // Variabel untuk menyimpan total energi (Wh)

void setup() {
  // Initialize serial and wait for port to open:
  Serial.begin(9600);
  
  // Inisialisasi HardwareSerial (Serial1)
  mySerial.begin(9600, SERIAL_8N1, 16, 17); // 9600 baud rate, RX=16, TX=17

  pinMode(device1, OUTPUT);  // relay1
  pinMode(device2, OUTPUT);  // relay2
  pinMode(device3, OUTPUT);  // relay3
  pinMode(device4, OUTPUT);  // relay4

  pinMode(button1, INPUT);  // button1
  pinMode(button2, INPUT);  // button2
  pinMode(button3, INPUT);  // button3
  pinMode(button4, INPUT);  // button4

  // This delay gives the chance to wait for a Serial Monitor without blocking if none is found
  delay(1500);

  // Defined in thingProperties.h
  initProperties();

  // Connect to Arduino IoT Cloud
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

void loop() {
  ArduinoCloud.update(); // Update cloud variables
  
  // Baca daya (W) dari PZEM
  float power = pzem.power();

  if (!isnan(power)) {
    // Hitung energi per detik (Wh)
    totalWh += power; // Tambah totalWh berdasarkan waktu per detik
    float totalKwh = totalWh / 1000.0; // Konversi ke kWh

    // Update variabel kwh di Arduino IoT Cloud
    kwh = totalKwh;

    Serial.print("Daya: ");
    Serial.print(power);
    Serial.print(" W | Total Energi: ");
    Serial.print(totalKwh, 6);
    Serial.println(" kWh");
  } else {
    Serial.println("Gagal baca daya");
  }

  // Pengaturan button untuk perangkat relay
  if (digitalRead(button1) == 1) {
    delay(100);
    sta1 = !sta1;
    dev1 = sta1;
    delay(500);
  }

  if (digitalRead(button2) == 1) {
    delay(100);
    sta2 = !sta2;
    dev2 = sta2;
    delay(500);
  }

  if (digitalRead(button3) == 1) {
    delay(100);
    sta3 = !sta3;
    dev3 = sta3;
    delay(500);
  }

  if (digitalRead(button4) == 1) {
    delay(100);
    sta4 = !sta4;
    dev4 = sta4;
    delay(500);
  }

  // Atur status relay sesuai dengan dev1/dev2/dev3/dev4
  if (sta1) {
    digitalWrite(device1, HIGH);
  } else {
    digitalWrite(device1, LOW);
  }

  if (sta2) {
    digitalWrite(device2, HIGH);
  } else {
    digitalWrite(device2, LOW);
  }

  if (sta3) {
    digitalWrite(device3, HIGH);
  } else {
    digitalWrite(device3, LOW);
  }

  if (sta4) {
    digitalWrite(device4, HIGH);
  } else {
    digitalWrite(device4, LOW);
  }
}

// Fungsi untuk mengubah status dev1 dari Cloud
void onDev1Change() {
  if (dev1 == 1) {
    sta1 = 1;
  } else {
    sta1 = 0;
  }
  
  if (sta1) {
    digitalWrite(device1, HIGH);
  } else {
    digitalWrite(device1, LOW);
  }
}

// Fungsi untuk mengubah status dev2 dari Cloud
void onDev2Change() {
  if (dev2 == 1) {
    sta2 = 1;
  } else {
    sta2 = 0;
  }

  if (sta2) {
    digitalWrite(device2, HIGH);
  } else {
    digitalWrite(device2, LOW);
  }
}

// Fungsi untuk mengubah status dev3 dari Cloud
void onDev3Change() {
  if (dev3 == 1) {
    sta3 = 1;
  } else {
    sta3 = 0;
  }

  if (sta3) {
    digitalWrite(device3, HIGH);
  } else {
    digitalWrite(device3, LOW);
  }
}

// Fungsi untuk mengubah status dev4 dari Cloud
void onDev4Change() {
  if (dev4 == 1) {
    sta4 = 1;
  } else {
    sta4 = 0;
  }

  if (sta4) {
    digitalWrite(device4, HIGH);
  } else {
    digitalWrite(device4, LOW);
  }
}
