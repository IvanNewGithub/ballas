import json

import requests
import time
from datetime import datetime


def all_status():
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata"
    mydictState = {}
    req = requests.get(url, headers=headers).json()
    for item in req['states']:
        mydictState[item['name']] = {}
        mydictState[item['name']]['meta'] = item['meta']

    return mydictState


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


def hours7(city, url, headers, params):  # Для саратова и балаково
    for offset in range(0, 1000, 100):
        state = "Доставлен (Без СМС)"
        req = requests.get(url, headers=headers, params=params)
        data = req.json()
        for zakaz in data['rows']:
            if zakaz['organization']['name'] in city:
                print(status(zakaz, state))
        if data['rows'] < 100:
            break


def main(url, headers, params):
    time_city = {
        7: ('саратов', 'балаково'),
        8: ('воронеж', 'липецк')

    }
    while True:
        current_time = datetime.now().time()  # текущее время
        # current_time_msk = datetime.now().time()  # текущее время

        if current_time.hour == 8 and current_time.minute == 0:
            print("Время 8ч, выполняю задачу", f"-[{current_time}]-")
            hours7(time_city[7], url, headers, params)
            time.sleep(60)

        if current_time.hour == 7 and current_time.minute == 0:
            print("Время 9ч, выполняю задачу", f"-[{current_time}]-")
            hours7(time_city[8], url, headers, params)
            time.sleep(60)

        if not current_time.hour in time_city and current_time.minute == 0:
            print("Начало часа, отписываюсь, время -", current_time)

        time.sleep(20)  # пауза в 20 секунд между проверками


if __name__ == '__main__':
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
    main(url, headers, params)  # запуск основной функции
