import network
import machine as m
import urequests
import time
import dht
import json
from machine import Pin, ADC

# Konfigurasi WiFi
SSID = "SBSN"
PASSWORD = "*#aulaSBSN#"
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

def connect_wifi():
    """Fungsi untuk menyambungkan ke WiFi."""
    if not sta_if.isconnected():
        print("Menghubungkan ke WiFi...")
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)
            print("Menunggu koneksi WiFi...")
    print("Terhubung ke WiFi:", sta_if.ifconfig())

# Konfigurasi Server Flask
SERVER_URL = " http://192.168.9.20:5000/kirim_data" 

# Konfigurasi Ubidots
TOKEN = "BBUS-GcWaexarM2FcQHMu9oVYcDTKSpEMpR"
DEVICE_LABEL = "cetta-ganteng"
VARIABLE_LABEL_TEMP = "temperature"
VARIABLE_LABEL_HUM = "humidity"
VARIABLE_LABEL_GAS = "gas"

# Inisialisasi sensor DHT11
sensor_dht = dht.DHT11(Pin(27))

# Inisialisasi sensor MQ135 (Gas Sensor) - Gunakan ADC untuk pin analog
sensor_mq135 = ADC(Pin(34))  # Pin 34 adalah pin ADC pada ESP32

# Mengatur rentang pembacaan ADC (0-4095)
sensor_mq135.atten(ADC.ATTN_0DB)  # Pengaturan untuk rentang 0-3.3V

def send_to_flask(temp, hum, gas):
    """Mengirim data ke server Flask."""
    payload = json.dumps({
        "temperature": temp,
        "humidity": hum,
        "gas": "Detected" if gas > 1000 else "Not Detected"  # Deteksi berdasarkan nilai sensor
    })
    headers = {"Content-Type": "application/json"}
    
    try:
        print("[Flask] Mengirim data ke server Flask...")
        response = urequests.post(SERVER_URL, data=payload, headers=headers)
        print("[Flask] Status Code:", response.status_code)
        print("[Flask] Response:", response.text)
        response.close()
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Flask:", e)

def send_to_ubidots(temp, hum, gas):
    """Mengirim data ke Ubidots."""
    if temp is None or hum is None or gas is None:
        print("[ERROR] Invalid data detected, not sending to Ubidots.")
        return
    
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    payload = {
        VARIABLE_LABEL_TEMP: temp,
        VARIABLE_LABEL_HUM: hum,
        VARIABLE_LABEL_GAS: "Detected" if gas > 1000 else "Not Detected"
    }
    
    try:
        print("[Ubidots] Mengirim data ke Ubidots...")
        response = urequests.post(url, headers=headers, json=payload)
        print("[Ubidots] Status Code:", response.status_code)
        print("[Ubidots] Response:", response.text)
        response.close()
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Ubidots:", e)

def main():
    connect_wifi()
    while True:
        try:
            # Membaca data dari sensor DHT11
            sensor_dht.measure()
            temp = sensor_dht.temperature()
            hum = sensor_dht.humidity()

            # Membaca data dari sensor MQ135
            gas = sensor_mq135.read()  # Membaca nilai analog dari sensor MQ135
            
            print("====================")
            print(f"Temperature: {temp}°C")
            print(f"Kelembapan: {hum}%")
            print(f"Gas: {'Detected' if gas > 1000 else 'Not Detected'}")
            print("====================")
            
            # Kirim data ke Flask dan Ubidots
            send_to_flask(temp, hum, gas)
            send_to_ubidots(temp, hum, gas)

        except OSError:
            print("[ERROR] Gagal membaca sensor.")
        
        time.sleep(2)  # Kirim data setiap 2 detik

if __name__ == '__main__':
    main()

