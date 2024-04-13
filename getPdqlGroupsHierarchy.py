from datetime import datetime
import csv
import getpass
import json
import logging
import os
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

bearerToken = '48DEF6BAB67E7E592E72C976E3548C31D765B01635F7C390C0D1D0E9F867CD3A'
rootUrl = 'https://10.2.183.20/api/assets_temporal_readmodel/v1/stored_queries/folders/queries/'

currentDirectory = os.path.dirname(os.path.abspath(__file__))                           #текущая директория
manifestsDirectory = os.path.join(currentDirectory, 'deployment_manifests')             #директория с манифестами
pdqlGroupsJsonFile = os.path.join(manifestsDirectory, "groupsOfQuerries.json")          #файл, куда скачаваем информацию о группах PDQL запросов

#PDQL запросы || функция скачивания файла, содержащего информацию о группах PDQL запросов
def downloadPdqlGroupsData(pdqlGroupsJsonFile):
    headers = {
        'Authorization': f'Bearer {bearerToken}',
        'content-type': 'application/json, text/plain, */*'
        }
    response = requests.get(rootUrl, headers=headers, verify=False)
    response.raise_for_status()

    with open (pdqlGroupsJsonFile, 'w', encoding='utf-8') as pdqlGroupsFile:
        json.dump(response.json(), pdqlGroupsFile, ensure_ascii=False)
