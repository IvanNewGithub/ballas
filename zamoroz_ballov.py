import requests
import time
from datetime import datetime

url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ==',
    "Accept-Encoding": "gzip"
    }

offset = 0
state = "Доставлен (Без СМС)"
params = {
        "limit": 100,
        "offset": offset,
        "filter": f"state.name={state}",
        "expand": "organization"
    }
def status():
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    data2 = {
        "state": {
            "meta": {
                "href": "https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/states/2a26e7a7-1471-11eb-0a80-0191000e70e1",
                "type": "state",
                "mediaType": "application/json"
            }
        }}
    url2 = f"https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}"
    a3 = requests.put(url2, headers=headers2, json=data2)
    print(a3.status_code)
    time.sleep(0.1)

def hours7(): # Для саратова и балаково
    for offset in range(0, 1000, 100):
        state = "Доставлен (Без СМС)"
        req = requests.get(url, headers=headers, params=params)
        data = req.json()
        for zakaz in data['rows']:
            if "саратов" in zakaz['organization']['name'] or "балаково" in zakaz['organization']['name']:
                pass
        if data['rows'] < 100:
            break

def hours8(): # Для липецка и Воронежа
    pass

while True:
    current_time = datetime.now().time()  # текущее время
    # current_time_msk = datetime.now().time()  # текущее время

    if current_time.hour == 8 and current_time.minute == 0:
        print("Время 8ч, выполняю задачу", f"-[{current_time}]-")
        hours7()
        time.sleep(60)

    if current_time.hour == 7 and current_time.minute == 0:
        print("Время 9ч, выполняю задачу", f"-[{current_time}]-")
        hours8()
        time.sleep(60)

    if not current_time.hour in (8, 7) and current_time.minute == 0:
        print("Начало часа, отписываюсь, время -", current_time)

    time.sleep(20)  # пауза в 20 секунд между проверками