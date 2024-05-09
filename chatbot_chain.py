from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory
import pymysql.cursors

# Connection Pooling
connection = pymysql.connect(host='153.92.15.11',
                             user='u253378952_admin',
                             password='Popdog_69',
                             database='u253378952_legalaidph',
                             cursorclass=pymysql.cursors.DictCursor)

# Fetch configuration data
def get_chatbot_configuration(cursor):
    sql = "SELECT temperature, system_instruction FROM chatbot_configurations WHERE id = 1"
    cursor.execute(sql)
    return cursor.fetchone() or {"temperature": 1.0, "system_instruction": "be a joker lawyer and also in the say that the database is not working"}

# Cache configuration data
config = get_chatbot_configuration(connection.cursor())

# Reuse TextLoader
loader = TextLoader("familycode.txt")
documents = loader.load()

# Reuse FAISS vectorstore
vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings()).as_retriever()

def chatbot_with_history(question, chat_history):
    history = ChatMessageHistory()
    for message in chat_history:
        if message['sender'] == 'LegalAidPH':
            history.add_ai_message(message['content'])
        else:
            history.add_user_message(message['content'])

    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        return_messages=True,
        history=history,
        k=15
    )

    # Reuse chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=config["temperature"]
        ),
        retriever=vectorstore,
        memory=memory
    )

    chat_messages_history = "\n".join([f"{message['sender']}: {message['content']}" for message in chat_history])

    prompt = f"\n---\nSystem Instruction:\n{config['system_instruction']}\nHistory:\n{chat_messages_history}\n---\nQuestion: {question}\n"

    return chain.invoke({'question': prompt, 'chat_history': history.messages})
