"""
Database for handling random things which need to be stored lol
"""
from typing import Optional

import psycopg # PostgreSQL db driver v3


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
            raise ValueError('Cannot fill in token and user_id. What was the point? You already have all the info!')
        elif token:
            self.cur.execute("SELECT * FROM Users WHERE token = %s", (token,))
        elif slack_id:
            self.cur.execute("SELECT * FROM Users WHERE slack_id = %s", (slack_id,))
        else:
            raise ValueError('No token or user_id provided. You realize this was mandatory, right?')

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
            raise ValueError("User already exists") from error
        else:
            self.conn.commit()


    def get_setting(self, slack_id: str, setting: Optional[str] = None) -> Optional[list]:
        """
        Yoinks a setting for a user
        """
        if setting:
            self.cur.execute(f"SELECT * FROM Settings WHERE slack_id = %s AND setting = %s", (slack_id, setting))
        else:
            self.cur.execute(f"SELECT * FROM Settings WHERE slack_id = %s", (slack_id,))

        setting_result = self.cur.fetchall()
        if not setting_result:
            return None

        if setting:
            return setting_result[0]
        return setting_result


    def add_setting(self, slack_id: str, setting: str, setting_value: str) -> None:
        """
        Adds a setting for a user
        """
        self.cur.execute("""
            INSERT INTO Settings (slack_id, setting, setting_value)
            VALUES  (%s, %s, %s)""", (slack_id, setting, setting_value)
        )
        self.conn.commit()


    def edit_setting(self, slack_id: str, setting: str, setting_value: str) -> None:
        """
        Changes settings for a user
        """
        self.cur.execute("""
            UPDATE Settings
            SET setting_value = %s
            WHERE slack_id = %s AND setting = %s;""", (setting_value, slack_id, setting)
        )
        self.conn.commit()


    def update_token(self, slack_id: str, new_token: str) -> None:
        """
        Updates the token of a user
        """
        self.cur.execute("""
            UPDATE Users
            SET token = (%s)
            WHERE slack_id = (%s)""", (new_token, slack_id)
        )
        self.conn.commit()