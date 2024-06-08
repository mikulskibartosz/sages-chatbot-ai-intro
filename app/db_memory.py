import sqlite3


class DbMemory:
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.conn = sqlite3.connect('../memory.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS user_messages (user_id TEXT, message TEXT)")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS ai_messages (user_id TEXT, message TEXT)")
        self.conn.commit()

    def add_user_message(self, message):
        self.cursor.execute(f"INSERT INTO user_messages VALUES (?, ?)", (self.user_id, message))
        self.conn.commit()

    def add_ai_message(self, message):
        self.cursor.execute(f"INSERT INTO ai_messages VALUES (?, ?)", (self.user_id, message))
        self.conn.commit()

    def get_user_messages(self):
        self.cursor.execute(f"SELECT message FROM user_messages WHERE user_id = ?", (self.user_id,))
        return [message[0] for message in self.cursor.fetchall()]

    def get_ai_messages(self):
        self.cursor.execute(f"SELECT message FROM ai_messages WHERE user_id = ?", (self.user_id,))
        return [message[0] for message in self.cursor.fetchall()]
