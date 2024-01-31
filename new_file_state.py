import json
import requests
import time
from datetime import datetime, timedelta

headers = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
def connect_MS(url):
    return requests.get(url, headers=headers, timeout=120)

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

    def upgrade_state(self, sec = 20):
        for zakaz in self.all_zakaz:
            url2 = f"https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}"
            a3 = requests.put(url2, headers=headers, json=self.data)
            print(f'Изменили статус на {self.current_status} в Моем Складе с ID:', zakaz)
            time.sleep(sec)

    def search_id_WA(self):
        id = []
        for zakaz in self.all_zakaz:
            url = f'https://hatiko.ru/api.php/shop.order.search?hash=search%2Fmoyskladapi_id%3D{zakaz}&access_token=6acf9ef3e246128715d8ecaf9d7e1a83'
            id.append(requests.get(url).json()['orders'][0]['id'])
        return id

    def edit_stete_WA(self, sec = 20):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for id in self.all_zakaz:
            data = {"id": f"{id}"}
            req = requests.post('https://hatiko.ru/api.php/shop.order.complete?access_token=6acf9ef3e246128715d8ecaf9d7e1a83',
                               headers=headers, data=data)
            print(f'Отредактировали заказ в WebAsyst с ID:', id)
            time.sleep(sec)

class product:
    def __init__(self, city,  state):
        self.city = city
        self.url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
        self.state = state
        self.params = {
            "limit": 100,
            "offset": 0,
            "filter": f"state.name={self.state}" if type(self.state) == str else ';'.join(('state.name=' + n for n in state)),
            "expand": "organization"
        }
    def result(self):
        zakazi = []
        for offset in range(0, 200, 100):
            self.params['offset'] = offset
            req = requests.get(self.url, headers=headers, params=self.params)
            data = req.json()
            for zakaz in data['rows']:
                for cities in self.city:
                    if cities in zakaz['organization']['name'].lower():
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
            time.sleep(1)
            url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
            current_time = datetime.now()
            while True:
                try:
                    req = connect_MS(url)
                    if req.status_code == 200:
                        data = req.json()
                        break
                except:
                    print("заного")
                    time.sleep(3)
            # req = requests.get(url, headers=headers).json()
            for item in data['rows']:
                start_time = datetime.strptime(item['moment'], "%Y-%m-%d %H:%M:%S.%f")
                time_difference = current_time - start_time
                if 'diff' in item and 'state' in item['diff']:  # Проверяем, прошло ли более 48 часов
                    if time_difference > timedelta(hours=48):
                        result.append(zakaz)
                    break
        return result
    def result_days(self):
        result = []
        with open('id.json', 'r')as js:
            id_skip = json.load(js)
        for zakaz in self.all_zakaz:
            time.sleep(1)
            url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
            current_time = datetime.now()
            # print('Дней прошло', (current_time - datetime.strptime(id_skip.get(zakaz, current_time), "%Y-%m-%d %H:%M:%S.%f")).days)

            if zakaz in id_skip and (current_time - datetime.strptime(id_skip[zakaz], "%Y-%m-%d %H:%M:%S.%f")).days > 14:
                result.append(zakaz)
                del id_skip[zakaz]
            else:
                while True:
                    try:
                        req = connect_MS(url)
                        if req.status_code == 200:
                            data = req.json()
                            break
                    except:
                        print("заного")
                        time.sleep(3)

                for item in data['rows']:
                    start_time = datetime.strptime(item['moment'], "%Y-%m-%d %H:%M:%S.%f")
                    time_difference = current_time - start_time
                    if 'diff' in item and 'state' in item['diff']:  # Проверяем, прошло ли более 48 часов
                        if time_difference.days >= 13:
                            # print(zakaz)
                            result.append(zakaz)
                        else:
                            data = {zakaz: start_time}
                            with open('id.json', 'r') as file:
                                data = json.load(file)
                                if zakaz not in data:
                                    data[zakaz] = item['moment']
                                    with open('id.json', 'w')as j:
                                        json.dump(data, j, ensure_ascii=False, indent=4)
                            pass
                        break
        with open('id.json', 'w') as file:
            json.dump(id_skip, file, ensure_ascii=False, indent=4)
        return result


def main():
    """ Тут будет запуск и распределение по часам """
    time_city = {19: ('саратов', 'балаково'), 20: ('воронеж', 'липецк')}
    all_city = list(j for n in time_city.values() for j in n)
    while True:
        current_time = datetime.now().time()
        if current_time.minute == 13: # Тут проверяем что должны быть ровные часы
            """ Надо из этой проверки запустить и 'отмененный статус' и 'доставлен' поменять в выполнен"""
            # В зависимости от статуса конечного
            # Шаг №1 получить заказы с определенным статусом с определенным городом
            zakaz_overdue = product(all_city,  "Истек срок резерва").result() #  Находим заказы с статусом Истек срок резерва
            zakaz_dostavlen = product(all_city, ('Доставлен', 'Доставлен - клиент не доволен')).result() #  Находим заказы с статусом Доставлен и доставлен не доволен
            print('zakaz_dostavlen', 'Всего:', len(zakaz_dostavlen), '->', zakaz_dostavlen)

            # Проверяем полученные заказы, соответствуют ли они времени
            true_zakaz_overdue = watch_edit_time(zakaz_overdue).result_hours()
            true_zakaz_dostavlen = watch_edit_time(zakaz_dostavlen).result_days()

            print('true_zakaz_dostavlen', 'Всего:', len(true_zakaz_dostavlen), '->', true_zakaz_dostavlen)
            # Изменяем статусы, на те что нам нужны
            edit_state("Отменен", true_zakaz_overdue).upgrade_state()
            edit_state("Выполнен", true_zakaz_dostavlen).upgrade_state()


            """ Ищем id с Веб Асиста"""
            if true_zakaz_dostavlen:
                id_zakaz = edit_state('Выполнен', true_zakaz_dostavlen).search_id_WA()
                edit_state('Выполнен', id_zakaz).edit_stete_WA()
            else:
                print('Заказов для редактирования в Web Asyst не найдено')



            if current_time.hour in time_city:
                zakaz = product(time_city[current_time.hour],"Доставлен (Без СМС)").result()  # Находим заказы с статусом Доставлен, для определенных городов
                edit_zakaz = edit_state("Доставлен", zakaz).upgrade_state(1)

        print('Уснули на 20 секунд')
        time.sleep(20)




if __name__ == '__main__':
    main()



