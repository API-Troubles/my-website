import os
from typing import Optional

import psycopg  # PostgreSQL db driver v3


conn_params = {
    "dbname": "felixgao_url_shortener",
    "user": "felixgao",
    "password": os.environ['DB_PASSWORD'],
    "host": "hackclub.app",
    "port": "5432"
}

# Note to self, database table formats :D
"""
felixgao_url_shortener=> SELECT * FROM URLs;
 id | original_url | shortened_url | analytics_url 
----+--------------+---------------+---------------
(0 rows)

felixgao_url_shortener=> SELECT * FROM Analytics;
 id | url_id | created_at | referrer | user_agent 
----+--------+------------+----------+------------
(0 rows)
"""

class Database:
    def __init__(self):
        print("Database opened")
        self.conn = psycopg.connect(**conn_params)
        self.cur = self.conn.cursor()


    def close(self):
        """
        Close the database connection

        :return: Nothing
        """
        print("Database closed")
        if self.cur is not None:
            self.cur.close()

        if self.conn is not None:
            self.conn.close()


    def get_url(self, shortened_url: str) -> list:
        """
        Fetch URL data from the database
        """
        self.cur.execute("SELECT * FROM URLs WHERE shortened_url = %s;", (shortened_url,))
        return self.cur.fetchall()

    def get_hostname(self, url_id: str) -> list:
        """
        Fetch URL data from the database
        """
        self.cur.execute("SELECT * FROM domains WHERE url_id = %s;", (url_id,))
        return self.cur.fetchall()


    def get_analytics(self, analytics_url: str) -> Optional[list]:
        """
        Fetch analytics data from the database
        """
        self.cur.execute("SELECT * FROM URLs WHERE analytics_url = %s", (analytics_url,))
        url_table = self.cur.fetchall()
        if not url_table:
            return None
        url_id = url_table[0][0] # Get url_id so search with on Analytics table

        self.cur.execute("SELECT * FROM Analytics WHERE url_id = %s", (url_id,))
        return self.cur.fetchall()


    def add_url(self, original_url: str, shortened_url: str, analytics_url: str, url_hostnames: list) -> None:
        """
        Creates a database entry for a new URL
        """
        self.cur.execute("""
        INSERT INTO URLs (original_url, shortened_url, analytics_url) 
        VALUES (%s, %s, %s)
        RETURNING id
        """, (original_url, shortened_url, analytics_url))
        url_id = self.cur.fetchone()[0]
        for domain in url_hostnames:
            self.cur.execute("""
            INSERT INTO domains (url_id, domain) 
            VALUES (%s, %s)
            """, (url_id, domain))
        self.conn.commit()


    def add_analytics(self, url_id: int, referrer: str, user_agent: str) -> None:
        """
        Creates a database entry for analytics
        """
        self.cur.execute("""
        INSERT INTO Analytics (url_id, referrer, user_agent)
        VALUES  (%s, %s, %s)
        """, (url_id, referrer, user_agent))
        self.conn.commit()


    def check_url_exists(self, table_item: str, table_value: str) -> bool:
        """
        Checks if a table item already exists
        """
        self.cur.execute(f"SELECT COUNT(*) FROM URLs where {table_item} = %s", (table_value,))
        result = self.cur.fetchall()

        if result[0][0] > 1:
            raise ValueError("Somethings messed up in the database to have multiple of the same URL")
        else:
            return result[0][0] != 0


if __name__ == "__main__":
    ...