import logging
import requests

def sendAnyPostRequest(requestType, requestUrl, headers, data, jsonData, requestPurpose):

    try:
        if jsonData:
            logging.info(f'Отправляется POST запрос на {requestPurpose} с JSON данными на URL: {requestUrl}')
            response = requests.post(requestUrl, headers=headers, json=jsonData, verify=False)
        else:
            logging.info(f'Отправляется POST запрос на {requestPurpose} с DATA данными на URL: {requestUrl}')
            response = requests.post(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logging.info(f'Запрос на {requestPurpose} выполнен успешно на url {requestUrl}. Статус код: {response.status_code}')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении запроса на URL: {requestUrl}:\n {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла HTTP-ошибка при выполнении запроса на {requestPurpose}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestPurpose} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка отправки запроса {requestPurpose}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на {requestPurpose} на url {requestUrl}: {err}')
        logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла неизвестная ошибка при выполнении запроса на {requestPurpose}.\nЛоги находятся в {loggingDirectory}+{loggingFile}')
        return None

responce = sendAnyGetRequest(url, headers, data, None, 'запрос')