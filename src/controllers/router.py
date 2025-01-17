from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1")

pc_apikey = "pcsk_25oCJP_NkpfLrNG7FrNpev3yRsvhPR1VmWQZuaUWbXdNvFbM16G2YMwdLH15wMRjqPHs8i"
pinecone3 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="topic-store2")
pinecone4 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="content-store")


def getContext(query, course_id):
    filter = { "course_id": { "$eq": course_id } }
    results = pinecone3.similarity_search_with_score(query, k=3, filter=filter)
    topic_ids = [
        doc.metadata["topic_id"]
        for doc, score in results
    ]

    filter = { "topic_id": { "$in": topic_ids } }
    results = pinecone4.similarity_search_with_score(query, k=5, filter=filter)
    return [
        doc.page_content
        for doc, score in results
    ], topic_ids

# def routeTopic(query, course_id):
#     filter = { "course_id": { "$eq": course_id } }
#     results = pinecone3.similarity_search_with_score(query, k=3, filter=filter)

#     topic_ids = [
#         doc.metadata["topic_id"]
#         for doc, score in results
#     ]

# def routeContent(query, topic_ids):
#     filter = { "topic_id": { "$in": topic_ids } }
#     results = pinecone4.similarity_search_with_score(query, k=5, filter=filter)

#     return [
#         doc.page_content
#         for doc, score in results
#     ]
