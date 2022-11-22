# сначала в терминале запускаем команду, чтобы создать БД vkinder2022
# createdb -U postgres vkinder2022
# потом запускаем код:

import psycopg2


with psycopg2.connect(database="vkinder2022",
                      user="postgres",
                      password="29fihonu") as conn:
    with conn.cursor() as cur:
        
        # Перед повторным запуском кода необходимо разкомментировать:

        # cur.execute("""
        # DROP TABLE dislikes;
        # DROP TABLE likes;
        # DROP TABLE requests;
        # DROP TABLE searchers;
        # """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        searchers
        (
            searcherID SERIAL PRIMARY KEY NOT NULL,
            vk_id INTEGER NOT NULL UNIQUE,
            searcher_name VARCHAR(40),
            searcher_surname VARCHAR(40),
            searcher_birth_year INTEGER,
            city VARCHAR(40),
            link VARCHAR,
            searcher_photo1_link VARCHAR,
            searcher_photo2_link VARCHAR,
            searcher_photo3_link VARCHAR);
        
        CREATE TABLE IF NOT EXISTS 
        requests
        (
            requestID SERIAL PRIMARY KEY NOT NULL,
            date_time TIMESTAMPTZ NOT NULL,
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID),
            gender VARCHAR(10) NOT NULL,
            city VARCHAR(40) NOT NULL,
            birth_year INTEGER NOT NULL);
            
        CREATE TABLE IF NOT EXISTS 
        likes
        (
            likeID SERIAL PRIMARY KEY NOT NULL,
            request_id INTEGER NOT NULL REFERENCES requests(requestID),
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID),
            vk_id INTEGER NOT NULL UNIQUE,
            name VARCHAR(40),
            surname VARCHAR(40),
            birth_year INTEGER,
            city VARCHAR(40),
            link VARCHAR,
            photo1_link VARCHAR,
            photo2_link VARCHAR,
            photo3_link VARCHAR);

        CREATE TABLE IF NOT EXISTS 
        dislikes
        (
            dislikeID SERIAL PRIMARY KEY NOT NULL,
            request_id INTEGER NOT NULL REFERENCES requests(requestID),
            searcher_id INTEGER NOT NULL REFERENCES searchers(searcherID),
            vk_id INTEGER NOT NULL UNIQUE);            
            
            """)

        conn.commit()
conn.close()