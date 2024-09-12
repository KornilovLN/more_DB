from rethinkdb import RethinkDB
import os
import time

r = RethinkDB()

HOST = '127.0.0.1'
#host = os.getenv('RETHINKDB_HOST', 'rethink1')
WAITCONNECT = 5
INTERVAL = 1
NUMBROWS = 8

ABOUT_TEXT = [
        "------------------------------------------------------------",
        "Программа чтения таблицы weather в БД rethink1 на 127.0.0.1",
        "author: Старых ЛН",
        "e-mail: ln.kornilovstar@gmail.com",
        "github: https://github.com/KornilovLN",
        "tel:    +380 66 9805661",
        "------------------------------------------------------------\n"
]

def print_about(about):
    for line in about:
        print(line)

def connect_db(host):
    while True:
        try:
            conn = r.connect(host=host, port=28015)
            print("Connected to RethinkDB")
            return conn
        except Exception as e:
            print(f"Failed to connect to RethinkDB: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(WAITCONNECT)

def fetch_and_print_data(conn, num):
    cursor = r.db('r_info').table('weather').order_by(r.desc('timestamp')).limit(num).run(conn)
    for document in cursor:
        region = document.get('region', '')
        post = document.get('post', 0)
        bme_t = document.get('bme', {}).get('t', 0.0)
        bme_h = document.get('bme', {}).get('h', 0.0)
        bme_p = document.get('bme', {}).get('p', 0.0)
        ds_t1 = document.get('ds', {}).get('t1', 0.0)
        ds_t2 = document.get('ds', {}).get('t2', 0.0)
        ds_t3 = document.get('ds', {}).get('t3', 0.0)
        dht_t = document.get('dht', {}).get('t', 0.0)
        dht_h = document.get('dht', {}).get('h', 0.0)
        timestamp = document.get('timestamp', '')

        print(f"{region}\t{post}\t{bme_t:.2f}\t{bme_h:.2f}\t{bme_p:.2f}\t{ds_t1:.2f}\t{ds_t2:.2f}\t{ds_t3:.2f}\t{dht_t:.2f}\t{dht_h:.2f}\t{timestamp}")

    feed = r.db('r_info').table('weather').changes().run(conn)
    for change in feed:
        print("Detected change, fetching latest data...")
        fetch_and_print_data(conn, num)
        time.sleep(INTERVAL)  # Add a small delay to avoid overwhelming the console

def main():
    numb = NUMBROWS
    conn = connect_db(HOST)
    fetch_and_print_data(conn, numb)
    watch_changes(conn, numb)

if __name__ == "__main__":
    print_about(ABOUT_TEXT)
    main()