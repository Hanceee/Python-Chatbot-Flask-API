import chatbot_chain
import sys
from dotenv import load_dotenv

load_dotenv()

history = []

while True:
    query = input('Prompt (or type "exit" to quit): ')

    if query == "exit":
        print('Exiting')
        sys.exit()

    response = chatbot_chain.chatbot_with_history(query, history)

    history.append({
        "sender": "User",
        "content": query
    })
    history.append({
        "sender": "AI Bot",
        "content": response["answer"]
    })

    print("Answer: " + response["answer"])
