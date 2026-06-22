import chromadb
from chromadb.utils import embedding_functions
from fetch_live_byui import search_live_byui_catalog  # Imports your web scraper!

# =====================================================================
# 1. DATABASE CONNECTION
# =====================================================================
# This connects directly to the chroma_db folder you just copied over
client = chromadb.PersistentClient(path="chroma_db")
embedding_function = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="books", embedding_function=embedding_function)

def sync_catalog_to_database(search_term):
    print(f"🚀 Starting Live Sync Pipeline for keyword: '{search_term}'...")
    
    # 2. Fetch the live data using your web scraper
    live_books = search_live_byui_catalog(search_term)
    
    if not live_books:
        print("⚠️ No live books retrieved. Pipeline stopped.")
        return

    print(f"⚡ Vectorizing and injecting {len(live_books)} books into ChromaDB...")
    
    # Preparation arrays for ChromaDB
    documents = []
    metadatas = []
    ids = []
    
    for idx, book in enumerate(live_books):
        title = book['title']
        author = book['author']
        
        # We combine title and author to create a descriptive text block for the AI to read
        text_payload = f"Title: {title} | Author: {author} | Available at BYUI Library."
        documents.append(text_payload)
        
        # Store clean metadata attributes
        metadatas.append({
            "title": title,
            "author": author,
            "isbn": ""  # Web catalogs often hide ISBNs inside deeper product pages, we can leave this blank for now
        })
        
        # Generate a unique string ID based on the title/author combo
        unique_id = f"live_{hash(title + author)}"
        ids.append(unique_id)
        
    # 3. Upsert (Insert or Update if already exists) into your database
    try:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"🎉 Success! Your ChromaDB now includes the live tracking data for '{search_term}'.")
    except Exception as e:
        print(f"❌ Failed to update ChromaDB: {e}")

if __name__ == "__main__":
    # Let's run a test sync for books about "data science"
    sync_catalog_to_database("data science")