from abc import ABC, abstractmethod
import random
import uuid
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool


app = Flask(__name__, static_folder="static")
CORS(app)


def random_number(x):
    return random.randint(0, int(x))


class Memory(ABC):
    @abstractmethod
    def add_user_message(self, message):
        pass

    @abstractmethod
    def add_ai_message(self, message):
        pass

    @abstractmethod
    def get_user_messages(self):
        pass

    @abstractmethod
    def get_ai_messages(self):
        pass


class DbMemory(Memory):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.conn = sqlite3.connect('memory.db')
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


class AI:
    def __init__(self, external_memory=None):
        self.tools = [
            Tool(
                name="Random",
                func=random_number,
                description="""Generates a random number between 0 and x."""
            )
        ]
        self.model = ChatOpenAI(model_name="gpt-4", temperature=0)
        self.langchain_memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = initialize_agent(
            agent="conversational-react-description",
            tools=self.tools,
            llm=self.model,
            memory=self.langchain_memory,
            verbose=True,
        )
        self.external_memory = external_memory

    def __call__(self, message):
        self.langchain_memory.chat_memory.clear()

        for user_message, ai_message in zip(self.external_memory.get_user_messages(), self.external_memory.get_ai_messages()):
            self.langchain_memory.chat_memory.add_user_message(user_message)
            self.langchain_memory.chat_memory.add_ai_message(ai_message)

        self.external_memory.add_user_message(message)

        response = self.agent(message)

        self.external_memory.add_ai_message(response['output'])
        return response['output']


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data['message']
    user_id = data['userId']

    memory = DbMemory(user_id)
    agent = AI(memory)

    response = agent(msg)

    result = []
    for user_message, ai_message in zip(memory.get_user_messages(), memory.get_ai_messages()):
        result.append({"who": "user", "message": user_message})
        result.append({"who": "ai", "message": ai_message})

    return jsonify({"message": msg, "response": response, "history": result}), 200


@app.route("/userid", methods=['GET'])
def userid():
    return str(uuid.uuid4())


@app.route('/web', methods=['GET'])
def web():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(debug=True)
