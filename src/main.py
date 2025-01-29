import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from flask_cors import CORS

model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1")

pc_apikey = "pcsk_6gdQRf_7G1DD6mozXD3NmdFYEc6TU9fcQMdM9USPxrjdt8qBBsrmiPt9EKtxyFAvivtxT1"
pinecone3 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="topic-store2")
pinecone4 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="content-store")

import psycopg2
conn = psycopg2.connect(
    dbname="postgres",
    user="root",
    password="lms@123",
    host="65.1.143.128",
    port=5432,
    options = "-c search_path=lmstest"
)

#cursor.execute("SET search_path = lmstest")


import jwt
SECRET_KEY = "whyisitasitis"

import flask
import requests
app = flask.Flask(__name__)
CORS(app)


from controllers.auth import authenticateToken
from controllers.router import getContext

@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/auth/register", methods=["POST"])
def registerUser():
    return "Not Implemented", 501

@app.route("/auth/login", methods=["POST"])
def loginUser():
    return "Not Implemented", 501

@app.route("/auth", methods=["GET"])
def getUserProfile():
    return "Not Implemented", 501


@app.route("/chats", methods=["GET"])
def getChats():
    return "Not Implemented", 501

@app.route("/chats/latest", methods=["GET"])
def getLatestChat():
    return "Not Implemented", 501

@app.route("/chats/<chat_id>", methods=["GET"])
def getChatByID(chat_id):
    return "Not Implemented", 501

@app.route("/chats", methods=["POST"])
def createChat():
    return "Not Implemented", 501

@app.route("/chats/<chat_id>", methods=["PUT"])
def updateChat():
    return "Not Implemented", 501

@app.route("/chats/<chat_id>", methods=["DELETE"])
def deleteChat():
    return "Not Implemented", 501


# @app.route("/router/topic", methods=["POST"])
# def routeTopic():
#     data = flask.request.json
#     query = data.get("query")
#     course_id = data.get("course_id")
#     if query is None or course_id is None:
#         return "Bad Request", 400

#     filter = { "course_id": { "$eq": course_id } }
#     results = pinecone3.similarity_search_with_score(query, k=3, filter=filter)

#     return flask.jsonify([
#         { "metadata": doc.metadata, "topic": doc.page_content, "score": score } 
#         for doc, score in results
#     ]), 200

# @app.route("/router/content", methods=["POST"])
# def routeContent():
#     data = flask.request.json
#     query = data.get("query")
#     topic_id = data.get("topic_id")
#     if query is None or topic_id is None:
#         return "Bad Request", 400

#     # filter = { "topic_id": { "$eq": topic_id } }
#     filter = {}
#     results = pinecone4.similarity_search_with_score(query, k=5, filter=filter)

#     return flask.jsonify([
#         { "metadata": doc.metadata, "content": doc.page_content, "score": score }
#         for doc, score in results
#     ]), 200

@app.route("/content", methods=["POST"])
def createContent():
    cursor = conn.cursor()
    data = flask.request.json
    cls = data.get("class")
    course_id = data.get("course")
    subject_id = data.get("subject")
    topic_id = data.get("topic")
    content_id = data.get("content")
    link = data.get("link")

    try:
        assert isinstance(course_id,int)
        assert isinstance(subject_id, int)
        assert isinstance(topic_id, int)
        assert isinstance(content_id, int)
        assert isinstance(link, str)
    except:
        return flask.jsonify({"error":"Please give all ids as integer"}),400

    cursor.execute("SELECT name FROM subject WHERE subject_id = %s", (subject_id,))
    subject = cursor.fetchone()[0]
    cursor.execute("SELECT name, description FROM topic WHERE topic_id = %s", (topic_id,))
    topic, topic_desc = cursor.fetchone()

    try:
        # INSERT INTO PINECONE topic-store2
        documents = [Document(
            id = topic_id,
            page_content = f"{subject} {topic} {topic_desc}",
            metadata = { "cls": cls, "course_id": course_id, "subject_id": subject_id, "topic_id": topic_id }
        )]
        pinecone3.add_documents(documents)


        # INSERT INTO PINECONE content-store
        documents = PyPDFLoader(link).load()
        for doc in documents:
            doc.metadata["cls"] = cls
            doc.metadata["course_id"] = course_id
            doc.metadata["subject_id"] = subject_id
            doc.metadata["topic_id"] = topic_id
            doc.metadata["content_id"] = content_id
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        documents = text_splitter.split_documents(documents)
        pinecone4.add_documents(documents)

    except Exception as e:
        return flask.jsonify({"error": f"Error inserting in pinecone {str(e)}"}), 500

    return flask.jsonify({"content_id": content_id}), 200


@app.route("/query", methods=["POST"])
def query():
    cursor = conn.cursor()
    user_id = authenticateToken()
    if not user_id:
        return "Unauthorized", 401
    try:
        cursor.execute("SELECT course_id FROM users WHERE user_id = %s", (user_id,))
        course_id = cursor.fetchone()[0]
        if not course_id:
            return "Unauthorized", 401

        data = flask.request.json
        query = data.get("query")
        # context = data.get("context")
        stream = data.get("stream")
        if not stream: stream = False
        
        context, topic_ids = getContext(query, course_id)
    
        rag_query = f"""
            context: {context}
            prompt: {query}
        """
    
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:1b",
            "prompt": rag_query,
            "stream": stream
        }, stream=stream)

        if stream:
            response = ""
            def generate_response():
                yield json.dumps({"context": context, "query": query, "topic_ids": topic_ids}) + "\n"
                for chunk in response.iter_content(chunk_size=None):  # chunk_size=None for streaming
                    chunk = chunk.decode("utf-8")
                    response += json.loads(chunk).response
                    yield chunk
    
            # SOMEHOW Put the things into the Database
            return flask.Response(generate_response(), content_type="application/json")
        else:
            #cursor.execute("INSERT INTO chats (user_id, prompt, response) VALUES (%s, %s, %s) RETURNING chat_id", (user_id, query, response.json()))
            return flask.jsonify(response.json()), 200
        
        # cursor.execute("INSERT INTO chats (user_id, prompt, response) VALUES ($1, $2, $3, $4) RETURNING chat_id", )
    except Exception as e:
        return flask.jsonify({"error":str(e)}), 500



if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
