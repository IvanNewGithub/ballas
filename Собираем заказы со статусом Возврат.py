import json
import requests as r
import re
from phonemask import phone_check
import time
from datetime import datetime, timedelta

headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
}


def search_salereturn():
    headers = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    result = {}
    for offset in range(0,700,100):
        params = {
            "limit": 100,
            "offset": offset,
            "filter": f"moment>2023-01-11 12:00:00;",
            'expand': 'demand,positions.assortment,agent'
        }

        url = "https://api.moysklad.ru/api/remap/1.2/entity/salesreturn"
        data = r.get(url, headers=headers, params=params).json()
        # with open('File/return_sale.json', 'w') as j:
        #     json.dump(data, j, ensure_ascii=False, indent=4)
        for x in data['rows']:
            # print(x['phone'])
            try:
                id_zakaz = x['demand']['customerOrder']['meta']['href'].split('/')[-1]
                phone = phone_check(x['agent']['phone'])
                if phone not in result and phone != 0:
                    result[phone] = {}
                if id_zakaz not in result[phone]:
                    result[phone][id_zakaz] = []
                for j in x['positions']['rows']:
                    result[phone][id_zakaz].append(j['assortment']['externalCode'])
                    # result[x['agent']['phone']]['Внешний код товара'][j['assortment']['externalCode']] = j['things']
            except:
                pass

    with open('File/salereturn.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)
    # print(r1, r1.text)


class product:
    def __init__(self, city, state, offset):
        self.city = city
        self.url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
        self.state = state
        self.offset = offset
        self.params = {
            "limit": 100,
            "offset": self.offset,
            "filter": f"state.name=Выполнен;moment>2023-01-01 12:00:00;",
            "expand": "agent, positions.assortment"
        }

    def result(self):
        req = r.get(self.url, headers=headers, params=self.params)
        data = req.json()
        return data

def main_2():
    time_city = {19: ('саратов', 'балаково'), 20: ('воронеж', 'липецк')}
    all_city = list(j for n in time_city.values() for j in n)
    result = {}
    start_time = datetime.now()
    current = 0
    for offset in range(0, 40000, 100):
        data = product(all_city, 'Доставлен', offset).result()
        for item in data['rows']:
            try:
                name = phone_check(item['agent']['phone'])
                if name not in result and name != 0:
                    result[name] = {} # Создали ключ с именем ID контрагента
                # теперь надо добавить ключ с id заказа
                if item['id'] not in result[name]:
                    result[name][item['id']] = {}
                    result[name][item['id']]['Дата заказа'] = item['created']
                # Добавляем товары из сделки
                for assortment in item['positions']['rows']:
                    externalCode = assortment['assortment']['externalCode']
                    if externalCode not in result[name][item['id']]:
                        result[name][item['id']][externalCode] = {}
                    result[name][item['id']][externalCode]['Цена'] = (assortment['price'])
                    result[name][item['id']][externalCode]['Скидка'] = (assortment['discount'])
                for balls in item['attributes']:
                    if balls['name'] == 'Оплачено бонусами':
                        result[name][item['id']]['Оплачено бонусами'] = balls['value']
            except:
                pass

        if len(data['rows']) < 100:
            break

    print('Готово')
    print(datetime.now() - start_time)
    with open('./File/result.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)


main_2()
# search_salereturn()