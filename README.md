# Телеграм Бот

## Запуск

### Зміна даних у віртуальному оточенні

Відкриваємо .env файл, у ньому вписуємо:
`BOT__TOKEN` - Токен бота
`KEY__OPENAI` - Ключ від OpenAI
`DB__NAME` - Бажана назва БД
`DB__PASSWORD` - Бажаний пароль БД

### Створення контейнерів БД та бота

Після заміни даних та заливу бота, відкриваємо його папку, у якій знаходиться файл `docker-compose.yml`

Запускаємо команду 
```shell
docker-compose up --build
```

Після чого підвантажуємо міграцію до БД 
```shell
docker-compose exec bot alembic upgrade head
```


### Адміна

Для отримання статусу адміна можна використати команду в боті: `/1af705e0-1689-40a6-8b29-fb6fec3a81b3`