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

bearerToken = 'E93F95E0BC0CF5C6BCC9AD82CDB75A19ADCCFE184F2AD9ED29C2A8B9B5C8EDA8'
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

#ЗАПРОСЫ PDQL || функция поиска id группы по displayName в файле groupsOfQuerries.json
def getPdqlGroupId(groupsData, displayName):
    if not groupsData:
        print('Не было найдено группы с именем: ' + displayName)
        return None

    for group in groupsData:
        if group["displayName"] == displayName:
            return group["id"]
        
        if 'children' in group:
            result = getPdqlGroupId(group, displayName)
            if result:
                return result
            

downloadPdqlGroupsData(pdqlGroupsJsonFile)



with open(pdqlGroupsJsonFile, 'r', encoding='utf-8') as pdqlGroupsFile:
    groupsData = json.load(pdqlGroupsFile)["nodes"]



print(json.dumps(groupsData, indent=4, sort_keys=True, ensure_ascii=False))





print(getPdqlGroupId(groupsData, 'Name_of_group'))