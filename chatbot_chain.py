from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory


def chatbot_with_history(question, chat_history):
    loader = CSVLoader('faq.csv')
    documents = loader.load()

    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings()).as_retriever()

    history = ChatMessageHistory()
    for i, message in enumerate(chat_history):
        if message['sender'] == 'AI Bot':
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
            model_name='gpt-4-1106-preview',
            temperature=0
        ),
        retriever=vectorstore,
        memory=memory
    )

    chat_messages_history = "\n".join([f"{message['sender']}: {message['content']}" for message in chat_history])

    prompt = f"\n---\nHistory:\n{chat_messages_history}\n---\nQuestion: {question}\n"

    return chain({'question': prompt, 'chat_history': history.messages})
