# -*- coding: utf-8 -*-
print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                  WELCOME                                  ║
║                              MP VM API TOOL                               ║
║                          by @github.com/kaifuss/                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

#библиотеки
import importlib
import sys
import subprocess
required_libraries = ['datetime', 'csv', 'getpass', 'json', 'logging', 'os', 'requests', 'time', 'urllib3', 'glob']
for lib in required_libraries:
    try:
        importlib.import_module(lib)
    except ImportError:
        print(f"{lib} не установлена. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
            print(f"{lib} успешно установлена.")
        except Exception as e:
            print(f"Ошибка при установке {lib}: {e}\n Скрипт будет остановлен. Попробуйте установить {lib} вручную")
            sys.exit()

from datetime import datetime
import csv
import getpass
import glob
import json
import logging
import os
import requests
import time
import urllib3

#-------------------------------------ГЛОБАЛЬНЫЕ-----------------------------------------#
#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ получения ввода Yes / No от юзера
def getYesNoInput(Action):
    logging.info(f'Пользователя спросили {Action}.')
    while True:
        print(Action)
        inputAnswer = input('[Yes, Y, Да, Д| / [No, N, Нет, Н]: ').strip().lower()
        if inputAnswer in ['yes', 'y', 'да', 'д']:
            logging.info('Пользователь согласился на действие.')
            return True
        elif inputAnswer in ['no', 'n', 'нет', 'н']:
            logging.info('Пользователь отказался от действия.')
            return False
        else:
            logging.error('Некорректный ввод от пользователя.')
            print('Некорректный ввод. Повторите попытку.\n')

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ универсальная отправки POST запроса 
def sendAnyPostRequest(requestUrl, headers, data, jsonData, requestType):
    try:
        if jsonData:
            logging.info(f'Отправляется POST запрос на {requestType} с JSON данными на URL: {requestUrl}')
            response = requests.post(requestUrl, headers=headers, json=jsonData, verify=False)
        else:
            logging.info(f'Отправляется POST запрос на {requestType} с DATA данными на URL: {requestUrl}')
            response = requests.post(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logging.info(f'Запрос на {requestType} выполнен успешно на url {requestUrl}. Статус код: {response.status_code}')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении запроса на URL: {requestUrl}:\n {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла HTTP-ошибка при выполнении запроса на {requestType}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestType} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка отправки запроса {requestType}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла неизвестная ошибка при выполнении запроса на {requestType}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ универсальная отправки GET запроса 
def sendAnyGetRequest(requestUrl, headers, data, json_data, requestType):
    try:
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
        print(f'Произошла ошибка при выполнении запроса.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        print(f'Произошла ошибка при выполнении запроса.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ получения clientSecret если есть деплоер
def getMpxClientSecret():
    logging.info('Вызов функции getMpxClientSecret для получения MpxClientSecret')

    deployerPath = os.path.dirname('/var/lib/deployer')
    deployedRolesPath = os.path.dirname('/var/lib/deployed-roles/Deployment-Application')

    if os.path.exists(deployerPath) and os.path.exists(deployedRolesPath):
        print('Скрипт запущен на сервере с ролью Deployer. MpxCLientSecret будет взят из параметров params.yaml')     
        # Поиск файлов по маске
        filePaths = glob.glob('/var/lib/deployer/role_instances/core*/params.yaml')
        # Вывод найденных файлов
        for filePath in filePaths:
            with open(filePath, 'r') as file:
                for line in file:
                    if 'ClientSecret' in line:
                        logging.info('Найден MpxClientSecret в params.yaml')
                        MpxClientSecret = line.split(':')[1].strip()
                        return MpxClientSecret
    else:
        MpxClientSecret = input('Введите ClientSecret: ')
        return MpxClientSecret

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ получения токена доступа
def getTokenMpx():
    logging.info('Вызов функции getTokenMpx для получения токена доступа')
    if getYesNoInput('Использовать креды по умолчанию: Administrator/P@ssw0rd? Yes/No'):
        adminName = 'Administrator'
        adminPassword = 'P@ssw0rd'
    else:
        adminName = input('Введите логин пользователя MP10: ') 
        while True: 
            adminPassword = getpass.getpass('Введите пароль пользователя MP10: ')
            adminPasswordCheck = getpass.getpass('Повторите пароль пользователя MP10: ')
            if adminPassword != adminPasswordCheck:
                logging.error('Пароли при вводе не совпали.')
                print('Пароли не совпадают. Повторите попытку.')
                continue
            else:
                logging.info('Логин и пароль пользователя MP10 введены верно')
                break
    clientSecret = getMpxClientSecret()
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
        'scope':'authorization offline_access mpx.api',
    }
    getTokenUrl = rootUrl + ":3334/connect/token"
    #отправка запроса
    print('\nОтправляется запрос на получение токена доступа для mpx...')
    getAuthToken = sendAnyPostRequest(getTokenUrl, headersOfRequest, dataGetAuthToken, None, 'получение токена доступа для mpx')
    if getAuthToken is None:
        logging.error('Не удалось получить токен доступа. Вернулся объект None')
        return None
    else:
        logging.info('Токен доступа получен.')
        return getAuthToken.json()['access_token']


#-------------------------------------ГРУППЫ АКТИВОВ-------------------------------------#
#ГРУППЫ АКТИВОВ || ФУНКЦИЯ поиска id группы-родителя по ее имени
def findAssetsGroupID(parentName):
    logging.info(f'Вызов функции getGroupID для поиска id группы-родителя: {parentName}')
    
    # Запрос на получение информации о всех группах
    groupsUrl = f"{rootUrl}/api/assets_temporal_readmodel/v2/groups/hierarchy"
    headers = {'Authorization': f'Bearer {bearerToken}'}
    response = sendAnyGetRequest(groupsUrl, headers, None, None, f'поиск группы {parentName}')
    groupsData = response.json()

    # Поиск родительской группы активов по имени
    parentGroupId, found = findAssetsGroupIdRecursive(groupsData, parentName)
    if not found:
        logging.info(f'Родительская группа {parentName} для создаваемой группы не была найдена.')
        print(f"Внимание! Родительская группа {parentName} для создаваемой группы не была найдена. Создаваемая группа будет создана в корне.")
        parentGroupId = '00000000-0000-0000-0000-000000000002'  # Устанавливаем ID root
    else:
        logging.info(f'Родительская группа {parentName} была найдена и имеет id: {parentGroupId}')
        assetsGroupsDictionary[parentName] = parentGroupId
    return parentGroupId

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ рекурсивного поиска группы в подгруппах
def findAssetsGroupIdRecursive(groupsData, targetGroupName):
    logging.info(f'Вызов рекурсивной функции findAssetsGroupIdRecursive для поиска id группы: {targetGroupName}')

    # Поиск группы по имени в текущем уровне
    for group in groupsData:
        logging.info(f'Поиск группы {targetGroupName} в группе {group["name"]}.')
        if group["name"] == targetGroupName:
            return group["id"], True  # Группа найдена, возвращаем ID и True

        # Рекурсивный поиск во всех дочерних группах
        if "children" in group:
            result, found = findAssetsGroupIdRecursive(group["children"], targetGroupName)
            if found:
                return result, True
        
    return '00000000-0000-0000-0000-000000000002', False  # Группа не найдена, возвращаем ID root и False

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ проверки статуса создания группы
def checkGroupCreated(operationId, groupName):
    logging.info(f'Вызов функции checkGroupCreated для проверки статуса создания группы. {groupName}.')
    operationStatusUrl = f"{rootUrl}/api/assets_processing/v2/groups/operations/{operationId}"
    headers = {'Authorization': f'Bearer {bearerToken}'}
    while True:
        response = sendAnyGetRequest(operationStatusUrl, headers, None, None, f'проверку статуса создания группы {groupName}')
        if response is not None and response.status_code != 202:
            logging.info(f'Группа {groupName} создана. Ее ID {response.json()}')
            print(f'Группа {groupName} создана. Ее ID {response.json()}')
            assetsGroupsDictionary[groupName] = response.json()
            break
        elif response is not None:
            logging.info(f'На момент времени {datetime.now()} группа {groupName} еще создается.')
            print('Группа еще создается. Пожалуйста, подождите...')
            time.sleep(1)
        else:
            logging.error('Не удалось получить статус создания группы {groupName}. Вернулся объект None')
            break

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ групп CSV -> JSON + сохраняем на сервер
def createAssetsFromCsv(csvFilePath, assetsGroupsDictionary):
    logging.info('Вызов функции createAssetsFromCsv для создания групп активов из CSV файла.')
    # Открываем CSV-файл
    with open(csvFilePath, 'r', newline='', encoding='utf-8') as assetsGroupsFile:
        csvReader = csv.reader(assetsGroupsFile, delimiter=';') # Создаем читатель CSV
        next(csvReader)                                         # Пропускаем заголовок (первую строку)
        for row in csvReader:                                   # Обрабатываем оставшиеся строки
            print('-----------------------------------------------------------------------')
            logging.info(f'Выполянется чтение параметров для создания группы: {row[0]}')
            print(f'Выполянется чтение параметров для создания группы: {row[0]}')
            parentIdTemp = assetsGroupsDictionary.get(row[2])
            if parentIdTemp is None: parentIdTemp = findAssetsGroupID(row[2])
            # Создаем словарь для хранения данных текущей строки
            rowData = {
                "name": row[0],
                "description": row[1],
                "parentId": parentIdTemp,
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
                logging.info(f'Удален pdql-фильтр для группы {row[0]}')

            # отправляем запрос на создание группы
            print(f'Отправляется запрос на создание группы: {row[0]}')
            createAssetsGroupsUrl = rootUrl + '/api/assets_processing/v2/groups' 
            headers = {'Authorization': 'Bearer ' + bearerToken}
            createGroupsRequest = sendAnyPostRequest(createAssetsGroupsUrl, headers, None, rowData, f'создание группы {row[0]}')
            
            if createGroupsRequest is None:
                print(f'Произошла ошибка при создании группы {row[0]}. Группа не будет создана.')
                if getYesNoInput('Прервать создание групп?'):
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь прервал выполнение скрипта.')
                    break
                else:
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь продолжил выполнение скрипта.')
            else:
                #проверяем статус того, что группа создалась
                logging.info(f'Проверка создания группы: {row[0]}')
                checkGroupCreated(createGroupsRequest.json()["operationId"], row[0])
                print('\n')

#-------------------------------------PDQL ЗАПРОСЫ----------------------------------------#
#PDQL запросы || функция скачивания файла, содержащего информацию о группах PDQL запросов
def downloadPdqlGroupsData(querriesGroupsDictionary):
    logging.info('Вызвана функция downloadPdqlGroupsData для скачивания информации о группах PDQL запросов.')
    headers = {
        'Authorization': f'Bearer {bearerToken}',
        'content-type': 'application/json, text/plain, */*'
        }
    querriesHierarchyUrl = rootUrl + '/api/assets_temporal_readmodel/v1/stored_queries/folders/queries/'
    print("Выполняется актуализация информации об иерархии групп PDQL запросов.")
    response = sendAnyGetRequest(querriesHierarchyUrl, headers, None, None, "скачивание информации о группах PDQL запросов")
    response.raise_for_status()
    with open (querriesGroupsDictionary, 'w', encoding='utf-8') as querriesGroupsFile:
        json.dump(response.json(), querriesGroupsFile, ensure_ascii=False)
    print("Информация о текущей иерархии получена")
    logging.info("Информация о текущей иерархии групп записана в файл groupsOfQuerries.json")

#PDQL запросы || функция поиска ID группы в иерархии групп
def findQuerriesGroupId(groupsData, displayName):
    logging.info(f'Вызвана функция findQuerriesGroupId для поиска ID группы {displayName} в иерархии групп.')
    if not groupsData:
        return None

    for group in groupsData:
        if group["displayName"] == displayName:
            return group["id"]

        if "children" in group and group["children"]:
            result = findQuerriesGroupId(group["children"], displayName)
            if result:
                return result
    
    querriesGroupsDictionary[displayName] = group["id"]
    return None

#ЗАПРОСЫ PQDL || ФУНКЦИЯ создание групп для запросов
def createPdqlGroups(querriesGroupsCsvFile):
    # Читаем информацию о группах для запросов из файла pdql_groups_manifest.csv
    logging.info('Вызвана функция createPdqlGroups для создания групп PDQL запросов из файла pdql_groups_manifest.csv.')

    with open(querriesGroupsCsvFile, 'r', newline='', encoding='utf-8') as pdqGroupslManifestFile:
        csvReader = csv.reader(pdqGroupslManifestFile, delimiter=';')   # Создаем читатель CSV
        next(csvReader)                                                 # Пропускаем заголовок (первую строку)                               
        for row in csvReader:                                           # Обрабатываем оставшиеся строки
            print('-----------------------------------------------------------------------\n')
            logging.info(f'Выполняется чтение параметров для создания группы PDQL запросов: {row[0]}')
            print(f'Выполняется чтение параметров для создания группы PDQL запросов: {row[0]}')
            parentIdTemp = querriesGroupsDictionary.get(row[1])
            if parentIdTemp is None: parentIdTemp = findQuerriesGroupId(row[1], querriesGroupsJsonFile)
            #Параметры группы из текущей строки
            rowData = {
                "displayName": row[0],
                "parentId": parentIdTemp,
                "type": row[2]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {bearerToken}"
            }

            # Отправляем запрос на создание групп PDQL запросов
            print(f'Отправляется запрос на создание группы PDQL запросов: {row[0]}')
            createPdqlGroupsUrl = rootUrl + '/api/assets_temporal_readmodel/v1/stored_queries/folders/queries'
            createPdqlGroupsRequest = sendAnyPostRequest(createPdqlGroupsUrl, headers, None, rowData, f'создание группы запросов: {row[0]}')

            if createPdqlGroupsRequest.status_code == 200:
                logging.info(f'Группа {row[0]} создана успешно. Ее ID: {createPdqlGroupsRequest.json()["id"]}')
                print(f'Группа {row[0]} создана успешно. Ее ID: {createPdqlGroupsRequest.json()["id"]}')
                querriesGroupsDictionary[row[0]] = createPdqlGroupsRequest.json()["id"]
            else:
                print(f'Произошла ошибка при создании группы {row[0]}. Группа не будет создана. Необходимо ли остановить скрипт? Yes/No')
                if input() == 'Yes':
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь прервал выполнение скрипта.')
                    break
                else:
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь продолжил выполнение скрипта.')
            print('\n')

#ЗАПРОСЫ PDQL || ФУНКЦИЯ создание PDQL запросов
def createPdqlQueries(querriesCsvFile):
    logging.info('Вызвана функция createPdqlQueries для создания запросов.')
    with open(querriesCsvFile, 'r', newline='', encoding='utf-8') as pdqlQueriesFile:
        csvReader = csv.reader(pdqlQueriesFile, delimiter=';')
        next(csvReader)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearerToken}"
        }
        for row in csvReader:
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
            createQuerryUrl = rootUrl + "/api/assets_temporal_readmodel/v1/stored_queries/queries"
            print("Отправляется запрос на создание PDQL запроса: " + row[0])
            response = sendAnyPostRequest(createQuerryUrl, headers, None, rowData, f'создание PDQL запроса: {row[0]}')
            response.raise_for_status()
            if response.status_code == 200:
                print('PDQL запрос ' + row[0] + ' создан успешно. ID: ' + response.json()["id"] + '\n')


#-------------------------- INT MAIN --------------------------------------------
#--------------------ОСНОВНОЙ КОД ПРОГРАММЫ--------------------------------------

#пропускать ворнинги
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#глобальные переменные
bearerToken = None                                                          #токен MP10 Core
werePqlGroupsCreated = False                                                #флаг создания групп PDQL запросов нужен для PDQL запросов
assetsGroupsDictionary = {'Root':'00000000-0000-0000-0000-000000000002'}    #словарь с группами активов
querriesGroupsDictionary = {'CommonRootFolder':'CommonRootFolder'}          #словарь с группами PDQL запросов

#установление пути к файлам манифестам
currentDirectory = os.path.dirname(os.path.abspath(__file__))                           #текущая директория
manifestsDirectory = os.path.join(currentDirectory, 'deployment_manifests')             #директория с манифестами
groupsCsvFile = os.path.join(manifestsDirectory, "assets_groups_manifest.csv")          #манифест с настройками групп активов
querriesGroupsCsvFile = os.path.join(manifestsDirectory, "pdql_groups_manifest.csv")    #манифест с настройками групп PDQL запросов
querriesCsvFile = os.path.join(manifestsDirectory, "pdql_manifest.csv")                 #манифест с настройками PDQL запросов
querriesGroupsJsonFile = os.path.join(manifestsDirectory, "groupsOfQuerries.json")      #файл, куда скачаваем информацию о группах PDQL запросов

#логирование ошибок
loggingDirectory = os.path.join(currentDirectory, 'logging')                            #установление пути к директории с логами
if not os.path.exists(loggingDirectory):                                                #создание директории с логами, если ещё нет
    os.mkdir(loggingDirectory)                                                          #директория с логами
loggingFile = f"main-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}-log.log"            #имя лог файла
logging.basicConfig(                                                                    #настройка логирования
    filename=os.path.join(loggingDirectory, loggingFile),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logging.info('Программа запущена пользователем.')

#запрос корневой uRL и получение токена
print('-------------------------------Создание токена------------------------------\n')
while True:
    rootUrl = 'https://' + input('Введите адрес MP10 Core: https://')
    bearerToken = getTokenMpx()
    if bearerToken is None:
        print('Не удалось получить токен. Повторите попытку.\n')
    else:
        print('Токен получен.\n')
        break

#создание групп активов
print('-------------------------------Группы активов-------------------------------\n')
if(getYesNoInput(f'Необходимо ли создать группы активов из {groupsCsvFile} ?')): 
    print('\n')
    createAssetsFromCsv(groupsCsvFile, assetsGroupsDictionary)

downloadPdqlGroupsData(querriesGroupsJsonFile)
#создание групп PDQL запросов
print('-------------------------------Группы запросов------------------------------\n')
if(getYesNoInput(f'Необходимо ли создать группы PDQL запросов из {querriesGroupsCsvFile} ?')):
    createPdqlGroups(querriesGroupsCsvFile)
    print('\n')

#создание PDQL запросов
print('-------------------------------PDQL запросы----------------------------------\n')
if(getYesNoInput(f'Необходимо ли создать PDQL запросы из {querriesCsvFile}? Yes/No')):
    print('\n')
    createPdqlQueries(querriesCsvFile)

logging.info('Программа завершена.')
#print('Необходимо ли создать задачи? Yes/No')
#if(input() == 'Yes'): tasksCreate = True
#print('Необходимо ли создать учетные записи? Yes/No')
#if(input() == 'Yes'): accountsCreate = True