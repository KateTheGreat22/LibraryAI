import chromadb
from chromadb.utils import embedding_functions
import webbrowser

def open_byui_lookup(isbn, title, author):
    base = "https://byui.ent.sirsi.net/client/en_US/main/search/results"
    
    if isbn:
        # 1. Clean up the ISBN string: split by spaces and stitch back together with ' OR '
        # '9780590407434 0590407435' becomes '9780590407434 OR 0590407435'
        isbn_clean = " OR ".join(isbn.split())
        
        # 2. Build a flexible general search query instead of a strict single field link
        url = f"{base}?qu={isbn_clean}&te=ILS"
        print(f"Opening BYUI Library Catalog for ISBN options: {isbn_clean}...")
    else:
        # FALLBACK: Combine Title and Author for a general catalog search
        search_query = f"{title} {author}"
        url = f"{base}?qu={search_query}"
        print(f"No ISBN found. Opening BYUI Catalog search for: '{search_query}'...")
        
    webbrowser.open(url)

# 2. Connect to your PERMANENT local database directory
# This points directly to the 'chroma_db' folder your builder script made.
client = chromadb.PersistentClient(path="chroma_db")

# Use the exact same embedding function you used to build the database
embedding = embedding_functions.DefaultEmbeddingFunction()

# Access your existing "books" collection
collection = client.get_or_create_collection(
    name="books",
    embedding_function=embedding
)

print(f"Connected to database. Total books available to search: {collection.count()}")

# 3. Get the vague plot or "vibe" from the user
vague_prompt = input("\nDescribe the specific plot/vibe details you want to find: ")

# 4. Query the local collection for the top 5 matches
results = collection.query(
    query_texts=[vague_prompt],
    n_results=5,
    include=["metadatas", "distances"]
)

print("\n--- AI Rank: Top 5 Most Likely Matches ---")

# We will store the matches in a temporary list so we can access them by number later
top_matches = []

for i in range(len(results['metadatas'][0])):
    metadata = results['metadatas'][0][i]
    distance = results['distances'][0][i]
    
    # Calculate confidence based on semantic distance
    confidence = round((1 - distance) * 100, 1)
    top_matches.append(metadata)
    
    # 1. Safely extract values with upbeat, descriptive fallbacks if data is missing
    title = metadata.get('title', 'Unknown Title')
    author = metadata.get('author', 'Unknown Author')
    
    # If 'subjects' doesn't exist, use a default string instead
    subjects = metadata.get('subjects', 'No specific themes listed for this edition.')
    
    # If 'description' doesn't exist, use a default string instead
    description = metadata.get('description', 'No description available. A mystery waiting to be read!')

    # 2. Print out the beautifully formatted card
    print(f"{i + 1}. {title} by {author} ({confidence}% Match)")
    print(f"   Themes: {subjects[:120]}...")
    print(f"   Description: {description[:180]}...")
    print("-" * 50) # Prints a neat visual line divider between book choices

# 5. Let the user select a book to open in the BYUI Catalog
try:
    choice = int(input("Enter the number (1-5) of the book you want to look up at the BYUI Library: "))
    if 1 <= choice <= 5:
        # Retrieve the chosen book's metadata
        chosen_book = top_matches[choice - 1]
        
        # Pull the lowercase fields that you saved in your database
        isbn_to_search = chosen_book.get("isbn")
        title_to_search = chosen_book.get("title")
        author_to_search = chosen_book.get("author")
        
        # Send ALL THREE to the library function!
        open_byui_lookup(isbn_to_search, title_to_search, author_to_search)
    else:
        print("Invalid choice. Please run the script again to search.")
except ValueError:
    print("Please enter a valid number.")