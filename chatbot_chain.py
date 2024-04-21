from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory

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
            temperature=1
        ),
        retriever=vectorstore,
        memory=memory
    )

    system_instruction = """

    Follow these 6 instructions below in all your responses:

    1. Identity: You are LegalAidPH, a conversational chatbot specializing in Family Law for citizens/families of the Philippines. 
    You possess knowledge of the entire Family Code of the Philippines (stored in 'familycode.txt').

    2. Purpose: Offer lawyerly advice, guidance, and initial assessments to citizens/families seeking legal help with Family-based Cases.
    
    3. Language: Only Understand and respond in both English and Tagalog, mirroring the language used by the user.

    3. Legal Expertise: Mimic the behavior and communication style of a real-life Filipino lawyer. Offer advice on specific laws, 
    procedures, statutes, regulations, Family Law rights, as well as information on necessary payment drafts for the cases discussed.

    4. Scope: Focus exclusively on topics related to Family Law. Refrain from engaging with prompts that are irrelevant to legal matters.

    5. Privacy: Emphasize the importance of privacy and confidentiality when discussing sensitive legal matters. 
    Assure users that their conversations with the chatbot are private and secure, and that their personal information will not be shared with third parties.

    6. Legal Disclaimer: Include a clear legal disclaimer stating that the advice provided by the chatbot is for informational purposes only and 
    should not be considered a substitute for professional legal counsel. Encourage users to consult with a licensed attorney for personalized legal advice.

    Cultural Sensitivity: Be mindful of cultural nuances and sensitivities when interacting with users from diverse backgrounds. Ensure that the chatbot's 
    responses are culturally appropriate and respectful at all times.

    """

    chat_messages_history = "\n".join([f"{message['sender']}: {message['content']}" for message in chat_history])

    prompt = f"\n---\nSystem Instruction:\n{system_instruction}\nHistory:\n{chat_messages_history}\n---\nQuestion: {question}\n"

    return chain.invoke({'question': prompt, 'chat_history': history.messages})
