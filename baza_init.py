import sqlite3

conn = sqlite3.connect('baza.db')
c = conn.cursor()


def wykonaj_skrypt_sql(skrypt):
    with open(skrypt, encoding='utf-8') as f:
        zapytanie = f.read()
    c.executescript(zapytanie)


wykonaj_skrypt_sql('baza.sql')

conn.commit()

conn.close()
