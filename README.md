

![example workflow](https://github.com/HoodFast/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)


#### Проект доступен по адресу http://51.250.107.11/

#### Документация доступна по адресу http://51.250.107.11/api/docs/

Foodgram приложение для публикации рецептов. Пользователи могут публиковать свои рецепты,
подписываться на понравившиеся рецепты и понравившихся авторов. Так же есть возможность 
сформировать список продуктов на основе выбраных рецептов.Список продуктов скачивается в формате PDF

## Для запуска проекта необходимо:

#### Создать Fork и склонировать репозиторий на локальную машину:

#### Отредактировать файл infra/nginx/default.conf
- отредактируйте файл infra/nginx/default.conf
- в строке server_name необходимо вписать 127.0.0.1

Cоздайте .env файл в папке проекта:

    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ> 
    ```
для запуска локально находясь в /infra выполните команду:

    ```
    docker-compose up
    ```


#### Для запуска на удаленном сервере:
- оредактируйте файл infra/nginx/default.conf
- в строке server_name необходимо вписать IP своего сервера

- Установите на сервер docker и docker-compose
- Скопируйте файлы docker-compose.yml и default.conf из директории infra и infra/nginx на сервер


Cоздайте на сервере .env файл:

    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ> 
    ```
Добавьте в Secrets GitHub переменные:

    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ>

    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя DockerHub>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для ssh, если он имеется>
    SSH_KEY=<SSH ключ>

    TELEGRAM_TO=<ID чата>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
 
После команды git push Workflow автоматически развернет проект на удаленном сервере. 

После успешного деплоя выполните команды:
    
    ```
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    ```
    ```
    sudo docker-compose exec backend python manage.py migrate --noinput
    ```
    - Загрузите ингридиенты  в базу данных:  
    ```
    sudo docker-compose exec backend python manage.py load_ingredients
    ```
    - Для создания суперпользователя введите команду:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    ```

#### Автор Андрей Кузнецов