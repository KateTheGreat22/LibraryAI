import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# 1. Setup the Database
# This creates a folder on your computer to store the "data map"
client = chromadb.PersistentClient(path="./book_vector_db")

# Use a built-in AI model to turn text into vectors
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Create a 'Collection' (think of it like a Table in SQL)
collection = client.get_or_create_collection(
    name="childrens_books", 
    embedding_function=default_ef
)

# 2. Prepare the Data
df = pd.read_csv("large_books_table.csv").fillna("")

# Combine columns so the AI has full context for each book
documents = (df['Title'] + ": " + df['Keywords'] + " " + df['Plot summary']).tolist()

# Metadata helps you filter by specific columns later (like Genre)
metadatas = df.to_dict(orient='records')

# IDs must be unique strings
ids = [str(i) for i in range(len(df))]

# 3. Import into the Vector DB
# Chroma handles the "Embedding" (turning text to numbers) automatically here
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"Successfully indexed {len(df)} books!")

# 4. The Smart Search
def smart_search(query_text, n_results=3):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results


# Even if the word "Yuletide" isn't in your CSV, it will find "The Polar Express"
my_results = smart_search("A festive Yuletide story with train magic")
#print(my_results['documents'])

print("\n--- AI Book Finder ---")

# 1. Ask the user for their vague description
user_prompt = input("Describe the book you're looking for (e.g., 'a story about a hungry bug' or 'something festive'): ")

# 2. Query the database
# ChromaDB converts the user's words into a vector and finds the nearest match
results = collection.query(
    query_texts=[user_prompt],
    n_results=1  # We only want the single best match
)

# 3. Display the result intelligently
if results['metadatas'][0]:
    book_data = results['metadatas'][0][0] # Get the first match
    print(f"\nI think you're looking for: **{book_data['Title']}**")
    print(f"Genre: {book_data['Genre']}")
    print(f"Plot Summary: {book_data['Plot summary']}")
else:
    print("\nSorry, I couldn't find a close match for that description.")