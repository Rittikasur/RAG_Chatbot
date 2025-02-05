import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from flask_cors import CORS
import jwt
import flask
import requests
from controllers.auth import authenticateToken
from controllers.model_router import llmroute,sessionname
from controllers.router import getContext
import psycopg2
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

ollamamodel = OllamaLLM(model="llama3.2:1b")

model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1")

pc_apikey = "pcsk_6gdQRf_7G1DD6mozXD3NmdFYEc6TU9fcQMdM9USPxrjdt8qBBsrmiPt9EKtxyFAvivtxT1"
pinecone3 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="topic-store2")
pinecone4 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="content-store")

conn = psycopg2.connect(
    dbname="postgres",
    user="root",
    password="lms@123",
    host="65.1.143.128",
    port=5432,
    options = "-c search_path=lmstest"
)

#cursor.execute("SET search_path = lmstest")



SECRET_KEY = "whyisitasitis"


app = flask.Flask(__name__)
CORS(app)



@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/sessions/<int:user_id>", methods=["GET"])
def get_sessions(user_id):
    """Fetch all sessions for a user, ordered by created_at (newest first)."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, created_at, name
            FROM sessions 
            WHERE user_id = %s 
            ORDER BY created_at DESC;
        """, (user_id,))
        sessions = cursor.fetchall()
        cursor.close()

        return flask.jsonify([
            {"session_id": s[0], "created_at": s[1],"name":s[2]} for s in sessions
        ]), 200

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@app.route("/chats/<int:session_id>", methods=["GET"])
def get_chats(session_id):
    """Fetch all chats for a session, ordered by created_at (oldest first)."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chat_id, user_id, prompt, response, created_at 
            FROM chats 
            WHERE session_id = %s 
            ORDER BY created_at ASC;
        """, (session_id,))
        chats = cursor.fetchall()
        cursor.close()

        return flask.jsonify([
            {"chat_id": c[0], "user_id": c[1], "prompt": c[2], "response": c[3], "created_at": c[4]}
            for c in chats
        ]), 200

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


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



@app.route("/route", methods=["POST"])
def route():
    cursor = conn.cursor()
    user_id = authenticateToken()
    if not user_id:
        return "Unauthorized", 401
    try:
        cursor.execute("SELECT course_id FROM users WHERE user_id = %s", (user_id,))
        data = flask.request.json
        query = data.get("query")
        course_id = cursor.fetchone()[0]
        if not course_id:
            return "Unauthorized", 401

        context, topic_ids = getContext(query, course_id)

        chain = (
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
        ctx = ''.join(context)
        response = chain.invoke({"context":ctx,"question": query})
        return flask.jsonify({"answer": response}), 200
    except Exception as e:
        return flask.jsonify({"error":str(e)}), 500


@app.route("/query", methods=["POST"])
def query():

    user_id = authenticateToken()
    if not user_id:
        return "Unauthorized", 401
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT course_id FROM users WHERE user_id = %s", (user_id,))
        course_id = cursor.fetchone()[0]
        if not course_id:
            return "Unauthorized", 401

        data = flask.request.json
        query = data.get("query")
        session_id = data.get("session_id")
        context, topic_ids = getContext(query, course_id)
        ctx = ''.join(context)
        response = llmroute(query,ctx)

        # Start a transaction
        cursor.execute("BEGIN;")

        if not session_id:
            # Create a new session and get its ID
            session_name = sessionname(query,ctx)
            print(session_name)
            print(type(session_name))
            cursor.execute("INSERT INTO sessions (user_id,name) VALUES (%s,%s) RETURNING session_id;", (user_id,session_name,))
            session_id = cursor.fetchone()[0]

        # Insert chat record
        cursor.execute("""
                    INSERT INTO chats (user_id, session_id, prompt, response) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING chat_id;
                """, (user_id, session_id, query, response))

        chat_id = cursor.fetchone()[0]

        # Commit transaction
        conn.commit()
        cursor.close()

        return flask.jsonify({
            "session_id": session_id,
            "chat_id": chat_id,
            "response": response
        }), 200
    except Exception as e:
        conn.rollback()
        return flask.jsonify({"error":str(e)}), 500



if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
