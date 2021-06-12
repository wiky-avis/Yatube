# Yatube – социальная сеть для публикации дневников.

## Стек:
Python 3, Django 2.2 LST, PostgreSQL, pytest, unittest.

## Описание:
Реализован пользовательский функционал:
*	Создание, редактирование и удаление постов.
*	Пагинация постов и кэширование.
*	Регистрация с верификацией данных, сменой и восстановлением пароля.
*	Профиль пользователя с возможностью редактирования личных данных.
*	Личные сообщения.
*	Возможность подиски и отписки на авторов.
*	Поиск по сайту.
*	Возможность комментировать посты.

Сайт выложен в сеть и доступен по адресу [Yatube](http://stroymart.pythonanywhere.com/)

## Установка:
Клонируем репозиторий на локальную машину:
```$ git clone https://github.com/wiky-avis/Yatube.git```

Создаем виртуальное окружение:
```$ python -m venv venv```

Устанавливаем зависимости:
```$ pip install -r requirements.txt```

Создание и применение миграций:
```$ python manage.py makemigrations``` и ```$ python manage.py migrate```

Создаем суперпользователя:
```$ python manage.py createsuperuser --email admin@admin.com --username admin```

Запускаем django сервер:
```$ python manage.py runserver```

## Примеры страниц:
https://recordit.co/lxtDC6a9oV

