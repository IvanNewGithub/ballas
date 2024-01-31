import json
import requests as r
import time
from datetime import datetime, timedelta

headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }


params = {
        "limit": 10,
        "offset": 0,
        "filter": f"moment>2023-01-11 12:00:00;",
        'expand': 'demand,positions.assortment,agent'
    }

url = "https://api.moysklad.ru/api/remap/1.2/entity/salesreturn"
r1 = r.get(url, headers=headers, params=params).json()
with open('File/salereturn.json', 'w') as j:
    json.dump(r1, j, ensure_ascii=False, indent=4)
# print(r1, r1.text)