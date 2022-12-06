import psycopg2
from datetime import datetime as dt
import re
import configparser


config = configparser.ConfigParser()
config.read('token.ini')
passw = config['BD_password']['passw']

connection = psycopg2.connect(
    user="postgres",
    password=passw,
    database="vkinder2022")

connection.autocommit = True


def insert_searchers(user_id):
    """Заполнение таблицы searchers (пользователи, написавшие боту)"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                    f"""INSERT INTO searchers (vk_id) 
                    VALUES ({user_id})
                    ON CONFLICT (vk_id) DO NOTHING;""")
    except Exception as error:
        print(error)  # Можно залогировать ошибки
        return


def insert_requests(user_id):
    """Заполнение таблицы requests (дата и время обращения к боту)"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                    """INSERT INTO requests (date_time, searcher_id) 
                            VALUES (%s, (SELECT searcherID from searchers WHERE vk_id=%s));
                """, (dt.today(), user_id))
    except Exception as error:
        print(error)  # Можно залогировать ошибки
        return


def insert_likes(user_id, result):
    """Заполнение таблицы likes (сохраняем в БД данные страницы, которую пользователь добавил в "Избранное")"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                    """INSERT INTO likes 
                    (searcher_id, user_vkid, name, surname, link) 
                    VALUES ((SELECT searcherID from searchers WHERE vk_id=%s),%s, %s, %s, %s)
                    ON CONFLICT (user_vkid) DO NOTHING;
        """, (user_id, int(''.join(re.findall(r'(\d+)', result['url']))),
                result['name'].split()[0],
                result['name'].split()[1],
                result['url']))
    except Exception as error:
        print(error)  # Можно залогировать ошибки
        return


def insert_dislikes(user_id, result):
    """Заполнение таблицы dislikes (сохраняем в БД данные страницы, которую пользователь добавил в "черный список")"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                    """INSERT INTO dislikes (searcher_id, user_vkid) 
                    VALUES ((SELECT searcherID from searchers WHERE vk_id=%s),%s);
                     """, (user_id, int(''.join(re.findall(r'(\d+)', result['url'])))))
    except Exception as error:
        print(error)  # Можно залогировать ошибки
        return


def select_likes(user_id):
    """Выбираем для пользователя все страницы, которые он отметил, как Like"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT l.name, l.surname, l.link 
                            FROM likes l
                            JOIN  searchers s 
                            ON l.searcher_id = s.searcherid  
                            WHERE s.vk_id = {user_id};""")
            result = [" ".join(fav) for fav in cursor.fetchall()]
        return result
    except Exception as error:
        print(error)  # Можно залогировать ошибки
        return


if __name__ == "__main__":
    pass
