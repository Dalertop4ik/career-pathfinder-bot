import sqlite3

class Database:
    def __init__(self, db_name="career_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, result TEXT)''')
        # Таблица профессий
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS professions
                            (id TEXT PRIMARY KEY, title TEXT, description TEXT, skills TEXT)''')
        self.conn.commit()

    def add_user(self, user_id, name, age, result):
        self.cursor.execute("INSERT OR REPLACE INTO users (id, name, age, result) VALUES (?, ?, ?, ?)",
                            (user_id, name, age, result))
        self.conn.commit()

    def get_profession(self, prof_id):
        self.cursor.execute("SELECT title, description, skills FROM professions WHERE id = ?", (prof_id,))
        return self.cursor.fetchone()
