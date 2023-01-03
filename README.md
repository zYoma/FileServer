## FastApi File Server

API-сервис для хранения файлов.
Файловое хранилище, которое позволяет хранить различные типы файлов - документы, фотографии, другие данные.

## Стек

- Python3.11
- FastApi
- Postgresql
- Redis


Сервис развернут на сервере в 3-х Docker-контейнерах:

    - Postgres
    - Redis
    - FastApi

Документация к API доступна по адресу: http://111/api/openapi

## Описание методов

<details>
<summary> Список доступных эндпойнтов </summary>

1. Статус активности связанных сервисов

```
GET /ping
```
Получить информацию о времени доступа ко всем связанным сервисам.

**Response**
```json
{
    "db": 1.27,
    "cache": 1.89,
}
```

2. Регистрация пользователя.

```
POST /register
```
Регистрация нового пользователя. Запрос принимает на вход логин и пароль для создания новой учетной записи.


3. Авторизация пользователя.

```
POST /auth
```
Запрос принимает на вход логин и пароль учетной записи и возвращает авторизационный токен. Далее все запросы проверяют наличие токена в заголовках - `Authorization: Bearer <token>`


4. Информация о загруженных файлах

```
GET /files/list
```
Возвращает информацию о ранее загруженных файлах. Доступно только авторизованному пользователю.

**Response**
```json
{
    "files": [
          {
            "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
            "name": "notes.txt",
            "created_ad": "2020-09-11T17:22:05Z",
            "path": "/homework/test-fodler/notes.txt",
            "size": 8512,
            "user_id": "c382f541-c2e7-42a2-9a7b-6cd091061325",
            "directory_id": "3fdeb8a0-7b8f-4b4b-9bbd-c71b31bcc8b9",
          },
        ...
          {
            "id": "113c7ab9-2300-41c7-9519-91ecbc527de1",
            "name": "tree-picture.png",
            "created_ad": "2019-06-19T13:05:21Z",
            "path": "/homework/work-folder/environment/tree-picture.png",
            "size": 1945,
            "user_id": "c382f541-c2e7-42a2-9a7b-6cd091061325",
            "directory_id": "d6c79512-5e27-4d25-bfb3-0b52f778d4a3",
          }
    ]
}
```


5. Загрузить файл в хранилище

```
POST /files/upload
```
Метод загрузки файла в хранилище. Доступно только авторизованному пользователю.
Для загрузки заполняется полный путь до файла, в который будет загружен/переписан загружаемый файл. Если нужные директории не существуют, то они будут созданы автоматически.
Так же, есть возможность указать путь до директории. В этом случае имя создаваемого файла будет создано в соответствии с текущим передаваемым именем файла.

**Request parameters**
```
{
    "path": <full-path-to-save-file>||<path-to-folder>,
}
```
**Response**
```json
{
    "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
    "name": "notes.txt",
    "created_ad": "2020-09-11T17:22:05Z",
    "path": "/homework/test-fodler/notes.txt",
    "size": 8512,
    "is_downloadable": true
}
```


6. Скачать загруженный файл

```
GET /files/download
```
Скачивание ранее загруженного файла. Доступно только авторизованному пользователю.

**Path parameters**
```
/?path=[<path-to-file>||<file-meta-id>||<path-to-folder>||<folder-meta-id>]
```
Возможность скачивания есть как по переданному пути до файла, так и по идентификатору.
Есть возможности скачивания директории в архиве.
Можно указать как путь до директории, так и ее **UUID**. При скачивании директории будут скачиваться все файлы, находящиеся в ней.

7. Информация об использовании пользователем дискового пространства.

```
GET /user/status
```

Возвращает информацию о статусе использования дискового пространства и ранее загруженных файлах. Доступно только авторизованному пользователю.

**Response**
```json
{
    "info": {
        "account_id": "taONIb-OurWxbNQ6ywGRopQngc",
        "home_folder_id": "19f25-3235641",
    },
    "folders": [
        "root": {
            "used": 395870,
            "files": 89
        },
        "home": {
            "used": 539,
            "files": 19
        },
        ...,
        "folder-188734": {
            "used": 79,
            "files": 2
      }
    ]
}
```

8.  Поиск файлов по заданным параметрам

```
GET /files/search
```

Возвращает информацию о загруженных файлах по заданным параметрам. Доступно только авторизованному пользователю.

**Request**
```json
{
    "options": {
        "path": <folder-id-to-search>,
        "extension": <file-extension>,
        "order_by": <field-to-order-search-result>,
        "limit": <max-number-of-results>
    },
    "query": "<any-text||regex>"
}
```

**Response**
```json
{
    "matches": [
          {
            "id": "113c7ab9-2300-41c7-9519-91ecbc527de1",
            "name": "tree-picture.png",
            "created_ad": "2019-06-19T13:05:21Z",
            "path": "/homework/work-folder/environment/tree-picture.png",
            "size": 1945,
          },
        ...
    ]
}
```

9. Поддержка версионирования изменений файлов.

```
GET /files/revisions
```

Возвращает информацию о изменениях файла по заданным параметрам. Доступно только авторизованному пользователю.

**Request**
```json
{
    "path": <path-to-file>||<file-meta-id>,
    "limit": <max-number-of-results>
}
```

**Response**
```json
{
    "revisions": [
          {
            "id": "b1863132-5db6-44fe-9d34-b944ab06ad81",
            "name": "presentation.pptx",
            "created_ad": "2020-09-11T17:22:05Z",
            "path": "/homework/learning/presentation.pptx",
            "rev_id": "676ffc2a-a9a5-47f6-905e-99e024ca8ac8",
            "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "modified_at": "2020-09-21T05:13:49Z"
          },
        ...
    ]
}
```

</details>



## Запуск
```
docker-compose build app
docker-compose up -d app
или
make up - запуск
make build - создать контейнеры
make shell - запустить контейнер с приложением и войти в bash
make test   - запустить автотесты
make makemigrations args=name - создать миграции
make migrate  - запустить alembic upgrade head (все миграции)
make migrate_downgrade - запустить alembic downgrade -1 (откатить на 1 миграцию назад)

```

### Тестирование

Перед запуском тестов, необходимо создать для них БД с тем же паролем.
```
create database postgres_test;
GRANT ALL PRIVILEGES ON DATABASE postgres_test TO postgres;
```

### Переменные окружения

| Название| Описание                                      | Пример значения                                                  |
|---|-----------------------------------------------|------------------------------------------------------------------|
| SECRET_KEY | соль для паролей                              | 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7 |
| DOCKER_COMPOSE_FILE | имя файла композ                              | docker-compose.yml                                               |
| SERVICE_NAME | название сервиса с приложением в композ файле | app                                                              |
| DOCKER_APP_PORT | публичный порт приложения                     | 8000                                                             |
| DOCKER_POSTGRES_PORT | порт БД в контейнере                          | 5432                                                             |
| DOCKER_REDIS_PORT | порт redis в контейнере                       | 6379                                                             |
| RW_DSN | DSN базы данных                               | postgresql+asyncpg://postgres@postgres:5432/postgres             |
| POSTGRES_PASSWORD | пароль БД                                     | postgres       |
| REDIS_DSN | DSN redis                                     | redis://redis:6379/1       |
| LOG_LEVEL | уровень логирования                           | INFO                                                             |
| SQL_ECHO | логирование sql запросов                      | false                                                            |
| STATIC_ROOT | директория для статических файлов             | static/                                                          |





