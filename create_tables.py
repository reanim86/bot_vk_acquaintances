# сначала в терминале запускаем команду, чтобы создать БД vkinder2022
# createdb -U postgres vkinder2022
# потом запускаем код:

import psycopg2


with psycopg2.connect(database="vkinder2022",
                      user="postgres",
                      password="Vu293893") as conn:
    with conn.cursor() as cur:
        
        # Перед повторным запуском кода необходимо разкомментировать:

        # cur.execute("""
        # DROP TABLE dislikes;
        # DROP TABLE likes;
        # DROP TABLE requests;
        
        # """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        searchers
        (
            searcherID SERIAL PRIMARY KEY NOT NULL,
            vk_id INTEGER NOT NULL UNIQUE);
        
        CREATE TABLE IF NOT EXISTS 
        requests
        (
            requestID SERIAL PRIMARY KEY NOT NULL,
            date_time TIMESTAMP,
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID));
            
        CREATE TABLE IF NOT EXISTS 
        likes
        (
            likeID SERIAL PRIMARY KEY NOT NULL,
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID),
            user_vkid INTEGER UNIQUE,
            name VARCHAR(40),
            surname VARCHAR(40),
            link VARCHAR,
            photo1_link VARCHAR,
            photo2_link VARCHAR,
            photo3_link VARCHAR);

        CREATE TABLE IF NOT EXISTS 
        dislikes
        (
            dislikeID SERIAL PRIMARY KEY NOT NULL,
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID),
            user_vkid INTEGER UNIQUE);            
            
            """)

        conn.commit()

conn.close()
