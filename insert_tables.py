import psycopg2
from datetime import datetime as dt 
import re
from my_data import passw

 
def insert_searchers(user_id):   
    with psycopg2.connect(database="vkinder2022",
                        user="postgres",
                        password=passw) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO searchers (vk_id) 
                VALUES ({user_id})
                ON CONFLICT (vk_id) DO NOTHING;"""
            )
        conn.commit()
    conn.close()


def insert_requests(user_id):
    with psycopg2.connect(database="vkinder2022",
					user="postgres",
					password=passw) as conn:
        with conn.cursor() as cur:
                cur.execute(
                        """INSERT INTO requests (date_time, searcher_id) 
                        VALUES (%s, (SELECT searcherID from searchers WHERE vk_id=%s));
            """, (dt.today(), user_id))
        conn.commit()		
    conn.close()
    

def insert_likes(user_id, result):
    with psycopg2.connect(database="vkinder2022",
                    user="postgres",
                    password=passw) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO likes (searcher_id, user_vkid, name, surname, link, photo1_link, photo2_link, photo3_link) 
                VALUES ((SELECT searcherID from searchers WHERE vk_id=%s),%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_vkid) DO NOTHING;
    """, (user_id, int(''.join(re.findall('(\d+)', result['url']))), result['name'].split()[0], result['name'].split()[1], result['url'],  result['photo'][0], result['photo'][1], result['photo'][2]))
        conn.commit()
    conn.close()


def insert_dislikes(user_id, result):
    with psycopg2.connect(database="vkinder2022",
                    user="postgres",
                    password=passw) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO dislikes (searcher_id, user_vkid) 
                VALUES ((SELECT searcherID from searchers WHERE vk_id=%s),%s);
    """, (user_id, int(''.join(re.findall('(\d+)', result['url'])))))
        conn.commit()
    conn.close()


def select_likes(user_id):
    with psycopg2.connect(database="vkinder2022",
                    user="postgres",
                    password=passw) as conn:
        with conn.cursor() as cur:
            cur.execute(
                    f"""SELECT name, surname, photo1_link, photo2_link, photo3_link
                    FROM likes 
                    JOIN searchers ON searcher_id=searcherID
                    WHERE searchers.vk_id={user_id};
        """)
            print(cur.fetchall())	
    conn.close()
