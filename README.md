# API конвертации валют

Это API для конвертации валют в реальном времени, поддерживающее как традиционные валюты, так и криптовалюты.

## Краткое описание

- Конвертация между различными валютами и криптовалютами
- Поддержка основных мировых валют и популярных криптовалют
- Данные из нескольких надежных источников
- Построено с использованием фреймворка Litestar
- Поддержка Docker для простого развертывания

## Запуск проекта

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/imelbow/concs.git
   cd currency-conversion-api
   ```

2. Добавьте файл `config.yaml` в корневой директории проекта с необходимыми API ключами и настройками.

3. Соберите Docker образ:
   ```bash
   docker build -t currency-conversion-api .
   ```

4. Запустите Docker контейнер:
   ```bash
   docker run -p 8000:8000 simple-litestar-converter
   ```

5. API будет доступно по адресу `http://localhost:8000`

## Использование

Пример запроса:
```
http://localhost:8000/v1/api/rates?from_currency=USD&to_currency=EUR&value=100
```

Документация Swagger доступна по адресу:
```
http://localhost:8000/schema
```

## Поддержка

При возникновении вопросов:
- Telegram: https://t.me/imelbow
- Email: lokdeaf@gmail.com