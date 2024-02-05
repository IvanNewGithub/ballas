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


id_table = '1V0thoYAF4quDw2bn2TZDv8mmOYLTW_kH0SkmFCqW4RQ'
range = 'cust_file'

data = google_requst(id_table, range).download_table()
print(data)