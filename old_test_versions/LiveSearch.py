import requests
import chromadb
from chromadb.utils import embedding_functions

# 1. Setup the Database (In-Memory for high-speed session search)
client = chromadb.PersistentClient(path="chroma_db")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="web_cache", 
    embedding_function=default_ef
)

def fetch_from_web():
    print("\n--- Advanced AI Web Search ---")
    keyword = input("Enter broad keywords (e.g., 'March sisters' or 'Stoker Transylvania'): ") 
    
    # Logic to detect if we should allow collections/anthologies
    wants_bundle = any(word in keyword.lower() for word in ["anthology", "collection", "complete", "works"])
    
    # DOUBLE-NET SEARCH: Scans general index and specific subject tags
    url = f"https://openlibrary.org/search.json?q={keyword}&subject={keyword}&language=eng&limit=150"
    
    print(f"Deep-scanning Open Library for '{keyword}'...")
    try:
        response = requests.get(url).json()
    except Exception as e:
        print(f"Error connecting to Open Library: {e}")
        return

    docs_to_add, metadatas_to_add, ids_to_add = [], [], []
    skipped_bundles = 0

    for i, book in enumerate(response.get('docs', [])):
        title = book.get('title', 'Unknown Title')
        
        # --- ANTHOLOGY FILTER ---
        bundle_indicators = ["anthology", "collection", "complete works", "omnibus", "novels of", "selected works"]
        is_bundle = any(word in title.lower() for word in bundle_indicators)
        
        if is_bundle and not wants_bundle:
            skipped_bundles += 1
            continue

        # --- DATA EXTRACTION (The "Seed" Information) ---
        author = ", ".join(book.get('author_name', ['Unknown']))
        characters = ", ".join(book.get('person', [])) 
        subjects = ", ".join(book.get('subject', []))
        places = ", ".join(book.get('place', []))
        first_line = book.get('first_sentence', [''])[0]
        
        # THE AI BRAIN: This combined string is what the AI 'understands' about the book.
        # We repeat the title and add key details to strengthen the 'signal'.
        combined_text = (
            f"Title: {title}. Author: {author}. "
            f"Characters in the book: {characters}. "
            f"Set in: {places}. Themes: {subjects}. "
            f"Opening line: {first_line}"
        )

        docs_to_add.append(combined_text)
        metadatas_to_add.append({
            "Title": title,
            "Author": author,
            "Characters": characters[:100] if characters else "Common/Historical Figures",
            "Tags": subjects[:100] + "..."
        })
        ids_to_add.append(str(i))

    if docs_to_add:
        # Reset the cache for the new search
        existing = collection.get()
        if existing['ids']:
            collection.delete(ids=existing['ids'])
            
        collection.add(documents=docs_to_add, metadatas=metadatas_to_add, ids=ids_to_add)
        print(f"Success! Indexed {len(docs_to_add)} books (Filtered {skipped_bundles} anthologies).")
    else:
        print("No specific books found. Try simpler keywords (e.g., just the author's last name).")

# --- EXECUTION ---
fetch_from_web()

if collection.count() > 0:
    vague_prompt = input("\nDescribe the specific plot/vibe details: ")

    results = collection.query(
        query_texts=[vague_prompt],
        n_results=5,
        include=["metadatas", "distances"]
    )

    print("\n--- AI Rank: Most Likely Matches ---")
    for i in range(len(results['metadatas'][0])):
        data = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        
        # Calculate confidence: Closer to 100% is better. 
        # Low distance = High Match.
        confidence = round((1 - dist) * 100, 1) 
        
        print(f"{i+1}. {data['Title']} by {data['Author']} ({confidence}% Match)")
        print(f"   Known Characters: {data['Characters']}")
        print(f"   Library Tags: {data['Tags']}\n")
else:
    print("Search failed to return usable data.")