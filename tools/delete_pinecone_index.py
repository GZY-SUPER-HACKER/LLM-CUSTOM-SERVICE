from pinecone import Pinecone
from config import get_pinecone_api_key, get_pinecone_index_name

pc = Pinecone(api_key=get_pinecone_api_key())
index_name = get_pinecone_index_name()

if index_name in [i["name"] for i in pc.list_indexes()]:
    pc.delete_index(index_name)



print(pc.list_indexes())
