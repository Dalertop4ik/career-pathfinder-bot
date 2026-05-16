import sqlite3

class Database:
    def __init__(self, db_name="career_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                age INTEGER, 
                interest TEXT
            )
        ''')
        
        # Таблица профессий
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS professions (
                id INTEGER PRIMARY KEY, 
                title TEXT, 
                description TEXT, 
                category TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, name, age, interest):
        # Приводим к строке на случай, если прилетит список
        str_interest = str(interest)
        self.cursor.execute(
            "INSERT OR REPLACE INTO users (id, name, age, interest) VALUES (?, ?, ?, ?)",
            (user_id, name, age, str_interest)
        )
        self.conn.commit()

    def get_recommendations(self, interest):
        # Если прилетел список, берем нужный элемент, иначе саму строку
        category = interest[1] if isinstance(interest, list) else interest
        self.cursor.execute(
            "SELECT title, description FROM professions WHERE category = ?", 
            (category,)
        )
        return self.cursor.fetchall()
