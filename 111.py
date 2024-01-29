def edit_datetime(zakaz):
    zakaz = '2214bd95-27bd-11ee-0a80-1421000e4125'
    headers2 = {
        "Authorization": f'Basic Z2FsY2V2QHNrbDRkbTpMaVRGcUlBTQ=='
    }
    url = f'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/{zakaz}/audit'
    req = requests.get(url, headers=headers2).json()
    print(req)
    pass