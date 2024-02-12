import os
import pickle
import json
import re
import time
from phonemask import phone_check
import pandas as pd
from datetime import datetime, timedelta
import re
import time
# # Загружаем переменную из файла
# data = {}
# with open('jsons/output_70000.pkl', 'rb') as file:
#     loaded_variable = pickle.load(file)
#
# for i in loaded_variable['rows']:
#     print(i['moment'])

result = {}

folder_path = 'C:/Users/Aleksandr/PycharmProjects/ballas/jsons'
for i in range(0, 73000, 100):
    filename = f"output_{i}.pkl"
    file_path = os.path.join(folder_path, filename)
    print(i)

    with open(file_path, 'rb') as file:
        loaded_variable = pickle.load(file)

    for item in loaded_variable['rows']:
        # print(item['name'])
        # try:
        if "phone" in item['agent']:
            name = phone_check(item['agent']['phone'])
            # print("это name", name)
        if not "phone" in item['agent']:
            name = 0
            continue
        if name == 0:
            # print("набе был пустым")
            continue
        # print(name)
        if name not in result and name != 0:
            result[name] = {}  # Создали ключ с именем ID контрагента
            result[name]['Счетчик бонусов'] = 0
        # print(name, item['agent']['phone'], item['id'])
        # теперь надо добавить ключ с id заказа
        if item['id'] not in result[name]:
            result[name][item['id']] = {}
            result[name][item['id']]['Дата заказа'] = item['created']
            result[name][item['id']]['Организация'] = item['organization']['name']
            result[name][item['id']]['Цена на заказ без скидки'] = 0
            result[name][item['id']]['Цена на заказ у с учетом скидки'] = 0
            result[name][item['id']]['Скидка на заказ'] = 0
            if 'attributes' in item:
                for balls in item[
                    'attributes']:  # Здесь отвалится если не будет атрибутов у заказа и заказ будет пропущен (Поправил)
                    if balls['name'] == 'Оплачено бонусами':
                        try:
                            result[name][item['id']]['Оплачено бонусами'] = int(balls['value'])
                        except:
                            result[name][item['id']]['Оплачено бонусами'] = 0
                result[name][item['id']]['Оплачено бонусами'] = result[name][item['id']].get('Оплачено бонусами',
                                                                                             0)  # Заносим кол-во бонусов, но это не приоритет
        # Добавляем товары из сделки
        if 'positions' in item:
            bonuses = 0
            for assortment in item['positions'][
                'rows']:  # Тут отвалится если нет ассортимента, но это некорректные заказы. Rows может быть пустым при наличии позишн?
                if "externalCode" in assortment['assortment']:
                    externalCode = assortment['assortment'][
                        'externalCode']  # Внешний код может быть пустым, особенно если это заказ сервиса или услуги за пределами "главной"
                if not "externalCode" in assortment['assortment']:
                    externalCode = "notExternalCode"  # Если нету внеш кода
                if externalCode not in result[name][item['id']]:
                    result[name][item['id']][externalCode] = {}
                pice_sale = (int(assortment['price']) / 100) * assortment['quantity']
                result[name][item['id']][externalCode]['Цена на товар без скидки'] = pice_sale
                result[name][item['id']][externalCode]['Цена на товар со скдикой'] = pice_sale - (
                            pice_sale * (assortment['discount'] / 100))  # Скидку делим на 100% чтобы вычесть скидку

                result[name][item['id']]['Цена на заказ без скидки'] += result[name][item['id']][externalCode][
                    'Цена на товар без скидки']
                # result[name][item['id']][externalCode]['Скидка'] = (assortment['discount']) # будет перезаписываться, если у последнего товара скидка будет равна нулю
                bonuses += pice_sale * (assortment['discount'] / 100)
                result[name][item['id']][externalCode]['Списанно баллами'] = pice_sale * (assortment['discount'] / 100)
            if bonuses > 0:
                result[name][item['id']]['Оплачено бонусами'] = bonuses

        result[name][item['id']]['Цена на заказ у с учетом скидки'] = int(item['sum']) / 100
        # result[name][item['id']]['Скидка на заказ'] = 0
# with open('resultzakaztzv2.json', 'w') as j:
#     json.dump(result, j, ensure_ascii=False, indent=4)
with open('zakazs_oborobotans.pkl', 'wb') as file:
    pickle.dump(result, file)

