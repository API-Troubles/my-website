"""
Database for handling random things which need to be stored

WIP, borrowed from my url shortener, will modify but don't know whats gonna be stored yet
"""
import re
from typing import Optional

import psycopg # PostgreSQL db driver v3


class DuplicateKey(Exception):
    pass


class Database:
    def __init__(self, conn_params):
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


    def get_user(self, *, token: Optional[str] = None, slack_id: Optional[str] = None) -> Optional[list]:
        """
        Get a user from database with either token or slack user_id
        """
        if token and slack_id:
            return ValueError('Cannot fill in token and user_id. What was the point? You already have all the info!')
        elif token:
            self.cur.execute("SELECT * FROM Users WHERE token = %s", (token,))
        elif slack_id:
            self.cur.execute("SELECT * FROM Users WHERE slack_id = %s", (slack_id,))

        user = self.cur.fetchall()
        if not user:
            return None
        return user[0]


    def add_user(self, slack_id: str, token: str) -> None:
        """
        Adds a user to the database
        """
        try:
            self.cur.execute("""
                INSERT INTO Users (token, slack_id)
                VALUES  (%s, %s)""", (token, slack_id)
            )
        except psycopg.errors.UniqueViolation as error:
            # Rollback changes, D:
            self.conn.rollback()
        else:
            self.conn.commit()
