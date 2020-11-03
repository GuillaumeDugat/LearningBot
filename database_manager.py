import sqlite3
import time

db_name = 'learning_database.db'

def init_db():
    """Création de la base de données"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Deck(
            id_deck INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            id_user INTEGER,
            name VRCHAR(50),            
            desc VARCHAR(5000),
            FOREIGN KEY(id_user) REFERENCES User(id_user)            
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Card(
            id_card INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            id_user INTEGER,
            id_deck INTEGER,
            word VARCHAR(80),
            translated_word VARCHAR(300),
            FOREIGN KEY(id_deck) REFERENCES Deck(id_deck),
            FOREIGN KEY(id_user) REFERENCES User(id_user)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User(
            id_user INTEGER PRIMARY KEY,
            date DATE,
            username VARCHAR(50),
            id_working_deck INTEGER,
            FOREIGN KEY(id_working_deck) REFERENCES Deck(id_deck)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sequence(
            id_seq INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            id_user INTEGER,
            id_card INTEGER,
            FOREIGN KEY(id_user) REFERENCES User(id_user),
            FOREIGN KEY(id_card) REFERENCES Card(id_card)
        )
    ''')

    cursor.close()
    conn.close()


def add_deck_to_db(id_user, name, desc):
    """Create and add a new deck in the database"""
    if find_deck_by_name(id_user, name) != None:
        return None
    else:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Deck (date, id_user, name, desc)  VALUES (?, ?, ?, ?)''', (time.time(), id_user, name, desc))
        conn.commit()
        cursor.close()
        conn.close()
        return find_deck_by_name(id_user, name)

def add_card_to_db(id_user, id_deck, word, translated_word):
    """Create and add a new card in the database"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Card (date, id_user, id_deck, word, translated_word)  VALUES (?, ?, ?, ?, ?)''', (time.time(), id_user, id_deck, word, translated_word))
    conn.commit()
    cursor.close()
    conn.close()

def add_user_to_db(id_user, username):
    """Create and add a new user in the database or update its username"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Searching whether the user is already in the database or not
    cursor.execute('''SELECT * FROM User WHERE id_user = ?''',(id_user,))
    result = cursor.fetchall()
    if len(result) == 0: # A
        cursor.execute('''INSERT INTO User (id_user, date, username, id_working_deck)  VALUES (?, ?, ?, NULL)''', (id_user, time.time(), username))
    else:
        cursor.execute('''UPDATE User SET date = ?, username = ? WHERE id_user = ?''', (time.time(), username, id_user))
    conn.commit()
    cursor.close()
    conn.close()

def find_deck_by_id(id_deck):
    """Find and return a deck's attributes by its id"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Deck WHERE id_deck = ?''',(id_deck,))
    result = cursor.fetchall()[0]
    cursor.close()
    conn.close()
    return {"id_deck": result[0], "date": result[1], "id_user": result[2], "name": result[3], "desc": result[4]}

def find_deck_by_name(id_user, name):
    """Find and return a deck's id by its name"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT id_deck FROM Deck WHERE id_user = ? AND name = ?''', (id_user, name,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(result) == 0:
        return None
    else:
        return result[0][0]

def list_of_cards(id_deck):
    """Return the list of all the cards of a given deck"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT id_card FROM Card WHERE id_deck = ?''',(id_deck,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in result]

def find_working_deck_id(id_user):
    """Return the working deck id"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT id_working_deck FROM User WHERE id_user = ?''',(id_user,))
    result = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    return result   

def update_working_deck_id(id_user, new_working_deck_id):
    """Enable to move to another deck"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''UPDATE User SET id_working_deck = ? WHERE id_user = ?''', (new_working_deck_id, id_user))
    conn.commit()
    cursor.close()
    conn.close()

def add_sequence_to_db(id_user, id_card_list):
    """Add cards to create a sequence"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for id_card in id_card_list:
        cursor.execute('''INSERT INTO Sequence (date, id_user, id_card)  VALUES (?, ?, ?)''', (time.time(), id_user, id_card))
    conn.commit()
    cursor.close()
    conn.close()

def get_sequence_list(id_user):
    """Return the list of couples [word, translated_word] of the current sequence"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT Sequence.id_seq, Card.word, Card.translated_word FROM Sequence JOIN Card ON Sequence.id_card = Card.id_card WHERE Sequence.id_user = ? ORDER BY Sequence.id_seq ASC''',(id_user,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def remove_sequence_card(id_seq):
    """Delete a row of table Sequence"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM Sequence WHERE id_seq = ?''',(id_seq,))
    conn.commit()
    cursor.close()
    conn.close()