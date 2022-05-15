import sqlite3
from sqlite3 import Error


def create_connection(path):  # Создаем функцию для соединения с базой данных
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


# Соединяемся с бд
connection = create_connection("C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\DataBases\\sm_app.sqlite")
cursor = connection.cursor()
def execute_query(connection, query):
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER,
  languages TEXT,
  vocabulary_eng TEXT,
  vocabulary_deu TEXT
);
"""

execute_query(connection, create_users_table)

