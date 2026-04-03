from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.document_loader import get_vector_store
from backend.config import POLLINATIONS_API_KEY


PROMPT_TEXT = """You are a friendly customer support assistant for resolv.ai.
1. If the user is just saying hello, greeting you, or making small talk, politely greet them back and ask how you can help. DO NOT say "TICKET_NEEDED" for greetings.
2. For actual questions, use the context below to answer the customer's question.
3. If you cannot find the answer to their specific question in the context, say exactly: "TICKET_NEEDED"
4. Do not make up answers. Be short and helpful.

Context from company documents:
{context}

{question}

Your Answer:"""


def get_ai_answer(question, chat_history=None):
    vector_store = get_vector_store()

    if vector_store is None:
        return {
            "answer": "Sorry, my knowledge base hasn't been set up yet. Please ask an admin to click Retrain.",
            "needs_ticket": True
        }

    history_text = ""
    if chat_history and len(chat_history) > 0:
        history_text = "Previous conversation:\n"
        for msg in chat_history[-5:]:
            history_text += f"Customer: {msg['question']}\n"
            history_text += f"Assistant: {msg['answer']}\n\n"

    full_question = ""
    if history_text:
        full_question = history_text + "Customer's new message: " + question
    else:
        full_question = "Customer's message: " + question

    # Connect to the FREE Pollinations API (It acts exactly like OpenAI!)
    llm = ChatOpenAI(
        api_key=POLLINATIONS_API_KEY or "pollinations",  # It requires something here
        base_url="https://text.pollinations.ai/openai",
        model="openai",  # the model name pollinations expects
        temperature=0.7
    )

    prompt = PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["context", "question"]
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )

    result = chain.invoke({"query": full_question})
    answer = result["result"]

    needs_ticket = "TICKET_NEEDED" in answer

    if needs_ticket:
        answer = "I'm sorry, I couldn't find an answer to your question. A support ticket has been created and our team will get back to you soon!"

    return {
        "answer": answer,
        "needs_ticket": needs_ticket
    }
