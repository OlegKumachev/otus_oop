# Сервис скоринга OTUS

Этот проект представляет собой веб-сервер для HTTP API сервиса скоринга, написанный на Python. Сервис принимает POST-запросы с JSON-данными и выполняет их валидацию, аутентификацию и обработку.

## Структура проекта
```
├── api.py
├── app.log
├── README.md
├── requirements.txt
├── scoring.py
├── setup.cfg
└── test.py
```


## Описание

### api.py

Основной файл проекта, содержащий:

- Метакласс `FieldsMeta` для автоматического сбора полей классов запросов.
- Базовый класс `BaseRequest` для общих полей и валидации.
- Классы `OnlineScoreRequest` и `ClientsInterestsRequest` для конкретных методов.
- Функцию `check_auth` для проверки аутентификации.
- Обработчик `method_handler` для обработки запросов.
- Класс `MainHTTPHandler` для обработки HTTP-запросов.

### scoring.py

Модуль с функциями для вычисления скора и генерации интересов:

- `get_score` — функция для расчёта скора на основе переданных данных.
- `get_interests` — функция для генерации списка интересов.

### Требования

Для работы с этим API необходимо:

- Python 3.10+
- Зависимости из `requirements.txt`

### Установка 

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt


# Запуск 

    python api.py -p 8080

### Запуск с лог файлом 
    python api.py -p 8080 -l app.log


### Пример запроса 

```
curl -X POST -H "Content-Type: application/json" \
-d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав", "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' \
http://127.0.0.1:8080/method/
  ```

### Запуск тестов 
```
pytest test.py -v
```

### Формат запроса 
```
{
    "account": "<имя компании партнёра>",
    "login": "<имя пользователя>",
    "method": "<имя метода>",
    "token": "<токен>",
    "arguments": {"<аргументы метода>"}
}
```

### Пример запроса 

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав", "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' \
  http://127.0.0.1:8080/method/
```

