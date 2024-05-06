import logging
import requests

def sendAnyPostRequest(requestMethod, requestUrl, headers, data, jsonData, requestPurpose):
    try:
        if jsonData:
            logging.info(f'Отправляется {requestMethod} запрос для {requestPurpose} с JSON данными на URL: {requestUrl}')
            if requestMethod == 'GET':
                response = requests.get(requestUrl, headers=headers, json=jsonData, verify=False)
            elif requestMethod == 'POST':
                response = requests.post(requestUrl, headers=headers, json=jsonData, verify=False)
        else:
            logging.info(f'Отправляется {requestMethod} запрос для {requestPurpose} с DATA данными на URL: {requestUrl}')
            if requestMethod == 'GET':
                response = requests.get(requestUrl, headers=headers, data=data, verify=False)
            elif requestMethod == 'POST':
                response = requests.post(requestUrl, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logging.info(f'Запрос выполнен успешно. Статус код: {response.status_code}')
        return response
    
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP-ошибка при выполнении запроса на URL: {requestUrl}:\n{err}')
        if response.text: logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла HTTP-ошибка при выполнении запроса для {requestPurpose}.\nЛоги находятся в файле {loggingDirectory}+{loggingFile}')
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f'Ошибка отправки запроса на {requestPurpose} на UFL: {requestUrl}:\n{err}')
        if response.text: logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла ошибка отправки запроса для {requestPurpose}.\nЛоги находятся в файле {loggingDirectory}+{loggingFile}')
        return None
    
    except Exception as err:
        logging.error(f'Неизвестная ошибка при выполнении запроса на URL: {requestUrl}:\n{err}')
        if response.text: logging.error(f'Ответ сервера на запрос: \n{response.text}')
        print(f'Произошла неизвестная ошибка при выполнении запроса на {requestPurpose}.\nЛоги находятся в файле {loggingDirectory}+{loggingFile}')
        return None

responce = sendAnyGetRequest(url, headers, data, None, 'запрос')