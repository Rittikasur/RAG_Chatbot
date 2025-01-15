from langchain_huggingface import HuggingFaceEmbeddings
model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1")

from langchain_pinecone.vectorstores import PineconeVectorStore
pc_apikey = "pcsk_25oCJP_NkpfLrNG7FrNpev3yRsvhPR1VmWQZuaUWbXdNvFbM16G2YMwdLH15wMRjqPHs8i"
pinecone3 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="topic-store2")
pinecone4 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="content-store")

import psycopg2
conn = psycopg2.connect(
    dbname="postgres",
    user="root",
    password="lms@123",
    host="65.1.143.128",
    port=5432
)
cursor = conn.cursor()
cursor.execute("SET search_path = lmstest")


import flask
app = flask.Flask(__name__)

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


@app.route("/router/topic", methods=["POST"])
def routeTopic():
    data = flask.request.json
    query = data.get("query")
    course_id = data.get("course_id")
    if query is None or course_id is None:
        return "Bad Request", 400

    filter = { "course_id": { "$eq": course_id } }
    results = pinecone3.similarity_search_with_score(query, k=3, filter=filter)

    return flask.jsonify([
        { "metadata": doc.metadata, "topic": doc.page_content, "score": score } 
        for doc, score in results
    ]), 200

@app.route("/router/content", methods=["POST"])
def routeContent():
    data = flask.request.json
    query = data.get("query")
    topic_id = data.get("topic_id")
    if query is None or topic_id is None:
        return "Bad Request", 400

    filter = { "topic_id": { "$eq": topic_id } }
    results = pinecone4.similarity_search_with_score(query, k=5, filter=filter)

    return flask.jsonify([
        { "metadata": doc.metadata, "content": doc.page_content, "score": score }
        for doc, score in results
    ]), 200

@app.route("/content", methods=["POST"])
def createContent():
    data = flask.request.json
    cls = data.get("cls")
    course = data.get("course")
    subject = data.get("subject")
    topic = data.get("topic")
    content = data.get("content")
    link = data.get("link")

    # cursor.execute("SELECT * FROM class WHERE class_id = %s", (cls,))
    # result1 = cursor.fetchone()
    # if not result1:
    #     cursor.execute(
    #         "INSERT INTO class (class_id, name, code, search_key) VALUES (%s, %s, %s, %s)",
    #         (cls, f"Class {cls}", f"C{cls}", f"class-{cls}")
    #     )
    #     conn.commit()

    if isinstance(course, int):
        course_id = course
    else:
        cursor.execute("SELECT * FROM course WHERE name = %s AND class_id = %s", (course, cls))
        result2 = cursor.fetchone()
        if not result2:
            cursor.execute(
                "INSERT INTO course (class_id, user_id, name) VALUES (%s, %s, %s) RETURNING course_id",
                (cls, 1, course)
            )
            course_id = cursor.fetchone()[0]
            conn.commit()
        else:
            course_id = result2[0]

    if isinstance(subject, int):
        subject_id = subject
    else:
        cursor.execute("SELECT * FROM subject WHERE name = %s AND course_id = %s", (subject, course_id))
        result3 = cursor.fetchone()
        if not result3:
            cursor.execute(
                "INSERT INTO subject (course_id, name) VALUES (%s, %s) RETURNING subject_id",
                (course_id, subject)
            )
            subject_id = cursor.fetchone()[0]
            conn.commit()
        else:
            subject_id = result3[0]

    if isinstance(topic, int):
        topic_id = topic
    else:
        cursor.execute("SELECT * FROM topic WHERE name = %s AND subject_id = %s", (topic, subject_id))
        result4 = cursor.fetchone()
        if not result4:
            cursor.execute(
                "INSERT INTO topic (subject_id, name) VALUES (%s, %s) RETURNING topic_id",
                (subject_id, topic)
            )
            topic_id = cursor.fetchone()[0]
            conn.commit()

            # INSERT INTO PINECONE topic-store2
            # pinecone3.add_documents()
        else:
            topic_id = result4[0]

    cursor.execute("SELECT * FROM content WHERE topic_id = %s AND link = %s", (topic_id, link))
    result5 = cursor.fetchone()
    if result5:
        return "Conflict", 409

    cursor.execute(
        "INSERT INTO content (topic_id, name, link) VALUES (%s, %s, %s) RETURNING content_id",
        (topic_id, content, link)
    )
    content_id = cursor.fetchone()[0]
    conn.commit()
    # INSERT INTO PINECONE content-store

    return "Not Implemented", 501
    # return jsonify({"content_id": content_id}), 200



if __name__ == "__main__":
    app.run(debug=True)