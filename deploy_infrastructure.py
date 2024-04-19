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
required_libraries = ['datetime', 'csv', 'getpass', 'json', 'logging', 'os', 'requests', 'time', 'urllib3']

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
import json
import logging
import os
import requests
import time
import urllib3

#-------------------------------------ГЛОБАЛЬНЫЕ-----------------------------------------#
#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ получения ввода Yes / No от юзера
def getYesNoInput(Action):
    print(Action)
    logging.info(f'Пользователя спросили {Action}.')
    while True:
        inputAnswer = input('[Yes, Y, Да, Д| / [No, N, Нет, Н]: ').strip().lower()
        if inputAnswer in ['yes', 'y', 'да', 'д']:
            logging.info('Пользователь согласился на действие.')
            return True
        elif inputAnswer in ['no', 'n', 'нет', 'н']:
            logging.info('Пользователь отказался от действия.')
            return False
        else:
            logging.error('Некорректный ввод от пользователя.')
            print('Некорректный ввод. Повторите попытку.')

#ГЛОБАЛЬНЫЕ || ФУНКЦИЯ универсальная отправки POST запроса 
def sendAnyPostRequest(requestUrl, headers, data, jsonData, requestType):
    try:
        if jsonData:
            logging.info(f'Отправлен POST запрос на {requestType} с JSON данными на url {requestUrl}')
            response = requests.post(requestUrl, headers=headers, json=jsonData, verify=False)
        else:
            logging.info(f'Отправлен POST запрос на {requestType} с данными на url {requestUrl}')
            response = requests.post(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logging.info(f'Запрос на {requestType} выполнен успешно на url {requestUrl}. Статус код: {response.status_code}')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении {requestType} запроса на {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка при выполнении запроса на {requestType}. Логи находятся в {loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestType} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка при выполнении запроса на {requestType}. Логи находятся в {loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestType} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка при выполнении запроса на {requestType}. Логи находятся в {loggingFile}')
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
    logging.info('Вызов функции getTokenMpx для получения токена доступа')
    if getYesNoInput('Использовать креды по умолчанию: Administrator/P@ssw0rd? Yes/No'):
        adminName = 'Administrator'
        adminPassword = 'P@ssw0rd'
    else:
        adminName = input('Введите логин пользователя MP10: ') 
        #ввод логина и пароля
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
    #ввод clientSecret
    clientSecret = input('Введите clientSecret: ')
    logging.info('Введен clientSecret')

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
    print('\nОтправляется запрос на получение токена доступа для mpx...')
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
    logging.info(f'Вызов функции getGroupID для поиска id группы-родителя: {parentName}')
    
    # Запрос на получение информации о всех группах
    groupsUrl = f"{rootUrl}/api/assets_temporal_readmodel/v2/groups/hierarchy"
    headers = {'Authorization': f'Bearer {bearerToken}'}
    response = sendAnyGetRequest(groupsUrl, headers, None, None, f'поиск группы {parentName}')
    groupsData = response.json()

    # Поиск родительской группы по имени
    parentGroupId, found = findGroupIdRecursive(groupsData, parentName)
    if not found:
        logging.info(f'Родительская группа {parentName} для создаваемой группы не была найдена.')
        print(f"Внимание! Родительская группа {parentName} для создаваемой группы не была найдена. Создаваемая группа будет создана в корне.")
        parentGroupId = '00000000-0000-0000-0000-000000000002'  # Устанавливаем ID root
    else:
        logging.info(f'Родительская группа {parentName} была найдена и имеет id: {parentGroupId}')
    return parentGroupId

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ рекурсивного поиска группы в подгруппах
def findGroupIdRecursive(groupsData, targetGroupName):
    logging.info(f'Вызов рекурсивной функции findGroupIdRecursive для поиска id группы: {targetGroupName}')

    # Поиск группы по имени в текущем уровне
    for group in groupsData:
        logging.info(f'Поиск группы {targetGroupName} в группе {group["name"]}.')
        if group["name"] == targetGroupName:
            return group["id"], True  # Группа найдена, возвращаем ID и True

        # Рекурсивный поиск во всех дочерних группах
        if "children" in group:
            result, found = findGroupIdRecursive(group["children"], targetGroupName)
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
            break
        elif response is not None:
            logging.info(f'На момент времени {datetime.now()} группа {groupName} еще создается.')
            print('Группа не создана. Пожалуйста, подождите...')
            time.sleep(1)
        else:
            logging.error('Не удалось получить статус создания группы {groupName}. Вернулся объект None')
            break

#ГРУППЫ АКТИВОВ || ФУНКЦИЯ групп CSV -> JSON + сохраняем на сервер
def createAssetsFromCsv(csvFilePath):
    logging.info('Вызов функции createAssetsFromCsv для создания групп активов из CSV файла.')
    # Открываем CSV-файл
    with open(csvFilePath, 'r', newline='', encoding='utf-8') as assetsGroupsFile:
        csvReader = csv.reader(assetsGroupsFile, delimiter=';') # Создаем читатель CSV
        next(csvReader)                                         # Пропускаем заголовок (первую строку)
        for row in csvReader:                                   # Обрабатываем оставшиеся строки
            print('-----------------------------------------------------------------------')
            logging.info(f'Выполянется чтение параметров для создания группы: {row[0]}')
            print(f'Выполянется чтение параметров для создания группы: {row[0]}')
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
                logging.info(f'Удален pdql-фильтр для группы {row[0]}')

            # отправляем запрос на создание группы
            print(f'Отправляется запрос на создание группы: {row[0]}')
            createGroupsUrl = rootUrl + '/api/assets_processing/v2/groups' 
            headers = {'Authorization': 'Bearer ' + bearerToken}
            createGroupsRequest = sendAnyPostRequest(createGroupsUrl, headers, None, rowData, f'создание группы {row[0]}')
            
            if createGroupsRequest is None:
                print(f'Произошла ошибка при создании группы {row[0]}. Группа не будет создана. Необходимо ли остановить скрипт? Yes/No')
                if input() == 'Yes':
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь прервал выполнение скрипта.')
                    break
                else:
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь продолжил выполнение скрипта.')
            else:
                #проверяем статус того, что группа создалась
                print(f'Проверка создания группы: {row[0]}')
                checkGroupCreated(createGroupsRequest.json()["operationId"], row[0])
                print('\n')

#-------------------------------------PDQL ЗАПРОСЫ----------------------------------------#
#ЗАПРОСЫ PQDL || ФУНКЦИЯ поиска id группы запросов по ее displayName имени в файле groupsOfQuerries.json, если группы не создавались в программе
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

#ЗАПРОСЫ PDQL || ФУНКЦИЯ поиска id группы по ее имени в словаре, если группы создавались в программе
def searchInDictionary(keyName):
    logging.info(f'Вызов функции searchInDictionary для поиска id группы {keyName}.')
    if keyName in pgqlGroupsDictionary:
        logging.info(f'Группа {keyName} найдена в словаре созданных ранее групп. Имеет ID {pgqlGroupsDictionary[keyName]}')
        return pgqlGroupsDictionary[keyName]
    else:
        logging.info(f'Группа {keyName} не найдена в словаре созданных ранее групп.')
        print('Создаваемая группа будет в группе Общие запросы.')
        return 'CommonRootFolder'

#ЗАПРОСЫ PQDL || ФУНКЦИЯ создание группы для запросов
def createPdqlGroups(querriesGroupsCsvFile):
    # Читаем информацию о группах для запросов из файла pdql_groups_manifest.csv
    logging.info('Вызвана функция createPdqlGroups для создания групп PDQL запросов из файла pdql_groups_manifest.csv.')

    with open(querriesGroupsCsvFile, 'r', newline='', encoding='utf-8') as pdqGroupslManifestFile:
        csvReader = csv.reader(pdqGroupslManifestFile, delimiter=';')         # Создаем читатель CSV
        next(csvReader)                                                 # Пропускаем заголовок (первую строку)                               
        for row in csvReader:                                           # Обрабатываем оставшиеся строки
            print('-----------------------------------------------------------------------\n')
            logging.info(f'Выполняется чтение параметров для создания группы PDQL запросов: {row[0]}')
            print(f'Выполняется чтение параметров для создания группы PDQL запросов: {row[0]}')
            #Параметры группы из текущей строки
            rowData = {
                "displayName": row[0],
                "parentId": pgqlGroupsDictionary.get(row[1], findGroupId(row[1])),
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
                pgqlGroupsDictionary[row[0]] = createPdqlGroupsRequest.json()["id"]
            else:
                print(f'Произошла ошибка при создании группы {row[0]}. Группа не будет создана. Необходимо ли остановить скрипт? Yes/No')
                if input() == 'Yes':
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь прервал выполнение скрипта.')
                    break
                else:
                    logging.error(f'Не удалось создать группу {row[0]}. Пользователь продолжил выполнение скрипта.')
            print('\n')

#ЗАПРОСЫ PDQL || ФУНКЦИЯ создание pdql запросов с использованием словаря содержащего соотнесение созданных групп PDQL запросов и PDQL запросов
def createPdqlQueriesWithDictionary(querriesCsvFile):
    logging.info('Вызвана функция createPdqlQueriesWithDictionary для создания групп запросов с использованием локального словаря.')
    with open(querriesCsvFile, 'r', newline='', encoding='utf-8') as pdqlQueriesFile:
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

def createPdqlQueriesWuthRequest(querriesCsvFile):
    return None

#-------------------------- INT MAIN --------------------------------------------
#--------------------ОСНОВНОЙ КОД ПРОГРАММЫ--------------------------------------

#пропускать ворнинги
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#глобальные переменные
bearerToken = None                      #токен MP10 Core
werePqlGroupsCreated = False            #флаг создания групп PDQL запросов нужен для PDQL запросов
assetsGroupsDictionary = {}             #словарь с группами активов
pgqlGroupsDictionary = {}               #словарь с группами PDQL запросов

#установление пути к файлам манифестам
currentDirectory = os.path.dirname(os.path.abspath(__file__))                           #текущая директория
manifestsDirectory = os.path.join(currentDirectory, 'deployment_manifests')             #директория с манифестами
groupsCsvFile = os.path.join(manifestsDirectory, "assets_groups_manifest.csv")          #манифест с настройками групп активов
querriesGroupsCsvFile = os.path.join(manifestsDirectory, "pdql_groups_manifest.csv")    #манифест с настройками групп PDQL запросов
querriesCsvFile = os.path.join(manifestsDirectory, "pdql_manifest.csv")                 #манифест с настройками PDQL запросов
#querriesGroupsCsvFile = os.path.join(manifestsDirectory, "groupsOfQuerries.json")      #файл, куда скачаваем информацию о группах PDQL запросов

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
    createAssetsFromCsv(groupsCsvFile)

#создание групп PDQL запросов
print('-------------------------------Группы запросов------------------------------\n')
if(getYesNoInput(f'Необходимо ли создать группы PDQL запросов из {querriesGroupsCsvFile} ?')):
    print('\n')
    createPdqlGroups(querriesGroupsCsvFile)
    werePqlGroupsCreated = True

#создание PDQL запросов
print('-------------------------------PDQL запросы----------------------------------\n')
if(getYesNoInput(f'Необходимо ли создать PDQL запросы из {querriesCsvFile}? Yes/No')):
    print('\n')
    if werePqlGroupsCreated:
        createPdqlQueriesWithDictionary(querriesCsvFile)
    else:
        createPdqlQueriesWuthRequest(querriesCsvFile)

logging.info('Программа завершена.')
#print('Необходимо ли создать задачи? Yes/No')
#if(input() == 'Yes'): tasksCreate = True
#print('Необходимо ли создать учетные записи? Yes/No')
#if(input() == 'Yes'): accountsCreate = True