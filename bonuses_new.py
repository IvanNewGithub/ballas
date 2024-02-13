import os
import pickle
import json
import re
import time
import httplib2
import requests as r
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from phonemask import phone_check
import pandas as pd
from datetime import datetime, timedelta
import re
import time


def rasschet(price, procent, name, moment_sale):
    current_date = datetime.strptime(moment_sale, '%Y-%m-%d %H:%M:%S.%f')
    date_nachislenie = datetime(2024, 1, 30)
    if current_date > date_nachislenie: #Если 14 дней еще не прошло
        return 0
    if re.match(r'^уценка ', name):
        date_ucenka = datetime(2023, 12, 1)
        if current_date < date_ucenka:
            return int(price * 0.01)
        else:
            return int(price * 0.03)
    if procent == "":
        return 0
    if procent == 0:
        return 0
    if procent <= 10:
        date_all = datetime(2023, 1, 1)
        if current_date < date_all:
            return int(price * (procent/200))
        return int(price * (procent / 100))
    if procent > 10:
        date_aks = datetime(2023, 9, 1)
        if current_date > date_aks:
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
            else: return int(price * 0.01)
        else:
            return int(price * 0.01)

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


class balls:
    def __init__(self, item):
        self.item = item

    def plus(self):
        pass

    def minus(self, result, name, all_balls):
        otvet = result[name]['Счетчик бонусов'].copy()
        for key, value in result[name]['Счетчик бонусов'].items():
            if all_balls >= value:
                all_balls -= value
                del otvet[key]
            else:
                all_balls = value - all_balls
                otvet[key] = all_balls
            if value == 0:
                del otvet[key]

        return otvet

    def fair_balls(self, result, name):
        current_time = datetime.strptime(self.item['created'].split(' ')[0], '%Y-%m-%d')
        otvet = result[name]['Счетчик бонусов'].copy()
        #__________ Сгорание просроченных баллов ___________________
        for key, value in result[name]['Счетчик бонусов'].items():
            if current_time > datetime.strptime(key.split(' ')[0], '%Y-%m-%d') or value == 0:
                del otvet[key]
        return otvet



    def examination_return(self, name, externalCode):
        with open('./File/salereturn.json', 'r') as file:
            data = json.load(file)
            try:
                if externalCode in data[name][self.item['id']]:
                    return 1
                else:
                    return 0
            except:
                return 0

        pass

class atributes:
    def __init__(self, item):
        self.item = item

    def phonee(self):
        # ______________ Получаем номер телефона_______
        name = 0
        if "phone" in self.item['agent']:
            name = phone_check(self.item['agent']['phone'])
        return name

    def discount_balls(self):
        #__________ Бонусы оплаченные в Битрикс ___________________
        if 'attributes' in self.item:
            for balls in self.item[
                'attributes']:  # Здесь отвалится если не будет атрибутов у заказа и заказ будет пропущен (Поправил)
                if balls['name'] == 'Оплачено бонусами':
                    return balls
    def externalCode(self, assortment):
        if "externalCode" in assortment['assortment']:
            externalCode = assortment['assortment'][
                'externalCode']  # Внешний код может быть пустым, особенно если это заказ сервиса или услуги за пределами "главной"
        if not "externalCode" in assortment['assortment']:
            externalCode = "notExternalCode"  # Если нету внеш кода

        return externalCode


class Price(atributes):
    def Price_off_discount(self, assortment):
        return (int(assortment['price']) / 100) * int(assortment['quantity'])



