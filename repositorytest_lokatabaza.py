# -*- coding: utf-8 -*-

import repository
import sqlite3
import unittest

db_path = 'klient.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Lokaty')
        c.execute('DELETE FROM Klient')
        c.execute('''INSERT INTO Klient (id, imie, nazwisko, ilosc) VALUES(1, "Krystyna", "Nowak", 1)''')
        c.execute('''INSERT INTO Lokaty (nazwa, ilosc, oprocentowanie, klient_id) VALUES("trzymiesieczna", 10000, 1.15, 1)''')
        c.execute('''INSERT INTO Lokaty (nazwa, ilosc, oprocentowanie, klient_id) VALUES("polroczna", 3000, 1.0, 1)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Lokaty')
        c.execute('DELETE FROM Klient')
        conn.commit()
        conn.close()


# przygotowanie danych

    def testGetByIdInstance(self):
        klient = repository.KlientRepository().getById(1)
        self.assertIsInstance(klient, repository.Klient, "Objekt nie jest klasy Klient")


    def testGetByIdLokatyLen(self):
        self.assertEqual(len(repository.KlientRepository().getById(1).lokaty),
                2, "Powinno wyjść 2")


    def testGetByIdInstanceasda(self):
        klient = repository.KlientRepository().getById(1)
        self.assertEqual(klient.imie, "Krystyna", "Powinna być Krystyna")



if __name__ == "__main__":
    unittest.main()
