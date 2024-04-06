#библиотеки
from datetime import datetime
import csv
import getpass
import json
import logging
import os
import requests
import time
import urllib3

#-------------------------------------ГЛОБАЛЬНЫЕ-----------------------------------------#
#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ универсальная отправки POST запроса 
def sendAnyPostRequest(requestUrl, headers, data, jsonData, requestType):
    try:
        if jsonData:
            logging.info(f'Отправлен POST запрос на {requestType} с JSON данными на url {requestUrl}')
            response = requests.post(requestUrl, headers=headers, json=jsonData, verify=False)
        else:
            logging.info(f'Отправлен POST запрос на {requestType} с данными на url {requestUrl}')
            response = requests.post(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()  # Проверка статуса ответа

        logging.info(f'Запрос на {requestType} выполнен успешно на url {requestUrl}.')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении {requestType} запроса на {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ универсальная отправки GET запроса 
def sendAnyGetRequest(requestUrl, headers, data, json_data, requestType):
    try:
        print(f'Отправляется запрос на {requestType}')
        
        if json_data:
            logging.info(f'Отправлен GET запрос на {requestType} с JSON данными на url {requestUrl}')
            response = requests.get(requestUrl, headers=headers, json=json_data, verify=False)
        else:
            logging.info(f'Отправлен GET запрос на {requestType} с данными на url {requestUrl}')
            response = requests.get(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()  # Проверка статуса ответа

        logging.info(f'Запрос на {requestType} выполнен успешно на url {requestUrl}.')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса. Логи находятся в {loggingFile}')
        return None
    
#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ получения токена доступа
def getTokenMpx():
    logging.info('Функция getTokenMpx запущена')

    #ввод логина и пароля
    while True: 
        adminName = input('Введите логин пользователя MP10: ') 
        adminPassword = getpass.getpass('Введите пароль пользователя MP10: ')
        adminPasswordCheck = getpass.getpass('Повторите пароль пользователя MP10: ')
        if adminPassword != adminPasswordCheck:
            logging.error('Пароли при вводе не совпали.')
            print('Пароли не совпадают. Повторите попытку.')
            continue
        else:
            logging.info('Логин и пароль пользователя MP10 введены верно')
            break
    #ввод clientSecret
    logging.info('Введен clientSecret.')
    clientSecret = input('Введите clientSecret: ') 

    #заголовки запроса
    headersOfRequest = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    #тело запроса
    dataGetAuthToken = {
        'username': adminName,
        'password': adminPassword,  
        'client_id':'mpx',
        'client_secret': clientSecret,
        'grant_type':'password',
        'response_type':'token',
        'scope':'mpx.api',
    }
    #отправка запроса
    getAuthToken = sendAnyPostRequest(rootUrl + ':3334/connect/token', headersOfRequest, dataGetAuthToken, None, 'получение токена доступа для mpx')
    
    if getAuthToken is None:
        logging.error('Не удалось получить токен доступа. Вернулся объект None')
        return None
    else:
        logging.info('Токен доступа получен.')
        return getAuthToken.json()['access_token']

#-------------------------------------ГРУППЫ АКТИВОВ-------------------------------------#
#ГРУППЫ АКТИВОВ || ФУНКЦИЯ поиска id группы по ее имени
def getGroupID(parentName):
    print(f"Выполняется поиск id этой группы-родителя: {parentName}")
    
    # Запрос на получение информации о всех группах
    groupsUrl = f"{rootUrl}/api/assets_temporal_readmodel/v2/groups/hierarchy"
    headers = {'Authorization': f'Bearer {bearerToken}'}

    # Отправка запроса
    response = sendAnyGetRequest(groupsUrl, headers, None, None, f'поиск группы {parentName}')
    groupsData = response.json()

    # Поиск родительской группы по имени
    parentGroupId, found = findGroupIdRecursive(groupsData, parentName)
    if not found:
        print(f"Родительская группа {parentName} для создаваемой группы не была найдена. Создаваемая группа будет в группе Root")
        parentGroupId = '00000000-0000-0000-0000-000000000002'  # Устанавливаем ID root
    else:
        print(f"Родительская группа {parentName} имеет ID: {parentGroupId}")
    return parentGroupId

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ рекурсивного поиска группы в подгруппах
def findGroupIdRecursive(groupsData, targetGroupName):
    # Поиск группы по имени в текущем уровне
    for group in groupsData:
        if group["name"] == targetGroupName:
            return group["id"], True  # Группа найдена, возвращаем ID и True

        # Рекурсивный поиск во всех дочерних группах
        if "children" in group:
            result, found = findGroupIdRecursive(group["children"], targetGroupName)
            if found:
                return result, True

    return '00000000-0000-0000-0000-000000000002', False  # Группа не найдена, возвращаем ID root и False

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ проверки статуса создания группы
def checkGroupCreated(operationId):
    # Запрос на проверку статуса операции
    operationStatusUrl = f"{rootUrl}/api/assets_processing/v2/groups/operations/{operationId}"
    headers = {'Authorization': f'Bearer {bearerToken}'}

    while True:
        # Отправка запроса
        response = sendAnyGetRequest(operationStatusUrl, headers, None, None, f'проверка статуса создания группы')

        if response is not None and response.status_code != 202:
            print('Группа создана. Ее ID: ' + response.json())
            break
        elif response is not None:
            time.sleep(1)
            print('Группа не создана. Пожалуйста, подождите.')
        else:
            print('Ошибка при выполнении запроса. Повторная попытка отправки запроса.')

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ групп CSV -> JSON + сохраняем на сервер
def createAssetsFromCsv(csvFilePath):

    # Открываем CSV-файл
    with open(csvFilePath, 'r', newline='', encoding='utf-8') as assetsGroupsFile:
        # Создаем читатель CSV
        csvReader = csv.reader(assetsGroupsFile, delimiter=';')

        # Пропускаем заголовок (первую строку)
        next(csvReader)

        # Обрабатываем оставшиеся строки
        for row in csvReader:
            print('-----------------------------------------------------------------------')
            print(f"Выполняется чтение параметров для создания группы: {row[0]}")
            # Создаем словарь для хранения данных текущей строки
            rowData = {
                "name": row[0],
                "description": row[1],
                "parentId": getGroupID(row[2]),
                "groupType": row[3],
                "predicate": row[4],
                "metrics": {
                    "ar": row[5],
                    "cdp": row[6],
                    "cr": row[7],
                    "ir": row[8],
                    "td": row[9]
                },
                "organizationInformation": {
                    "address": row[10],
                    "contactUserId": row[11]
                },
                "organizationInfrastructure": {
                    "internetProviders": row[12],
                    "numberOfNodes": row[13],
                    "registeredDomains": row[14],
                    "usedNetworkApplications": row[15],
                    "usedNetworks": row[16]
                }
            }
            
            # удаление лишних полей
            if row[3] == "static":
                del rowData["predicate"]
            
            print('-----------------------------------------------------------------------')

            # Создаем новую группу
            createGroupsUrl = rootUrl + '/api/assets_processing/v2/groups' 
            headers = {'Authorization': 'Bearer ' + bearerToken}
            createGroupsRequest = sendAnyPostRequest(createGroupsUrl, headers, None, rowData, f'создание группы {row[0]}')

            #проверяем статус того, что группа создалась
            print('-----------------------------------------------------------------------')
            print(f'Проверка создания группы: {row[0]}')
            checkGroupCreated(createGroupsRequest.json()["operationId"])

#-------------------------------------PDQL ЗАПРОСЫ----------------------------------------#
#ЗАПРОСЫ PQDL || ФУНКЦИЯ поиска id группы запросов по ее displayName имени в файле groupsOfQuerries.json
def findGroupId(groupsData, displayName):
    if not groupsData:
        print('Не было найдено группы с именем: ' + displayName)
        return None

    for group in groupsData:
        if group["displayName"] == displayName:
            return group["id"]

        if "children" in group and group["children"]:
            result = findGroupId(group["children"], displayName)
            if result:
                return result

#ЗАПРОСЫ PQDL || ФУНКЦИЯ создание группы для запросов
def createPdqlGroups(querriesGroupsCsvFile, pdqlManifestCsvFile):
    # Читаем информацию о группах для запросов из файла pdql_groups_manifest.csv
    with open(querriesGroupsCsvFile, 'r', newline='', encoding='utf-8') as pqdlGroupsFile:
        # Создаем читателя
        csvreader = csv.reader(pqdlGroupsFile, delimiter=';')
        # Пропускаем первую строку
        header = next(csvreader)
        
        # Читаем все строки в память
        rows = list(csvreader)

    # Создаем группы по оставшимся строкам
    for row in rows:
        print('-----------------------------------------------------------------------')
        print(f"Выполняется чтение параметров для создания группы PDQL запросов: {row[0]}")

        # Отправляем запрос на создание группы PDQL запросов
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearerToken}"
        }
        rowData = {
            "displayName": row[0],
            "parentId": row[1],
            "type": row[2]
        }
        response = requests.post(rootUrl + "/api/assets_temporal_readmodel/v1/stored_queries/folders/queries", headers=headers, json=rowData, verify=False)
        print('Запрос на создание группы: ' + row[0] + ' отправлен')
        response.raise_for_status()
        if response.status_code == 200:
            print('Группа ' + row[0] + ' создана успешно. Ее ID: ' + response.json()["id"])
            
            # Обновление данных в памяти
            for line in rows:
                if line[1] == row[0]:
                    line[1] = response.json()["id"]

            # Перезаписываем файл с обновленными данными
            with open(querriesGroupsCsvFile, 'w', newline='', encoding='utf-8') as pqdlGroupsFile:
                # Создаем писателя
                csvwriter = csv.writer(pqdlGroupsFile, delimiter=';')
                # Записываем заголовок
                csvwriter.writerow(header)
                # Записываем обновленные строки
                csvwriter.writerows(rows)

            # Теперь обновим pdql_manifest.csv
            with open(pdqlManifestCsvFile, 'r', newline='', encoding='utf-8') as pdqlManifestFile:
                # Создаем читателя
                manifestReader = csv.reader(pdqlManifestFile, delimiter=';')
                # Пропускаем первую строку
                manifestHeader = next(manifestReader)
                
                # Читаем все строки в память
                manifestRows = list(manifestReader)

            # Обновляем значения в pdql_manifest.csv
            for manifestRow in manifestRows:
                if manifestRow[2] == row[0]:
                    manifestRow[2] = response.json()["id"]

            # Перезаписываем файл pdql_manifest.csv с обновленными данными
            with open(pdqlManifestCsvFile, 'w', newline='', encoding='utf-8') as pdqlManifestFile:
                # Создаем писателя
                manifestWriter = csv.writer(pdqlManifestFile, delimiter=';')
                # Записываем заголовок
                manifestWriter.writerow(manifestHeader)
                # Записываем обновленные строки
                manifestWriter.writerows(manifestRows)
        else:
            print('Сервер вернул код ошибки: ' + str(response.status_code))
    return True

#ЗАПРОСЫ PDQL || ФУНКЦИЯ создание pdql запросов
def createPdqlQueries(querriesCsvFile):
    
    with open(querriesCsvFile, 'r', newline='', encoding='utf-8') as pdqlQueriesFile:
        # Создаем читателя
        csvReader = csv.reader(pdqlQueriesFile, delimiter=';')
        next(csvReader)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearerToken}"
        }

        for row in csvReader:
            print('-----------------------------------------------------------------------')
            print(f"Выполняется чтение параметров для PDQL запроса: {row[0]}")

            rowData = {
                "displayName": row[0],
                "filterPdql": row[1],
                "folderId": row[2],
                "isDeleted": "false",
                "isInvalid": "false",
                "selectionPdql": row[5],
                "type": row[6],
            }

            if row[1] == "none":
                del rowData["filterPdql"]
                
            response = requests.post(rootUrl + "/api/assets_temporal_readmodel/v1/stored_queries/queries", headers=headers, json=rowData, verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                print('PDQL запрос ' + row[0] + ' создан успешно. ID: ' + response.json()["id"])

    return None

#-------------------------- INT MAIN --------------------------------------------
#--------------------ОСНОВНОЙ КОД ПРОГРАММЫ--------------------------------------

#пропускать ворнинги
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#глобальные переменные
bearerToken = ''                        #токен MP10 Core
werePqlGroupsCreated = False            #флаг создания групп PDQL запросов нужен для PDQL запросов

#установление пути к файлам манифестам
currentDirectory = os.path.dirname(os.path.abspath(__file__))                           #текущая директория
manifestsDirectory = os.path.join(currentDirectory, 'deployment_manifests')             #директория с манифестами
groupsCsvFile = os.path.join(manifestsDirectory, "assets_groups_manifest.csv")          #манифест с настройками групп активов
querriesGroupsCsvFile = os.path.join(manifestsDirectory, "pdql_groups_manifest.csv")    #манифест с настройками групп PDQL запросов
querriesCsvFile = os.path.join(manifestsDirectory, "pdql_manifest.csv")                 #манифест с настройками PDQL запросов
querriesGroupsCsvFile = os.path.join(manifestsDirectory, "groupsOfQuerries.json")       #файл, куда скачаваем информацию о группах PDQL запросов

#логирование ошибок
loggingDirectory = os.path.join(currentDirectory, 'logging')        #директория с логами
loggingFile = f"main-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}-log.log"
logging.basicConfig(
    filename=os.path.join(loggingDirectory, loggingFile),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

#запрос корневой uRL и получение токена
print('--------------------------Добро пожаловать----------------------------')
rootUrl = 'https://' + input('Введите адрес MP10 Core: https://')
logging.info('Вызов функции получения токена getTokenMpx')
bearerToken = getTokenMpx()

#создание групп активов
print('--------------------------Группы активов------------------------------')
print(f'Необходимо ли создать группы активов из {groupsCsvFile} ? Yes/No')
if(input() == 'Yes'): werePqlGroupsCreated = createAssetsFromCsv(groupsCsvFile)

#создание групп PDQL запросов
print('--------------------------Группы запросов-----------------------------')
print(f'Необходимо ли создать группы PDQL запросов из {querriesCsvFile}? Yes/No')
if(input() == 'Yes'): werePqlGroupsCreated = createPdqlGroups(querriesGroupsCsvFile, querriesCsvFile)

#создание PDQL запросов
print('--------------------------PDQL запросы--------------------------------')
print(f'Необходимо ли создать PDQL запросы из {querriesCsvFile}? Yes/No')
if(input() == 'Yes' and werePqlGroupsCreated): createPdqlQueries(querriesCsvFile)

#print('Необходимо ли создать задачи? Yes/No')
#if(input() == 'Yes'): tasksCreate = True
#print('Необходимо ли создать учетные записи? Yes/No')
#if(input() == 'Yes'): accountsCreate = True