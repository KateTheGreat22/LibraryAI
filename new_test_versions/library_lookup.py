import webbrowser

def open_byui_lookup(isbn, title, author):
    base = "https://byui.ent.sirsi.net/client/en_US/main/search/results"
    
    # Remove the 'if not isbn' exit condition entirely, and use this layout:
    if isbn:
        # 1. Precise lookup using ISBN
        url = f"{base}?qu={isbn}&te=ILS&rt=false|||ISBN|||ISBN"
        print(f"Opening BYUI Library Catalog for ISBN: {isbn}...")
    else:
        # 2. Fallback lookup using Title and Author
        search_query = f"{title} {author}"
        url = f"{base}?qu={search_query}"
        print(f"No ISBN found. Opening BYUI Catalog search for: '{search_query}'...")
        
    webbrowser.open(url)