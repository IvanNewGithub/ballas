import json
import requests
import time
from datetime import datetime, timedelta

headers = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }

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

class edit_state:
    def __init__(self, current_status, all_zakaz):
        self.current_status = current_status
        self.all_zakaz = all_zakaz
        self.data = {"state": all_status()[current_status]}

    def upgrade_state(self, sec = 0):
        for zakaz in self.all_zakaz:
            url2 = f"https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}"
            a3 = requests.put(url2, headers=headers, json=self.data)
            time.sleep(sec)

    def search_id_WA(self):
        id = []
        for zakaz in self.all_zakaz:
            url = f'https://hatiko.ru/api.php/shop.order.search?hash=search%2Fmoyskladapi_id%{zakaz}&access_token=6acf9ef3e246128715d8ecaf9d7e1a83'
            id.append(requests.get(url).json()['orders'][0]['id'])
        return id

    def edit_stete_WA(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for id in self.all_zakaz:
            data = {"id": f"{id}"}
            req = requests.post('https://hatiko.ru/api.php/shop.order.complete?access_token=6acf9ef3e246128715d8ecaf9d7e1a83',
                               headers=headers, data=data)

class product:
    def __init__(self, city,  state):
        self.city = city
        self.url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
        self.state = state
        self.params = {
            "limit": 100,
            "offset": 0,
            "filter": f"state.name={self.state}" if self.state == type(str) else ','.join(('state.name='+ n for n in state)),
            "expand": "organization"
        }
    def result(self):
        zakazi = []
        for offset in range(0, 1000, 100):
            self.params['offset'] = offset
            req = requests.get(self.url, headers=headers, params=self.params)
            data = req.json()
            for zakaz in data['rows']:
                for cities in self.city:
                    if cities in zakaz['organization']['name'].lower():
                        print("я тут")
                        zakazi.append(zakaz['id'])
            if len(data['rows']) < 100:
                break
        return zakazi
class watch_edit_time:
    def __init__(self, all_zakaz):
        self.all_zakaz = all_zakaz
        # self.utl = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
        # pass
    def result_hours(self):
        result = []
        for zakaz in self.all_zakaz:
            url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
            current_time = datetime.now()
            req = requests.get(url, headers=headers).json()
            for item in req['rows']:
                start_time = datetime.strptime(item['moment'], "%Y-%m-%d %H:%M:%S.%f")
                time_difference = current_time - start_time
                if 'state' in item['diff']:  # Проверяем, прошло ли более 48 часов
                    if time_difference > timedelta(hours=48):
                        result.append(zakaz)
        return result
    def result_days(self):
        result = []
        for zakaz in self.all_zakaz:
            url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
            current_time = datetime.now()
            req = requests.get(url, headers=headers).json()
            for item in req['rows']:
                start_time = datetime.strptime(item['moment'], "%Y-%m-%d %H:%M:%S.%f")
                time_difference = current_time - start_time
                if 'state' in item['diff']:  # Проверяем, прошло ли более 48 часов
                    if time_difference > timedelta(days=14):
                        result.append(zakaz)
        return result


def main():
    """ Тут будет запуск и распределение по часам """
    time_city = {19: ('саратов', 'балаково'), 20: ('воронеж', 'липецк')}
    all_city = list(j for n in time_city.values() for j in n)
    while True:
        current_time = datetime.now().time()
        if current_time.minute == 0: # Тут проверяем что должны быть ровные часы
            """ Надо из этой проверки запустить и 'отмененный статус' и 'доставлен' поменять в выполнен"""
            # В зависимости от статуса конечного
            # Шаг №1 получить заказы с определенным статусом с определенным городом
            zakaz_overdue = product(all_city,  "Истек срок резерва").result() #  Находим заказы с статусом Истек срок резерва
            zakaz_dostavlen = product(all_city, ('Доставлен', 'Доставлен - клиент не доволен')).result() #  Находим заказы с статусом Доставлен и доставлен не доволен

            # Проверяем полученные заказы, соответствуют ли они времени
            true_zakaz_overdue = watch_edit_time(zakaz_overdue).result_hours()
            true_zakaz_dostavlen = watch_edit_time(zakaz_overdue).result_days()

            """ Ищем id с Веб Асиста"""
            id_zakaz = edit_state('asda', true_zakaz_dostavlen).search_id_WA()

            edit_zakaz_overdue = edit_state("Отменен", true_zakaz_overdue).upgrade_state()
            edit_zakaz_dostavlen = edit_state("Выполнен", true_zakaz_dostavlen).upgrade_state()

            if current_time.hour in time_city:
                zakaz = product(time_city[current_time.hour],"Доставлен (Без СМС)").result()  # Находим заказы с статусом Доставлен, для определенных городов
                edit_zakaz = edit_state("Доставлен", true_zakaz_dostavlen).upgrade_state(1)
        time.sleep(20)








