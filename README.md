# Описание
Приложение, автоматизирующее сохранение звонков из сервиса "Скорозвон" в Битрикс24, а также формирующее отчеты в гугл-таблицах и телеграме об успешных сделках. <br>
Первая часть приложения - получение данных о сохраненном звонке с вебхука в "Скорозвоне" и создание сделки в Битрикс24 с этими данными, если звонок прошел успешно. Помимо прочего, учитывается проект, по которому был совершен звонок, и, основывываясь на этом, выбирается воронка, где сделка будет создана. <br>
Вторая часть приложения - формирование отчетов. После того, как оператор пометил сделку как валидную, происходит проверка на дубли и последующая рассылка в соответсвующий данной воронке телеграм чат и гугл-таблицу.

# Используемые технологии
- backend: django rest framework;
- субд: postgres;

# Пример работы
### 1. Создание сделки по данным скорозвона
Эмуляция срабатывания вебхука:
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/534b42d9-39a2-453a-ae56-4c6dbb1b5767)<br>

Созданная сделка в Битрикс:
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/a9035039-7d8b-4108-a500-318994760e3f)<br>

### 2. Пометка сделки как валидной
#### 2.1 Недублирующаяся сделка
Перенос на стадию "Отправить лид" <br>
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/441ed516-fc15-4b02-9f2c-811aa12aada1)<br>
Добавление в отчет <br>
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/bb1207a2-6101-4a7d-ac80-0f0ff12e90b6)<br>
#### 2.2 Дублирующаяся сделка
Автоматический перенос в стадию "Дубли" <br>
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/ee0975e5-a72f-4299-a8ea-4af64e1fab57)<br>
Сделка не заносится в отчет повторно <br>
![image](https://github.com/aovsybo/B24_skorozvon_integration/assets/66824112/42dd9834-110f-4f94-b963-41b5e362fb51)<br>
