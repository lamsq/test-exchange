Проект запрашивает курсы валют (exchangerate-api.com) через заданный промежуток времени.

Полученные данные сохраняются в тамблице responses БД, ошибки в logs/.

Создайте копию .env, заполните ключ API для exchangerate-api.com, запустите сборки образа и запуска контейнера 'docker-compose up --build'.

Select * from requests left join responses on responses.request_id = requests.id; //Выгрузка запросов и связанных ответов
