from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

query = "brake pads for bajaj pulsar 150"

results = vectorstore.similarity_search(
    query,
    k=3
)

for result in results:
    print(result.page_content)
    print("-" * 50)

#python tests/retrieval.py