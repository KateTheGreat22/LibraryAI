import csv
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="chroma_db")
embedding = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="books",
    embedding_function=embedding
)

with open("books.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    docs = []
    metas = []
    ids = []

    for row in reader:

        text = row["embedding_text"]

        docs.append(text)
        metas.append(row)
        ids.append(row["isbn"] if row["isbn"] else row["title"])

    print("Indexing", len(docs), "books...")

    collection.add(
        documents=docs,
        metadatas=metas,
        ids=ids
    )

print("Vector database created.")