import json

import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import pandas as pd


class google_requst:
    def __init__(self, spreadsheet_id, ranges):
        self.ranges = ranges
        self.spreadsheet_id = spreadsheet_id

    def connect(self):
        """Эта хрень нужна чисто для получени списка с симками"""
        CREDENTIALS_FILE = '../Необходимые файлы для подключений/credentials.json'

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

def obrabotka(current_tel):
    result = {}
    for index, item in current_tel.T.items():
        if item['есть основной?']:
            if item['phones'] not in result:
                result[item['phones']] = {}
            result[item['phones']]['osnova'] = item['id']
        else:
            if item['phones'] not in result:
                result[item['phones']] = {}
            if 'dubl' not in result[item['phones']]:
                result[item['phones']]['dubl'] = [item['id']]
            else:
                result[item['phones']]['dubl'].append(item['id'])
    return result


if __name__ == '__main__':
    id_table = '1V0thoYAF4quDw2bn2TZDv8mmOYLTW_kH0SkmFCqW4RQ'
    range = 'cust_file'
    data = google_requst(id_table, range).download_table()
    # print(data['есть основной?'])
    df = data.replace('#N/A', None)
    contagent_MS = list(df.dropna(axis='index', how='any', subset=['есть основной?']))
    # contagent_MS.to_csv('../File/contagent.csv')
    # print(contagent_MS)
    current_tel = pd.DataFrame(df.loc[df['phones'].str.len() >= 11]) # Собираем только те строки, где длина номера больше или равна 11
    print(type(current_tel))
    current_tel.to_csv('../File/contagent.csv')
    with open('../File/dubl.json', 'w') as j:
        json.dump(obrabotka(current_tel), j, ensure_ascii=False, indent=4)
    print('Comlete!')
