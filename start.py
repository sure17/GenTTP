import chromadb

client = chromadb.PersistentClient("example/chroma_database")

# Load the collection
list = client.list_collections()
for collection in list:
    print(collection.name)