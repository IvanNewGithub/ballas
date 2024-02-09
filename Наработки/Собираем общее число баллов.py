import json


with open('../File/result_actual.json', 'r') as j:
    data = json.load(j)

result = {}

for kontragent in data.items():
    print('Номер контагента', kontragent[0])
    skidka = 0
    for key, sdelka in kontragent[1].items():
        print(sdelka)
        print('Номер заказа', key)
        print('Цена на заказ без скидки', sdelka["Цена на заказ без скидки"])
        if type(sdelka) == dict:
            for item in sdelka.items():
                print(item)
    break