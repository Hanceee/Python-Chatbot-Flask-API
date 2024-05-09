import os
from flask import Flask, request, jsonify
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
    workers = int(os.getenv("WORKERS", default=4))
    debug = os.getenv("DEBUG", default=False)
    host = os.getenv("HOST", default='0.0.0.0')
    port = int(os.getenv("PORT", default=8080))

    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        from waitress import serve
        serve(app, host=host, port=port, threads=workers)
