import json
import requests as r
import time
from datetime import datetime, timedelta

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
for x in data['rows']:
    # print(x['phone'])
    try:
        result.setdefault(x['agent']['phone'], {})
        result[x['agent']['phone']].setdefault('id заказа', []).append(x['id'])
        result[x['agent']['phone']]['Внешний код товара'] = []
        for j in x['positions']['rows']:
            result[x['agent']['phone']]['Внешний код товара'].append(j['assortment']['externalCode'])
            # result[x['agent']['phone']]['Внешний код товара'][j['assortment']['externalCode']] = j['things']
    except:
        pass


with open('File/salereturn.json', 'w') as j:
    json.dump(result, j, ensure_ascii=False, indent=4)
# print(r1, r1.text)