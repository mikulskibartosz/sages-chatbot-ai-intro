import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.ai import AI
from app.tools import Tools
from app.db_memory import DbMemory


app = Flask(__name__)
CORS(app)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data['message']
    user_id = data['userId']

    memory = DbMemory(user_id)
    ai = AI(external_memory=memory, tools=[Tools().as_tool()])

    response = ai(msg)
    history = []
    for user_message, ai_message in zip(memory.get_user_messages(), memory.get_ai_messages()):
        history.append({"who": "user", "message": user_message})
        history.append({"who": "assistant", "message": ai_message})

    return jsonify({"message": msg, "response": response, "history": history}), 200


@app.route("/userid", methods=['GET'])
def userid():
    return str(uuid.uuid4())


if __name__ == "__main__":
    app.run(debug=True)