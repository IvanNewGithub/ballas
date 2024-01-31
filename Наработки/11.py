import json

with open ('../File/salereturn.json', 'r') as j:
    data = json.load(j)
    # print(data)
    data2 = tuple((j['assortment']['externalCode'] for n in data['rows'] for j in n['positions']['rows']))
    data3  = tuple((n['id'] for n in data['rows']))