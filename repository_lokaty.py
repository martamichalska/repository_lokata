# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

#
# Ścieżka połączenia z bazą danych
#
db_path = 'klient.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

#
# Model danych
#
class Klient():
    """Model pojedynczego klienta
    """
    def __init__(self, id, imie, nazwisko, lokaty=[]):
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.lokaty = lokaty
        self.ilosc = sum([lokaty.ilosc for lokaty in self.lokaty])

    def __repr__(self):
        return "<Klient(id='%s',imie='%s',nazwisko='%s', ilosc='%s', lokaty='%s')>" % (
                    self.id, self.imie,self.nazwisko, str(self.ilosc), str(self.lokaty)
                )


class Lokata():
    """Model lokaty. Występuje tylko wewnątrz obiektu Klient.
    """
    def __init__(self, nazwa, ilosc, oprocentowanie):
        self.nazwa = nazwa
        self.ilosc = ilosc
        self.oprocentowanie = oprocentowanie

    def __repr__(self):
        return "<Lokata(nazwa='%s', ilosc='%s', oprocentowanie='%s')>" % (
                    self.nazwa, str(self.ilosc), str(self.oprocentowanie)
                )


#
# Klasa bazowa repozytorium
#
class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow typu Klient
#
class KlientRepository(Repository):

    def add(self, klient):
        """Metoda dodaje pojedynczego klienta do bazy danych,
        wraz ze wszystkimi jego lokatami.
        """
        try:
            c = self.conn.cursor()
            # zapisz klienta
            ilosc = sum([item.ilosc*item.oprocentowanie for item in klient.lokaty])
            c.execute('INSERT INTO Klient (id, imie, nazwisko, ilosc) VALUES(?, ?, ?, ?)',
                        (klient.id, klient.imie, klient.nazwisko, str(klient.ilosc))
                    )
            # zapisz lokaty klienta
            if klient.lokaty:
                for lokata in klient.lokaty:
                    try:
                        c.execute('INSERT INTO Lokaty (nazwa, ilosc, oprocentowanie, klient_id) VALUES(?,?,?,?)',
                                        (lokata.nazwa, str(lokata.ilosc), str(lokata.oprocentowanie), klient.id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding klient item: %s, to klient: %s' %
                                                    (str(lokata), str(klient.id))
                                                )
        except Exception as e:
            #print "klient add error:", e
            raise RepositoryException('error adding klient %s' % str(klient))

    def delete(self, klient):
        """Metoda usuwa pojedynczego klienta z bazy danych,
        wraz ze wszystkimi jego lokatami.
        """
        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Lokaty WHERE klient_id=?', (klient.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Klient WHERE id=?', (klient.id,))

        except Exception as e:
            #print "klient delete error:", e
            raise RepositoryException('error deleting klient %s' % str(klient))

    def getById(self, id):
        """Get klient by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Klient WHERE id=?", (id,))
            inv_row = c.fetchone()
            klient = Klient(id=id, imie=inv_row[1], nazwisko=inv_row[2])
            if inv_row == None:
                klient=None
            else:
                klient.imie = inv_row[1]
                klient.nazwisko = inv_row[2]
                klient.ilosc = inv_row[3]
                c.execute("SELECT * FROM Lokaty WHERE klient_id=? order by nazwa", (id,))
                inv_items_rows = c.fetchall()
                items_list = []
                for item_row in inv_items_rows:
                    item = Lokata(nazwa=item_row[0], ilosc=item_row[1], oprocentowanie=item_row[2])
                    items_list.append(item)
                klient.lokaty=items_list
        except Exception as e:
            #print "klient getById error:", e
            raise RepositoryException('error getting by id klient_id: %s' % str(id))
        return klient

    def update(self, klient):
        """Metoda uaktualnia pojedynczego klienta w bazie danych,
        wraz ze wszystkimi jego lokatami.
        """
        try:
            # pobierz z bazy klienta
            inv_oryg = self.getById(klient.id)
            if inv_oryg != None:
                # klient jest w bazie: usuń go
                self.delete(klient)
            self.add(klient)

        except Exception as e:
            #print "klient update error:", e
            raise RepositoryException('error updating klient %s' % str(klient))



if __name__ == '__main__':
    try:
        with KlientRepository() as klient_repository:
            klient_repository.add(
                Klient(id = 1, imie="Anna", nazwisko="Nowak",
                        lokaty = [
                            Lokata(nazwa = "kwartalna",   ilosc = 4000, oprocentowanie = 1.0),
                            Lokata(nazwa = "polroczna",    ilosc = 10000, oprocentowanie = 1.2),
                            Lokata(nazwa = "roczna",  ilosc = 26000, oprocentowanie = 1.4),
                        ]
                    )
                )
            klient_repository.complete()
    except RepositoryException as e:
        print(e)

    print KlientRepository().getById(1)

    try:
        with KlientRepository() as klient_repository:
            klient_repository.update(
                Klient(id = 1, imie="Adam", nazwisko="Kwiatkowski",
                        lokaty = [
                            Lokata(nazwa = "trzymiesieczna", ilosc = 5000, oprocentowanie = 1.0),
                            Lokata(nazwa = "polroczna", ilosc = 15000, oprocentowanie = 1.25),
                            Lokata(nazwa = "kwartalna",   ilosc = 6000, oprocentowanie = 1.0)
                        ]
                    )
                )
            klient_repository.complete()
    except RepositoryException as e:
        print(e)

    print KlientRepository().getById(1)

    # try:
    #     with KlientRepository() as klient_repository:
    #         klient_repository.delete( Klient(id = 1) )
    #         klient_repository.complete()
    # except RepositoryException as e:
    #     print(e)