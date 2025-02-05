from langchain_core.runnables import RunnableLambda
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

ollamamodel = OllamaLLM(model="llama3.2:1b")
chain = (
        PromptTemplate.from_template(
            """
            You are an expert that can understand if the user is trying to have a general conversation
            or is asking about doubts and questions and specific subject topics
            Given the user question below, classify it as either being about `Subject Topic` or `Others`.

    Do not respond with more than one word.

    <question>
    {question}
    </question>

    Classification:"""
        )
        | ollamamodel
        | StrOutputParser()
)

general_chain = (PromptTemplate.from_template(
    """You are an expert in general conversation.
Respond to the following question:

Question: {question}
Answer:"""
) | ollamamodel | StrOutputParser() )

answerchain = (
        PromptTemplate.from_template(
            """
            You are an expert that can understand the context. Give a explanation or answer as a teacher to the
            student's question from the context.

    <context>
    {context}
    </context>

    <question>
    {question}
    </question>
    """
        )
        | ollamamodel
        | StrOutputParser()
)

sessionnamechain = (
        PromptTemplate.from_template(
            """
    <context>
    {context}
    </context>
    <question>
    {question}
    </question>
    
    From the context and question create a three word text which best describes the topic of the question and the context
    Do not respond with more than three word.
    """
        )
        | ollamamodel
        | StrOutputParser()
)

def llmroute(question,context):
    classification_result = chain.invoke({"question": question})
    if "Subject Topic" not in classification_result.lower():
        response = general_chain.invoke({"question": question})
    else:
        response = answerchain.invoke({"context": context, "question": question})
    return response

def sessionname(question,context):
    response = sessionnamechain.invoke({"context": context, "question": question})
    return response