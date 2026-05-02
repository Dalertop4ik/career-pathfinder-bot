import sqlite3

class Database:
    def __init__(self, db_name="career_bot.db"):
        self.coon = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()


    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user
                               (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, interest TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS professions 
                               (id INTEGER PRIMARY KEY, title TEXT, description TEXT, category TEXT)''')
        self.coon.commit()

    def add_user(self, user_id, name, age, interest):
        self.cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
                            (user_id, name, age, interest))
        self.conn.commit()

    def get_recommedations(self, interest):
        self.cursor.execute("SELECT title, description FROM professions WHERE category = ?", (interest,))
        return self.cursor.fetchall()