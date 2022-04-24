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
connection = create_connection("C:\\Users\StariyMicrozavr\PycharmProjects\TGbot\DataBases\sm_app.sqlite")

cursor = connection.cursor()


