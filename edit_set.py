import requests
import json
from sys import stdin

def search_id():
    external_all = tuple((n.replace('\n', '') for n in stdin.readlines()))
    id_all = []
    for external in external_all:
        url = f'https://hatiko.ru/api.php/shop.product.search?hash=search%2Fid_1c%3D{external}&access_token=f1ad6ccb4cabacd6e1de947f3d102868'
        req = requests.get(url)
        id_all.append((req.json()['products'][0]['id']))
    return id_all

def edit_set():
    id_all = search_id()
    for id in id_all:
        url = f'https://hatiko.ru/api.php/shop.product.addToSet?id={id}&access_token=6acf9ef3e246128715d8ecaf9d7e1a83'
        data = {
                # 'set_id': "keshbek-glavnaya"
                'set_id': "best_price"
            }
        req = requests.post(url, data=data)
        print(req.status_code)

if __name__ == '__main__':
    edit_set()


# keshbek-glavnaya
# best_price