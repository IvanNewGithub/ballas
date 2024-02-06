import json
import requests as r
import re
from phonemask import phone_check
import time
from datetime import datetime, timedelta

headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
}


def search_salereturn():  # Ищем среди всех возвратов
    headers = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    result = {}
    for offset in range(0, 2000, 100):
        params = {
            "limit": 100,
            "offset": offset,
            "filter": f"moment>2023-01-11 12:00:00;",
            'expand': 'demand,positions.assortment,agent'
        }

        url = "https://api.moysklad.ru/api/remap/1.2/entity/salesreturn"
        data = r.get(url, headers=headers, params=params).json()
        for x in data['rows']:
            try:
                id_zakaz = x['demand']['customerOrder']['meta']['href'].split('/')[-1]
                phone = phone_check(x['agent']['phone'])
                if phone not in result and phone != 0:
                    result[phone] = {}
                if id_zakaz not in result[phone]:
                    result[phone][id_zakaz] = []
                for j in x['positions']['rows']:
                    result[phone][id_zakaz].append(j['assortment']['externalCode'])
            except:
                pass
        if len(data['rows']) < 100:
            break

    with open('File/salereturn.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)


class product:
    def __init__(self, state, offset):
        self.url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
        self.state = state
        self.offset = offset
        self.params = {
            "limit": 100,
            "offset": 0,
            "filter": f"state.name=Выполнен;moment>2023-01-01 12:00:00;",
            "expand": "agent, positions.assortment"
        }

    def result(self):
        data_list = []
        for item_offset in range(0, self.offset, 100):
            self.params['offset'] = item_offset
            req = r.get(self.url, headers=headers, params=self.params)
            assert req.status_code == 200
            data = req.json()
            data_list.append(data)
            if len(data['rows']) < 100:
                break
        return data_list


def all_sale(offset):
    result = {}
    start_time = datetime.now()
    data_list = product('Доставлен', offset).result()
    for data in data_list:
        for item in data['rows']:
            try:
                name = phone_check(item['agent']['phone'])
                if name not in result and name != 0:
                    result[name] = {}  # Создали ключ с именем ID контрагента
                # теперь надо добавить ключ с id заказа
                if item['id'] not in result[name]:
                    result[name][item['id']] = {}
                    result[name][item['id']]['Дата заказа'] = item['created']
                    result[name][item['id']]['Цена на заказ без скидки'] = 0
                    result[name][item['id']]['Цена на заказ у с учетом скидки'] = int(item['sum']) / 100
                    result[name][item['id']]['Скидка на заказ'] = 0
                # Добавляем товары из сделки
                for assortment in item['positions']['rows']:
                    externalCode = assortment['assortment']['externalCode']
                    if externalCode not in result[name][item['id']]:
                        result[name][item['id']][externalCode] = {}
                    result[name][item['id']][externalCode]['Цена до скидки'] = int(assortment['price']) / 100 * \
                                                                               assortment['quantity']
                    result[name][item['id']]['Цена на заказ без скидки'] += result[name][item['id']][externalCode][
                        'Цена до скидки']

                    # result[name][item['id']][externalCode]['Цена до скидки'] = int(item['sum'])/100
                    result[name][item['id']][externalCode]['Скидка'] = (assortment['discount'])
                for balls in item['attributes']:
                    if balls['name'] == 'Оплачено бонусами':
                        result[name][item['id']]['Оплачено бонусами'] = balls['value']
                result[name][item['id']]['Скидка на заказ'] = result[name][item['id']]['Цена на заказ без скидки'] - \
                                                              result[name][item['id']][
                                                                  'Цена на заказ у с учетом скидки']
            except Exception as ex:
                print('Ошибка', ex)

    print('Готово')
    print(datetime.now() - start_time)
    with open('File/result.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # all_sale(offset=34500)
    search_salereturn() # Собираем возвраты
