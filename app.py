import os

from flask import Flask, request, jsonify
from waitress import serve
from chatbot_chain import chatbot_with_history
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route('/api/chat_with_history', methods=['POST'])
def chat_with_history_api():
    json_request = request.get_json()

    question = json_request['query']
    chat_history = json_request['chat_history']

    chat_chain = chatbot_with_history(question, chat_history)

    return jsonify({
        "data": {
            "question": question,
            "answer": chat_chain["answer"]
        }
    })


if __name__ == '__main__':
    if env("DEBUG"):
        app.run(host='0.0.0.0', port=8080, use_reloader=True, debug=True)
    else:
        serve(app, host="0.0.0.0", port=8080)

# if __name__ == '__main__':
#     if os.getenv("DEBUG"):
#         app.run(host='0.0.0.0', port=8080, use_reloader=True, debug=True)
#     else:
#         serve(app, host="0.0.0.0", port=8080)        
