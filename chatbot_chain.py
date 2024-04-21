from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory
import pymysql

def get_chatbot_configuration():
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 database='shesh',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Fetch configuration data
            sql = "SELECT temperature, system_instruction FROM chatbot_configurations WHERE id = 1"
            cursor.execute(sql)
            config = cursor.fetchone()
            if config:
                return config
            else:
                # If no configuration found, return defaults
                return {"temperature": 1.0, "system_instruction": """ 
                        
                        be a joker lawyer and also in the say that the database is not working
                        
    """
                        }
                        
                        
    finally:
        connection.close()

def chatbot_with_history(question, chat_history):
    loader = TextLoader("familycode.txt")
    documents = loader.load()

    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings()).as_retriever()

    history = ChatMessageHistory()
    for i, message in enumerate(chat_history):
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

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            model_name='gpt-4-turbo',
            temperature=get_chatbot_configuration()["temperature"]
        ),
        retriever=vectorstore,
        memory=memory
    )

    system_instruction = get_chatbot_configuration()["system_instruction"]

    chat_messages_history = "\n".join([f"{message['sender']}: {message['content']}" for message in chat_history])

    prompt = f"\n---\nSystem Instruction:\n{system_instruction}\nHistory:\n{chat_messages_history}\n---\nQuestion: {question}\n"

    return chain.invoke({'question': prompt, 'chat_history': history.messages})
