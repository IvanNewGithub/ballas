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

    params = {
        "limit": 100,
        "offset": 0,
        "filter": f"moment>2023-01-11 12:00:00;",
        'expand': 'demand,positions.assortment,agent'
    }

    url = "https://api.moysklad.ru/api/remap/1.2/entity/salesreturn"
    data = r.get(url, headers=headers, params=params).json()
    result = {}
    with open('File/return_sale.json', 'w') as j:
        json.dump(data, j, ensure_ascii=False, indent=4)
    for x in data['rows']:
        # print(x['phone'])
        try:
            phone = phone_check(x['agent']['phone'])
            if phone not in result and phone != 0:
                result[phone] = {}
            if x['id'] not in result[phone]:
                result[phone][x['id']] = []
            # result.setdefault(x['agent']['phone'], {})
            # result[phone].setdefault('id заказа', []).append(x['id'])
            # result[phone].setdefault('Номер заказа', []).append(x['name'])
            # result[phone]['Внешний код товара'] = []
            for j in x['positions']['rows']:
                result[phone][x['id']].append(j['assortment']['externalCode'])
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
            "offset": offset,
            # "filter": f"state.name={self.state}" if type(self.state) == str else ';'.join(('state.name=' + n for n in state)),
            "expand": "agent, positions.assortment"
        }

    def result(self):
        zakazi = []
        # for offset in range(0, 200, 100):
        #     self.params['offset'] = offset
        req = r.get(self.url, headers=headers, params=self.params)
        data = req.json()
        # for zakaz in data['rows']:
        #     for cities in self.city:
        #         if cities in zakaz['organization']['name'].lower():
        #             zakazi.append(zakaz['id'])
        # if len(data['rows']) < 100:
        #     break
        return data

def main_2():
    time_city = {19: ('саратов', 'балаково'), 20: ('воронеж', 'липецк')}
    all_city = list(j for n in time_city.values() for j in n)
    result = {}
    for offset in range(0, 500, 100):
        # with open('./File/cutomerorder.json', 'w') as j:
        #     json.dump(product(all_city, 'Доставлен').result(), j, ensure_ascii=False, indent=4)
        data = product(all_city, 'Доставлен', offset).result()

        # with open('./File/cutomerorder.json', 'w') as j:
        #     json.dump(data, j, ensure_ascii=False, indent=4)

        for item in data['rows']:
            try:
                name = phone_check(item['agent']['phone'])
                id_account = item['agent']['meta']['href'].split('/')[-1]
                if name not in result and name != 0:
                    result[name] = {} # Создали ключ с именем ID контрагента

                # теперь надо добавить ключ с id заказа
                if item['id'] not in result[name]:
                    result[name][item['id']] = []

                # Добавляем товары из сделки
                for assortment in item['positions']['rows']:
                    result[name][item['id']].append(assortment['assortment']['externalCode'])
            except:
                pass

    print('Готово')
    with open('./File/result.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)


# main_2()
search_salereturn()