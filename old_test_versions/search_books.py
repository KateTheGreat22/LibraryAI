import chromadb
from chromadb.utils import embedding_functions
from library_lookup import open_byui_lookup

client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory="chroma_db"
    )
)

embedding = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_collection(
    name="books",
    embedding_function=embedding
)

print("\nBook Finder AI")

query = input("Describe the book: ")

results = collection.query(
    query_texts=[query],
    n_results=5,
    include=["metadatas", "distances"]
)

print("\nPossible Matches\n")

for i, data in enumerate(results["metadatas"][0]):

    dist = results["distances"][0][i]
    confidence = round((1 - dist) * 100, 1)

    print(i+1, ".", data["title"], "by", data["author"])
    print("Match:", confidence, "%")
    print("ISBN:", data["isbn"])
    print()

choice = input("Open library search for which result? (1-5 or enter to skip): ")

if choice.isdigit():

    index = int(choice) - 1
    isbn = results["metadatas"][0][index]["isbn"]

    if isbn:
        open_byui_lookup(isbn)