import sqlite3
import pandas as pd
import os
from datetime import datetime

# Файл базы данных (будет лежать на сервере Timeweb)
DB_PATH = "clients_data.db"

class ClientManager:
    def __init__(self):
        self.init_db()

    def init_db(self):
        """Создает таблицу клиентов, если её нет (ФЗ-152: храним в РФ)"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                registration_date TIMESTAMP,
                last_interaction TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        conn.commit()
        conn.close()

    def add_client(self, tg_id, name, email=None, phone=None):
        """Добавляет нового клиента в базу"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO clients (telegram_id, full_name, email, phone, registration_date, last_interaction)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(tg_id), name, email, phone, datetime.now(), datetime.now()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Если клиент уже есть, обновляем время входа
            cursor.execute('UPDATE clients SET last_interaction = ? WHERE telegram_id = ?', 
                           (datetime.now(), str(tg_id)))
            conn.commit()
            return False
        finally:
            conn.close()

    def get_all_clients_df(self):
        """Возвращает всех клиентов в виде таблицы (Pandas)"""
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM clients", conn)
        conn.close()
        return df

    def export_to_excel(self, filename="clients_report.xlsx"):
        """Локальный экспорт (можно потом слать в Яндекс.Диск)"""
        df = self.get_all_clients_df()
        df.to_excel(filename, index=False)
        return os.path.abspath(filename)

# Пример использования:
# cm = ClientManager()
# cm.add_client("123456", "Иван Иванов", "ivan@mail.ru", "+79998887766")
