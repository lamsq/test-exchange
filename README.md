Проект запрашивает курсы валют (exchangerate-api.com) через заданный промежуток времени.
Полученные данные сохраняются в таблице responses БД, ошибки в logs/.

<li>Создайте копию .env, заполните ключ API для exchangerate-api.com</br>
<li>Запустите сборку образа и запустите контейнер 'docker-compose up --build'.

<b><i>Выгрузка запросов и связанных ответов:</i></b></br>
Select * from requests left join responses on responses.request_id = requests.id; 
