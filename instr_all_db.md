# Инструкция подготовки к запуску тестового комплекса баз данных
**_Саму программу тестового комплекса следует запускать так:_**
```
cd /mnt/poligon/html_bootstrap_js/
conda deactivate
source venv/bin/activate
./run.py
```
<br>и потом следует зайти на http://localhost:5000/login
<br>где надо выбрать свой позывной и ввести пароль
<br>или зайти по адресу http://localhost:5000/register
<br>и зарегистрироваться
<br>потом залогиниться и выбрать нужную БД, которая:
<br>перед этим должна быть запущена и ее поставщики также.

## Список баз данных в данном комплексе:
- QuestDB       база данных временных рядов 
- RethinkDB     база данных временных рядов
- TimescaleDB   база данных временных рядов
- SQLite        база данных Python
- PostgreSQL    SQL база данных 
- MongoDB       база данных документов
- Redis         база данных бысстрых запросов
- RabbitMQ      брокер сообщений

<br>Предполгается, что все базы данных уже установлены на локальной машине
<br>или на удаленной машине по адресу user:password:<url>:port_bd или
<br>без пароля по адресу <url>:port_bd

## Порядок подготовки и запуска тестового комплекса баз данных по каждой базе данных:
**_1. QuestDB      подготовка и запуск_**
- БД QuestDB по ssh starmark@gitlab.ivl.ua скопирована на удаленную машину вместе с: 
* Dockerfile
* Questdb_Rest_API.md
* docker-compose.yml
* questdb_start.sh*
* quick_start.md
* reader.py*

- Dockerfile:
```
FROM questdb/questdb:latest
# Устанавливаем необходимые зависимости (если нужно)
RUN apt-get update && apt-get install -y curl
# Устанавливаем переменные окружения для QuestDB
ENV QDB_ROOT=/var/lib/questdb
ENV PATH=$QDB_ROOT/bin:$PATH
```

- docker-compose.yml:
```
version: '3.8'
services:
  questdb:
    build: .
    container_name: questdb
    ports:
      - "9000:9000"
      - "8812:8812"
    volumes:
      - questdb-data:/var/lib/questdb
    environment:
      - QDB_ROOT=/var/lib/questdb
      - PATH=/var/lib/questdb/bin:$PATH
volumes:
  questdb-data:
```

- Стартовать можно bash файлом questdb_start.sh:
```
#!/bin/bash

docker build -t questdb_test .
docker run -p 9000:9000 questdb_test
```

После этого можно запустить скрипт reader.py, учтя следующее в этом скрипте:
```
#host = 'http://localhost:9000'
host = 'http://gitlab.ivl.ua:9000'
```
- Так можно проверить работоспособность БД не выходя из удаленного компьютера.

- Извне доступ к базе данных можно получить по адресу http://gitlab.ivl.ua:9000/
<br>Но в приватном окне браузера ;))

- Из приложения доступ к удаленной БД такой:
```
... код программы

host = 'http://gitlab.ivl.ua:9000'

sql_query = """SELECT DHT_Temperature, DHT_Humidity,
                    BME_Temperature, BME_Humidity, BME_Pressure,
                    DS_Temperature1, DS_Temperature2, timestamp
            FROM sensors
            ORDER BY timestamp DESC
            LIMIT 60;
            """

def get_data():
    try:
        response = requests.get(
            host + '/exec',
            params={'query': sql_query}
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json['dataset']
    except Exception as e:
        print("Error fetching data:", e)
        return None

... код программы
```

- Но это еще не все:
<br>БД питается данными с удаленного контроллера Arduino+{Bme280, Dht11, DS1, DS2, DS3,...}
<br>Данные контроллера потоком идут в линию uart на промежуточный компьютер, а уж с компьютера
<br>поступают в БД с помощью приложения контейнера sender1, и там оседают.
<br>Далее, настоящее приложение в модуле QuestDB вычитывает данные и выводит текстом и графикой    

**_Таким образом перед работой надо запустить 'вот это вот все'_**

- Теперь, Все!

**_2. RethinkDB    подготовка и запуск_**
- Первое, что можно сделать - запустить проект rethinkdb
<br>для удобства навигации по его частям, ибо в нем все необходимое
<br>для подготовки БД и установки ее в системе.

- Или: Зайти на ~/virt/dockers/rethinkdb и далее на внутр. каталог rethinkdb
```
cd ~/virt/dockers/rethinkdb/rethinkdb
```
- Запустить контейнер на основе официального образа rethinkdb
<br>docker-compose up -d
<br>такого содержания файла docker-compose.yml в данном каталоге
<br>что приведет к созданию своего образа и запуску init_rethinkdb.py
<br>который инициализирует данную БД

**<br>docker-compose.yml:**
```
version: '3.8'
services:
  rethinkdb:
    image: rethinkdb:2.4.1
    container_name: rethink1
    networks:
      - rethink_network
    ports:
      - "8087:8080"
      - "28015:28015"
      - "29015:29015"
    volumes:
      - ./rethinkdb_data:/data
  init_rethinkdb:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - rethinkdb
    networks:
      - rethink_network
networks:
  rethink_network:
    external: true
```

**<br>Dockerfile:**
```
FROM python:3.9-slim
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY init_rethinkdb.py /init_rethinkdb.py
CMD ["python", "/init_rethinkdb.py"]
```
<br>Файл init_rethinkdb.py содержит код создания базы r_info и таблицы weather

- Также следует запустить контейнеры sender1 и receiver1 выйдя в корень проекта:
**_<br>Подготовка и запуск docker-compose.yml_**  
```
cd ..
docker-compose up -d
```
<br>с таким содержанием файла docker-compose.yml
```
version: '3.8'

services:
  sender:
    container_name: sender1
    build:
      context: ./sender
      dockerfile: Dockerfile
    volumes:
      - ./sender:/app
    environment:
      - RETHINKDB_HOST=rethink1
    networks:
      - rethink_network  

  receiver:
    container_name: receiver1
    build:
      context: ./receiver
      dockerfile: Dockerfile
    volumes:
      - ./receiver:/app
    ports:
      - "5050:5000"
    environment:
      - RETHINKDB_HOST=rethink1
    networks:
      - rethink_network       

volumes:
  rethinkdb_data:
    external: true

networks:
  rethink_network:
    external: true
```
<br>При этом ресейвер доступен по адресу http://localhost:5050/
<br>Но можно проверить чтение из БД так
```
python3 read2console.py
```
<br>находясь в корне проекта reathinkdb

*
*
*
*


**_3. TimescaleDB  подготовка и запуск_**


**_4. SQLite       подготовка и запуск_**


**_5. PostgreSQL   подготовка и запуск_**


**_6. MongoDB      подготовка и запуск_**


**_7. RabbitMQ     подготовка и запуск_**


**_8. Redis        подготовка и запуск_**
 