def main(loaded_variable, result):
    for item in loaded_variable['rows']:

        name = atributes(item).phonee()
        if name == 0:
            continue

        if name not in result:
            result[name] = {}  # Создали ключ с именем ID контрагента
            result[name]['Счетчик бонусов'] = {}


        #______________________________ Создаем шапку _____________________________
        if item['id'] not in result[name]:
            result[name][item['id']] = {}
            result[name][item['id']]['Дата заказа'] = item['created']
            # result[name][item['id']]['Организация'] = item['organization']['name']
            result[name][item['id']]['Цена на заказ без скидки'] = 0
            result[name][item['id']]['Цена на заказ у с учетом скидки'] = 0
            result[name][item['id']]['Скидка на заказ'] = 0




        # balls =  # Баллы оплаченные в Битрикс

        try:
            result[name][item['id']]['Оплачено бонусами'] = int(atributes(item).discount_balls()['value'])
        except:
            result[name][item['id']]['Оплачено бонусами'] = 0

        result[name][item['id']]['Оплачено бонусами'] = result[name][item['id']].get('Оплачено бонусами', 0)  # Заносим кол-во бонусов, но это не приоритет



        # Добавляем товары из сделки
        if 'positions' in item:
            bonuses = 0
            for assortment in item['positions']['rows']:  # Тут отвалится если нет ассортимента, но это некорректные заказы. Rows может быть пустым при наличии позишн?

                externalCode = atributes(item).externalCode(assortment)



                if externalCode not in result[name][item['id']]:
                    result[name][item['id']][externalCode] = {}

                #_____________ Все цены на определенный товар _____________________________
                pice_sale = Price(item).Price_off_discount(assortment)

                result[name][item['id']][externalCode]['Цена на товар без скидки'] = pice_sale
                result[name][item['id']][externalCode]['Цена на товар со скдикой'] = pice_sale - (
                            pice_sale * (assortment['discount'] / 100))  # Скидку делим на 100% чтобы вычесть скидку
                skidka = result[name][item['id']][externalCode]['Цена на товар без скидки'] - result[name][item['id']][externalCode]['Цена на товар со скдикой']

                #___________ Определим является этот код возвратным _________________
                date_sale = str(datetime.strptime(result[name][item['id']]['Дата заказа'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=365))
                # if balls(item).examination(name, externalCode) == 1:
                #     continue

                result[name]['Счетчик бонусов'] = balls(item).fair_balls(result, name)

                #_______________________ Списываем баллы ______________________#
                # Шаг первый получить количество баллов которые нужно списать
                all_balls = result[name][item['id']]['Оплачено бонусами'] + skidka
                # шаг второй вычли баллы
                result[name]['Счетчик бонусов'] = balls(item).minus(result, name, all_balls)
                result[name][item['id']]['Оплачено бонусами'] = 0
                # print(externalCode)
                #_____________ Начисляем баллы ________________________________
                try:
                    if balls(item).examination_return(name, externalCode) == 0:
                        result[name]['Счетчик бонусов'][date_sale] = result[name]['Счетчик бонусов'].get(date_sale, 0) + rasschet(
                            result[name][item['id']][externalCode]['Цена на товар со скдикой'],
                            int(mytable.loc[mytable["Внешний код"] == f"{externalCode}", "Начисляемый процент"].item()),
                            mytable.loc[mytable["Внешний код"] == f"{externalCode}", "Наименование"].item(),
                            result[name][item['id']]['Дата заказа'])
                except:
                    result[name]['Счетчик бонусов'][date_sale] = result[name]['Счетчик бонусов'].get(date_sale, 0)
                result[name]['Счетчик бонусов'] = balls(item).fair_balls(result, name)
    return result







class product:
    def __init__(self, state, offset):
        self.url = "https://api.moysklad.ru/api/remap/1.2/entity/customerorder"
        self.state = state
        self.offset = int(offset)
        self.params = {
            "limit": 100,
            "offset": 0,
            "filter": f"state.name=Выполнен",
            "expand": "agent, positions.assortment",
            "order": "moment,asc;"
        }

    def result(self):
        data_list = []
        headers = {
            "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
        }
        # for item_offset in range(0, self.offset, 100):
        self.params['offset'] = self.offset
        req = r.get(self.url, headers=headers, params=self.params)
        assert req.status_code == 200
        data = req.json()
        # data_list.append(data)

        return data










if __name__ == '__main__':
    #______________ Открываем таблицу с процентами ______________
    id_table = '1HQNwp7ZfwKWDIewnlu81VI8TqTPjSpaAJURkj7BxcK4'
    ranges = 'Проценты'
    mytable = google_requst(id_table, ranges).download_table()
    mytable.drop(index=0, inplace=True)
    result = {}
    folder_path = './File/Заказы с МС/jsons'


    # ________Откроем файл с возвратами__________________________
    with open('./File/salereturn.json', 'r') as sr:
        sale_return = json.load(sr)
    end = 73000

    #_________Открываем продажи__________________________________
    for i in range(0, end, 100):
        try:
            # print('Прошли', i)
            # loaded_variable = product("Выполнен", i).result()
        # print(loaded_variable['rows'])
        filename = f"output_{i}.pkl"
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'rb') as file:
            loaded_variable = pickle.load(file)
        # except:
        #     break
        result = main(loaded_variable, result)
        # if len(loaded_variable['rows']) < 100:
        #     break

    with open('./File/zakazs_oborobotans.json', 'w') as file_1:
        json.dump(result, file_1, ensure_ascii=False, indent=4)