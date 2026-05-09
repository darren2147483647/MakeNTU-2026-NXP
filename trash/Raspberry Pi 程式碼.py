import requests
import json
import time

# ---- 填入 ESP32 的 IP（從 Serial Monitor 取得）----
ESP32_IP = "192.168.x.x"
BASE_URL  = f"http://{ESP32_IP}"

def get_sensor_data():
    """向 ESP32 請求感測器數據"""
    try:
        response = requests.get(f"{BASE_URL}/data", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"[RPi] Received data from ESP32: {data}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"[RPi] Error fetching data: {e}")
        return None

def send_command(command: str):
    """向 ESP32 發送指令"""
    payload = {"command": command}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            f"{BASE_URL}/command",
            data=json.dumps(payload),
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        print(f"[RPi] ESP32 responded: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"[RPi] Error sending command: {e}")
        return None

if __name__ == "__main__":
    while True:
        # 每 3 秒抓一次感測器數據
        get_sensor_data()
        time.sleep(1)

        # 發送 LED 開關指令
        send_command("LED_ON")
        time.sleep(1)
        send_command("LED_OFF")
        time.sleep(1)
