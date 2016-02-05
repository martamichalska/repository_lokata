import sqlite3


db_path = 'klient.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute("DROP TABLE IF EXISTS Klient;")
c.execute("DROP TABLE IF EXISTS Lokaty;")
c.execute('''
          CREATE TABLE Klient
          ( id INTEGER PRIMARY KEY,
            imie VARCHAR(100) NOT NULL,
            nazwisko VARCHAR(100) NOT NULL,
            ilosc NUMERIC NOT NULL
          )
          ''')
c.execute('''
          CREATE TABLE Lokaty
          ( nazwa VARCHAR(100),
            ilosc NUMERIC NOT NULL,
            oprocentowanie NUMERIC NOT NULL,
            klient_id INTEGER,
           FOREIGN KEY(klient_id) REFERENCES Klient(id),
           PRIMARY KEY (nazwa, klient_id))
          ''')