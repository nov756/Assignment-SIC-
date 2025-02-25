import network
import urequests
import time
import dht
from machine import Pin, ADC

# Konfigurasi WiFi
SSID = "SBSN"
PASSWORD = "*#aulaSBSN#"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-GcWaexarM2FcQHMu9oVYcDTKSpEMpR"
DEVICE_LABEL = "cetta-ganteng"
UBIDOTS_URL = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

# Konfigurasi Flask Server
FLASK_URL = "http://192.168.9.20:5000/receive_data"  # Sesuaikan dengan IP Flask

# Inisialisasi Sensor DHT11
sensor_dht = dht.DHT11(Pin(27))  # DHT11 di GPIO4

# Inisialisasi Sensor MQ135
mq135 = ADC(Pin(34))  # MQ135 di GPIO35 (hanya pin ADC)
mq135.atten(ADC.ATTN_11DB)  # Baca rentang 0-3.3V

# Koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        time.sleep(1)
    print("Terhubung ke WiFi:", wlan.ifconfig())

# Kirim data ke Ubidots
def send_to_ubidots(temp, humidity, gas):
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": UBIDOTS_TOKEN
    }
    data = {
        "temperature": {"value": temp},
        "humidity": {"value": humidity},
        "gas": {"value": gas}
    }
    response = urequests.post(UBIDOTS_URL, json=data, headers=headers)
    print("Response Ubidots:", response.text)
    response.close()

# Kirim data ke Flask
def send_to_flask(temp, humidity, gas):
    headers = {"Content-Type": "application/json"}
    data = {
        "temperature": temp,
        "humidity": humidity,
        "gas": gas
    }
    try:
        response = urequests.post(FLASK_URL, json=data, headers=headers)
        print("Response Flask:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim data ke Flask:", e)

# Main loop
connect_wifi()
while True:
    try:
        # Baca sensor DHT11
        sensor_dht.measure()
        temp = sensor_dht.temperature()
        humidity = sensor_dht.humidity()

        # Baca sensor MQ135
        gas_value = mq135.read()  # Baca nilai ADC (0-4095)
        gas_voltage = gas_value * (3.3 / 4095)  # Konversi ke voltase

        print(f"Suhu: {temp}°C | Kelembapan: {humidity}% | Gas: {gas_value} ({gas_voltage:.2f}V)")

        # Kirim ke Ubidots & Flask
        send_to_ubidots(temp, humidity, gas_value)
        send_to_flask(temp, humidity, gas_value)

    except Exception as e:
        print("Error:", e)
    
    time.sleep(10)  # Kirim data setiap 10 detik