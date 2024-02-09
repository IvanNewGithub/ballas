import json
import requests as r
import re
from phonemask import phone_check
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import pandas as pd
from datetime import datetime, timedelta

headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
}

import re

def rasschet(price, procent, name, moment_sale):


    if re.match(r'^уценка ', name):
        current_date = datetime.strptime(moment_sale, '%Y-%m-%d %H:%M:%S.%f')
        date_compare = datetime(2023, 12, 1)
        if current_date < date_compare:
            return 0
        else:
            return int(price * 0.03)

    if procent == "":
        return 0
    if procent == 0:
        return 0
    if procent <= 10:
        return int(price * (procent/100))
    if procent > 10:
        if price <= 2000:
            return int(price * 0.10)
        if price > 2000 and price <= 2500:
            return int(price * 0.09)
        if price > 2500 and price <= 3000:
            return int(price * 0.08)
        if price > 3000 and price <= 3500:
            return int(price * 0.07)
        if price > 3500 and price <= 4000:
            return int(price * 0.06)
        if price > 4000 and price <= 7000:
            return int(price * 0.05)


class google_requst:
    def __init__(self, spreadsheet_id, ranges):
        self.ranges = ranges
        self.spreadsheet_id = spreadsheet_id

    def connect(self):
        """Эта хрень нужна чисто для получени списка с симками"""
        CREDENTIALS_FILE = './Необходимые файлы для подключений/credentials.json'

        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, [
            'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

        httpAuth = credentials.authorize(httplib2.Http())
        service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

        return service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                        ranges=self.ranges,
                                                        valueRenderOption='FORMATTED_VALUE',
                                                        dateTimeRenderOption='FORMATTED_STRING').execute()

    def download_table(self):
        simall = pd.DataFrame(self.connect()['valueRanges'][0]['values'])
        simall.columns = simall.iloc[0]
        return simall

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
        self.offset = int(offset)
        self.params = {
            "limit": 100,
            "offset": 0,
            "filter": f"state.name=Выполнен;moment>2023-01-01 12:00:00;",
            "expand": "agent, positions.assortment",
            "order": "moment,asc;"
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


def all_sale(offset, mytable):
    result = {}
    start_time = datetime.now()
    data_list = product('Доставлен', offset).result()
    for data in data_list:
        for item in data['rows']:
            try:
                name = phone_check(item['agent']['phone'])
                if name not in result and name != 0:
                    result[name] = {}  # Создали ключ с именем ID контрагента
                    result[name]['Счетчик бонусов'] = 0
                # теперь надо добавить ключ с id заказа
                if item['id'] not in result[name]:
                    result[name][item['id']] = {}
                    result[name][item['id']]['Дата заказа'] = item['created']
                    result[name][item['id']]['Цена на заказ без скидки'] = 0
                    result[name][item['id']]['Цена на заказ у с учетом скидки'] = 0
                    result[name][item['id']]['Скидка на заказ'] = 0

                    for balls in item['attributes']:
                        if balls['name'] == 'Оплачено бонусами':
                            result[name][item['id']]['Оплачено бонусами'] = int(balls['value'])
                    result[name][item['id']]['Оплачено бонусами'] = result[name][item['id']].get('Оплачено бонусами', 0)
                # Добавляем товары из сделки
                for assortment in item['positions']['rows']:
                    externalCode = assortment['assortment']['externalCode']
                    if externalCode not in result[name][item['id']]:
                        result[name][item['id']][externalCode] = {}
                    pice_sale = (int(assortment['price']) / 100) * assortment['quantity']
                    result[name][item['id']][externalCode]['Цена на товар без скидки'] = pice_sale
                    result[name][item['id']][externalCode]['Цена на товар со скдикой'] =  pice_sale - (pice_sale * (assortment['discount'] / 100))

                    result[name][item['id']]['Цена на заказ без скидки'] += result[name][item['id']][externalCode]['Цена на товар без скидки']

                    # result[name][item['id']][externalCode]['Цена до скидки'] = int(item['sum'])/100
                    result[name][item['id']][externalCode]['Скидка'] = (assortment['discount'])
                    # print(mytable.loc[mytable["Внешний код"] == f"{externalCode}", "Начисляемый процент"].item())


                result[name][item['id']]['Цена на заказ у с учетом скидки'] = int(item['sum']) / 100
                result[name][item['id']]['Скидка на заказ'] = 0
                # _____Вычитаем потраченные бонусы_______
                result[name]['Счетчик бонусов'] -= result[name][item['id']]['Скидка на заказ']
                result[name]['Счетчик бонусов'] -= result[name][item['id']].get('Оплачено бонусами', 0)
                if result[name]['Счетчик бонусов'] < 0:
                    result[name]['Счетчик бонусов'] = 0
                for assortment in item['positions']['rows']:
                    externalCode = assortment['assortment']['externalCode']
                    result[name]['Счетчик бонусов'] += rasschet(
                        result[name][item['id']][externalCode]['Цена на товар со скдикой'],
                        int(mytable.loc[mytable["Внешний код"] == f"{externalCode}", "Начисляемый процент"].item()),
                        mytable.loc[mytable["Внешний код"] == f"{externalCode}", "Наименование"].item(),
                        result[name][item['id']]['Дата заказа'])

                result[name][item['id']]['Скидка на заказ'] = result[name][item['id']]['Цена на заказ без скидки'] - \
                                                              result[name][item['id']][
                                                                  'Цена на заказ у с учетом скидки']





            except Exception as ex:
                print('Ошибка', ex)
                # pass

    print('Готово')
    print(datetime.now() - start_time)
    with open('File/result.json', 'w') as j:
        json.dump(result, j, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    id_table = '1HQNwp7ZfwKWDIewnlu81VI8TqTPjSpaAJURkj7BxcK4'
    ranges = 'Проценты'
    table = google_requst(id_table, ranges).download_table()
    # print(type(table), table)
    all_sale(offset= 100, mytable=table)
    # search_salereturn()  # Собираем возвраты
