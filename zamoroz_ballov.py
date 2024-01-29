import json

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
def status(zakaz, state):
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    data2 = {
        "state": {
            all_status()[state]
        }}
    url2 = f"https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}"
    a3 = requests.put(url2, headers=headers2, json=data2)
    time.sleep(0.1)
    return a3.status_code

def hours7(): # Для саратова и балаково
    for offset in range(0, 1000, 100):
        state = "Доставлен (Без СМС)"
        req = requests.get(url, headers=headers, params=params)
        data = req.json()
        for zakaz in data['rows']:
            if "саратов" in zakaz['organization']['name'] or "балаково" in zakaz['organization']['name']:
                print(status(zakaz, state))
        if data['rows'] < 100:
            break

def hours8(): # Для липецка и Воронежа
    pass

def main():
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

def all_status():
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata"
    mydictState = {}
    req = requests.get(url, headers=headers).json()
    for item in req['states']:

        print(item['name'])
        mydictState[item['name']] = {}
        mydictState[item['name']]['meta'] = item['meta']

    return mydictState

