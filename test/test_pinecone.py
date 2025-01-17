from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1")

pc_apikey = "pcsk_25oCJP_NkpfLrNG7FrNpev3yRsvhPR1VmWQZuaUWbXdNvFbM16G2YMwdLH15wMRjqPHs8i"
pinecone3 = PineconeVectorStore(pinecone_api_key=pc_apikey, embedding=model, index_name="topic-store2")

doc = Document(page_content="Hiiii")

pinecone3.add_documents([doc])