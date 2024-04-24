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

bearerToken = '9CEB26E01B3C4CB4711D9437F959A7E9E4B640B10577AD5A0A3DE5A3CCA2FC9E'
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

downloadPdqlGroupsData(pdqlGroupsJsonFile)

def findGroupId(groupsData, displayName):
    if not groupsData:
        return None

    for group in groupsData:
        if group["displayName"] == displayName:
            return group["id"]

        if "children" in group and group["children"]:
            result = findGroupId(group["children"], displayName)
            if result:
                return result

    return None

# Открытие файла с JSON-данными
with open(pdqlGroupsJsonFile, 'r', encoding='utf-8') as jsonFile:
    data = json.load(jsonFile)

# Запрос у пользователя "displayName" группы
displayNameInput = input("Введите 'displayName' группы: ")

# Пример использования
groupId = findGroupId(data["nodes"], displayNameInput)
if groupId:
    print(f"The group ID for '{displayNameInput}' is: {groupId}")
else:
    print(f"Group with 'displayName' '{displayNameInput}' not found.")
