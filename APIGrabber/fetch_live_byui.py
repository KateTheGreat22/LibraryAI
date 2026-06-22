import requests

def search_live_byui_catalog(query_word):
    print(f"📡 Querying the Open Library API for: '{query_word}'...")
    
    # Open Library's universal search endpoint
    url = "https://openlibrary.org/search.json"
    
    params = {
        "q": query_word,
        "limit": 10  # Pull the top 10 most relevant matches
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Request failed. Status code: {response.status_code}")
            return []
            
        print("✅ Received clean data payload! Parsing book metadata structures...")
        data = response.json()
        docs = data.get("docs", [])
        
        live_books = []
        for doc in docs:
            title = doc.get("title", "Unknown Title")
            
            # Authors are stored as a list, let's grab the first one safely
            author_list = doc.get("author_name", [])
            author = author_list[0] if author_list else "Unknown Author"
            
            # Grab an ISBN if available (useful for catalog linking later!)
            isbn_list = doc.get("isbn", [])
            isbn = isbn_list[0] if isbn_list else ""
            
            live_books.append({
                "title": title,
                "author": author,
                "isbn": isbn
            })
            
        print(f"\n✨ Extracted {len(live_books)} Live Books:")
        for idx, b in enumerate(live_books[:5], 1):
            print(f"   {idx}. {b['title']} — by {b['author']}")
            
        return live_books

    except Exception as e:
        print(f"❌ API connection broke down: {e}")
        return []

if __name__ == "__main__":
    search_live_byui_catalog("data science")