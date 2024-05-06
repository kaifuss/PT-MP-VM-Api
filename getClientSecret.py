import os
import glob

def getClientSecret():
    #logging.info('Вызов функции getClientSecret для получения clientSecret')

    deployerPath = os.path.dirname('/var/lib/deployer')
    deployedRolesPath = os.path.dirname('/var/lib/deployed-roles/Deployment-Application')

    if os.path.exists(deployerPath) and os.path.exists(deployedRolesPath):
        print('Скрипт запущен на сервере с ролью Deployer. CLientSecret будет взят из параметров params.yaml')     
        # Поиск файлов по маске
        filePaths = glob.glob('/var/lib/deployer/role_instances/core*/params.yaml')
        # Вывод найденных файлов
        for filePath in filePaths:
            with open(filePath, 'r') as file:
                for line in file:
                    if 'ClientSecret' in line:
                        #logging.info('Найден clientSecret в params.yaml')
                        clientSecret = line.split(':')[1].strip()
                        return clientSecret
    else:
        clientSecret = input('Введите ClientSecret: ')
        return clientSecret
    
print(getClientSecret())