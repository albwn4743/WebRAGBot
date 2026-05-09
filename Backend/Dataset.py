from langchain_community.embeddings import HuggingFaceEmbeddings
import weaviate
from weaviate.classes.query import Filter
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv
load_dotenv()

def connect_weaviate():
    return weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
    skip_init_checks=True
    # print("Connected to:", WEAVIATE_URL)
)
    
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# -------- GET COLLECTION --------
def get_collection(client):
    return client.collections.get("WebDocument")

def search_query(query, client, embeddings):
    query_vector = embeddings.embed_query(query)
    query_lower = query.lower()

    collection = client.collections.get("CompanyDocs")

