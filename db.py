import psycopg2
from config_db import host, user, password, db_name

import time

class DataBase:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,   
        )
    
        self.cursor = self.connection.cursor()
    
    def add_user(self, user_id, chat_id):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, chat_id) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING;", (user_id, chat_id))
            self.connection.commit()

    def get_all_users(self):
        with self.connection:
            self.cursor.execute("SELECT user_id, chat_id, api_token_wb FROM users;")
            return self.cursor.fetchall()

    def update_user_chat_id(self, user_id, chat_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET chat_id = %s WHERE user_id = %s;", (chat_id, user_id))
            self.connection.commit()

    def update_api_wb(self, user_id, api_token_wb):
        with self.connection:
            return self.cursor.execute("UPDATE users SET api_token_wb = %s WHERE user_id = %s;", (api_token_wb, user_id,))

    def user_exists(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            result = self.cursor.fetchone()
            if result is not None:
                return bool(len(result))
            else:
                return False
        
    def get_signup(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT signup FROM users WHERE user_id = %s;", (user_id,))
            result = self.cursor.fetchone()
        if result:
            signup = str(result[0][0])
            return signup
        return None
    
    def set_signup(self, user_id, signup):
        with self.connection:
            return self.cursor.execute("UPDATE users SET signup = %s WHERE user_id = %s;", (signup, user_id,))
        
    def set_time_sub(self, user_id, time_sub):
        with self.connection:
            return self.cursor.execute("UPDATE users SET time_sub = %s WHERE user_id = %s;", (time_sub, user_id,))
        
    def get_time_sub(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT time_sub FROM users WHERE user_id = %s;", (user_id,))
            result = self.cursor.fetchall()
            for row in result:
                time_sub = int(row[0])
            return time_sub
        
    def get_sub_status(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT time_sub FROM users WHERE user_id = %s;", (user_id,))
            result = self.cursor.fetchall()
            for row in result:
                time_sub = int(row[0])
            
            if time_sub > int(time.time()):
                return True
            else:
                return False 
            
    def get_api_token_wb(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT api_token_wb FROM users WHERE user_id = %s;", (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None

    def get_all_user_chat_ids_with_api_key(self):
        with self.connection:
            self.cursor.execute("SELECT user_id FROM users WHERE api_token_wb IS NOT NULL;")
            result = self.cursor.fetchall()
            return [row[0] for row in result] if result else []