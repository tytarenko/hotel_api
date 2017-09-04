mkdir hotels and cd ./hotels
git clone

(mkvirtualenv -p python2 hotels)

pip install -r requirements.txt
make mkdb
make run


База даних


Із таблиці rooms слід виділити в окрему таблицю поле price, та із таблиці booking поле cost. Це дозволить
потім створювати гнучку систему оплати із різними знижками, купонами та акціями + обмеження у часі.
Наприклад "якщо ви сьогодні забрноюєте на поточний місяц номер то отримаєти знижку в 40%".

В таблиці rooms поле options також слід виділити в окему таблицю.
це дозволить не дублювати певні опціх в описі номерів.
Наприклад "панорамний вигляд", "wifi" тощо

В таблицю type слід додати поле "кількість місць у номері"
та поле що вказує чи одне двоспальне ліжко чи два окремих тощо.


Додаток


Слід додати авторизацію, та ACL. Та декілька ролей - користувач, адміністратор тощо.
Обмежити доступ для користувачів лише рєєстація, керування аккаунтом, керування бронюванням.

Додати інтерграцію із платіжною системою що б номери можна було не тільки бронювати а і оплачувати одразу.

Задачі які ще слід вирішити:
Наразі я не реалізував http методи put & delete для усіх моделей.
Для цього потрібно вирвшувати конфлікти:
    - Редагування параметрів бронювання дати заїзву-відїзду або типу номера, якщо бронювання вже оплочено.
    - Видалення бронювання, якщо воно оплачено, але дати ще актуальне.
    - Редагування чи видалення (тип, опції тощо) кімнати, якщо на неї є оплочене бронювання.
    - Видалення користувача, у якого є актуальні оплочені бронювання.


API

Часткова відповідь

Для того щоб отримати лише певні поля моделі, потрібно додати до запиту параметр fields і перерахувати через кому
необхідні поля

http://localhost:8080/api/v1/rooms/?fields=id,type

Навігація.

Peewee дозволяє із коробки отримати pagination використовуючи LIMIT OFFSET. У більшості sql подібних базах данних
таке рішення має недолік, OFFSET все таки поелементно пробігає діапазон на який потрібно
зміститись.
Альтернативний варіант запам'ятовувавти перший і останній індекс у отриманій колекції або/i або дату + сортування
та на основі її будувати запити через WHERE

WHEREt1.id BETWEEN last_index AND last_index + 25.

Також слід додати кешування першої "сторінки" (кожний раз при додаванні нових записів до бази),
оскільки вона найчастіше і найбільше створює навантаження.

Написати детальну частину опрацювання кодів відоповідей HTTP
із зрозумілим месседжем та посиланням на детальний опис помилкита можливі шляхи його вирішення
для найбільш вживаніших кодів
200 201 304 400 401 403 404 405 409 410 500
