import json
from datetime import datetime, timedelta
import requests
import time
start = datetime.now()
new = start - timedelta(days=14)
new_time = (str(new).split('.')[0])
# start_time = datetime.strptime(str(new), "%Y-%m-%d %H:%M:%S")

new1 = new.strftime("%Y-%m-%d %H:%M:%S")
print(new1)




headers = {
    "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
params = {
        "limit": 100,
        "offset": 0,
        "filter": f"state.name=Доставлен - клиент не доволен; moment<={new1}"
    }

def search_id_WA():
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/customerorder'
    req = requests.get(url, headers=headers, params=params)
    with open ('file.json', 'w')as file:
        json.dump(req.json(), file, ensure_ascii=False,  indent=4)
    print('Скачали')

search_id_WA()

