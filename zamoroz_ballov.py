import json

import requests
import time
from datetime import datetime, timedelta

# dsfasdasdasd
# asdasdasdasdas
#
# asdasdasd
def all_status():
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata"
    mydictState = {}
    req = requests.get(url, headers=headers2).json()
    for item in req['states']:
        mydictState[item['name']] = {}
        mydictState[item['name']]['meta'] = item['meta']

    return mydictState
def edit_datetime(zakaz):
    current_time = datetime.now()
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
    req = requests.get(url, headers=headers2).json()
    for item in req['rows']:
        time_delta = start_time = datetime.strptime(item['moment'], "%Y-%m-%d %H:%M:%S.%f")
        time_difference = current_time - start_time
        # Проверяем, прошло ли более 48 часов
        if item['diff']['state']:
            if time_difference > timedelta(hours=48):
                return True
            else:
                return False

def status(zakaz,current_status):
    print("начинаем")
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    data2 = {
        "state": all_status()[current_status]
    }
    url2 = f"https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}"
    if current_status == 'Отменен':
        if edit_datetime(zakaz):
            a3 = requests.put(url2, headers=headers2, json=data2)
    else:
        a3 = requests.put(url2, headers=headers2, json=data2)
    print(a3, a3.text)
    print(zakaz)
    time.sleep(10000)
    return a3.status_code


def hours7(city, url, headers, params, current_status):  # Для саратова и балаково
    for offset in range(0, 1000, 100):
        params['offset'] = offset
        req = requests.get(url, headers=headers, params=params)
        data = req.json()
        zakazi = []
        for zakaz in data['rows']:
            for cities in city:
                if cities in zakaz['organization']['name'].lower():
                    print("я тут")
                    zakazi.append(zakaz['id'])
                    # print(status(zakaz['id']))
        for zak1 in zakazi:
            print(status(zak1, current_status))
        if len(data['rows']) < 100:
            break


def main(url, headers, params):
    time_city = {
        19: ('саратов', 'балаково'),
        20: ('воронеж', 'липецк')

    }
    while True:
        current_time = datetime.now().time()  # текущее время
        current_status = 'Доставлен'
        for time_item in time_city:
            print(current_time.hour, current_time.minute)
            if current_time.hour == time_item and current_time.minute == 0:
                print(f"Время {time_item}ч, выполняю задачу", f"-[{current_time}]-")
                hours7(time_city[time_item], url, headers, params, current_status)
                time.sleep(60)
            else:
                print("Никуя")
        if not current_time.hour in time_city and current_time.minute == 0:  #`123123
            print("Начало часа, отписываюсь, время -", current_time)
            state = "Истек срок резерва"
            params2 = params.copy()
            current_status = 'Отменен'
            params2["filter"] = f"state.name={state}"
            all_city = list(j for n in time_city.values() for j in n)
            hours7(all_city, url, headers, params2, current_status)

        time.sleep(20)  # пауза в 20 секунд между проверками

a = 1231 #1231231231232
def start_1hours(url, headers): # Перевод в Доставлен
    state = "Доставлен (Без СМС)"
    params = {
        "limit": 100,
        "offset": offset,
        "filter": f"state.name={state}",
        "expand": "organization"
    }
    main(url, headers, params)  # запуск основной функции

if __name__ == '__main__':
    url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
    headers = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ==',
        "Accept-Encoding": "gzip"
    }

    offset = 0
    start_1hours(url, headers) # Перевод в Доставлен
