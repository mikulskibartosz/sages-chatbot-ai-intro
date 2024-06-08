import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.ai import AI


app = Flask(__name__)
CORS(app)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data['message']
    user_id = data['userId']

    ai = AI(tools=[])

    response = ai(msg)
    history = []

    return jsonify({"message": msg, "response": response, "history": history}), 200


@app.route("/userid", methods=['GET'])
def userid():
    return str(uuid.uuid4())


if __name__ == "__main__":
    app.run(debug=True)