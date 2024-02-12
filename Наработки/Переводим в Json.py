import pickle
import json
import os

for root, dirs, files in os.walk("../File/Заказы с МС/jsons"):
    for filename in files:
        with open(f'../File/Заказы с МС/jsons/{filename}', 'rb') as f:
            data = pickle.load(f)

            with open('../File/Заказы копия 12.02.json', 'r') as j:
                data2 = json.load(j)
                data2['rows'] = data2.get('rows', []) + data['rows']
                with open('../File/Заказы копия 12.02.json', 'w') as fb:
                    json.dump(data2, fb, ensure_ascii=False, indent=4)
                print(f"Добавили файл {filename}")
