import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings


def create_documents(df):
    documents = []

    for _, row in df.iterrows():
        text = f"""
        SKU: {row['sku']}
        Product: {row['name']}
        Category: {row['category']}
        Brand: {row['brand']}
        Vehicle Fitment: {row['vehicle_fitment']}
        Price: ₹{row['price_inr']}
        Stock: {row['stock']}
        Description: {row['description']}
        """

        documents.append(
            Document(page_content=text.strip())
        )

    return documents


load_dotenv()

df = pd.read_csv("data/catalogue.csv")  
documents = create_documents(df)

embeddings = HuggingFaceEmbeddings(

    model_name="sentence-transformers/all-MiniLM-L6-v2"

)

vectorstore = FAISS.from_documents(
    documents,
    embeddings
)

vectorstore.save_local("faiss_index")

print("FAISS index created successfully!")