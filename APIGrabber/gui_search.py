import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
import chromadb
from chromadb.utils import embedding_functions
import webbrowser
import requests
import ctypes

# Native crisp High-DPI scaling for Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  

# =====================================================================
# 1. DATABASE & API SETUP
# =====================================================================
client = chromadb.PersistentClient(path="chroma_db")
embedding_function = embedding_functions.DefaultEmbeddingFunction()

# --- FORCED REBUILD FOR COSINE MATH ---
try:
    client.delete_collection(name="books")
    print("🧹 Successfully reset old L2 collection to make room for Cosine Similarity...")
except Exception:
    pass

# Initialize the new vector collection explicitly configured for Cosine Similarity spacing
collection = client.get_or_create_collection(
    name="books", 
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"} 
)

current_matches = []

def fetch_and_sync_live_data(query_word):
    """Cleans conversational sentences into keywords, then queries the live API with retry logic."""
    # 1. SMART KEYWORD SCRUBBER
    clean_query = query_word.lower()
    fluff_phrases = [
        "i am looking for a book about", "i am looking for a book", "i am looking for",
        "looking for books about", "looking for a book", "books about", "a book about",
        "that lives in a", "that has a", "set in a", "with a", "about a", "about", "for a"
    ]
    for phrase in fluff_phrases:
        clean_query = clean_query.replace(phrase, "")
        
    filler_words = ["i", "want", "find", "the", "and", "a", "an", "in", "on", "at", "by", "of", "to", "with", "that"]
    words = clean_query.split()
    filtered_words = [w for w in words if w not in filler_words]
    api_keyword = " ".join(filtered_words) if filtered_words else query_word
    
    print(f"📡 Background Sync: Conversational query scrubbed down to core tags: '{api_keyword}'")
    
    # 2. CREATE A RESILIENT RETRY SESSION
    url = "https://openlibrary.org/search.json"
    params = {"q": api_keyword, "limit": 12} 
    
    session = requests.Session()
    # Tell Python to automatically retry up to 2 times if the server blinks
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount("https://", adapter)
    
    try:
        # Bumping timeout to 7 seconds to give the public server room to breathe
        response = session.get(url, params=params, timeout=7)
        if response.status_code != 200:
            print(f"ℹ️ Server responded with status code {response.status_code}. Using local cache.")
            return
            
        data = response.json()
        docs = data.get("docs", [])
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, doc in enumerate(docs):
            title = doc.get("title", "Unknown Title")
            author_list = doc.get("author_name", [])
            author = author_list[0] if author_list else "Unknown Author"
            isbn_list = doc.get("isbn", [])
            isbn = isbn_list[0] if isbn_list else ""
            
            text_payload = f"Title: {title} | Author: {author} | Subject Context: {api_keyword}"
            documents.append(text_payload)
            metadatas.append({"title": title, "author": author, "isbn": isbn})
            
            unique_id = f"live_{idx}_{len(title)}_{abs(hash(title[:5] + author[:5]))}"
            ids.append(unique_id)
            
        if documents:
            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            print(f"✅ Background Sync: Successfully indexed {len(documents)} live books matching context.")
            
    except requests.exceptions.ConnectionError:
        print("🌐 Offline Mode: API rate limit reached or network down. Relying strictly on local database cache.")
    except Exception as e:
        print(f"⚠️ Background Sync Notice: {e} (Falling back to local database engine)")
# =====================================================================
# 2. LOGIC FUNCTIONS
# =====================================================================
def run_ai_search():
    vague_prompt = entry_search.get().strip()
    if not vague_prompt:
        messagebox.showwarning("Empty Query", "Please type a plot or vibe description first!")
        return

    root.config(cursor="watch")
    root.update()

    # 1. Fetch live API records and sync them into our local database store
    fetch_and_sync_live_data(vague_prompt)

    # 2. Reset previous viewport outputs
    listbox_results.delete(0, tk.END)
    current_matches.clear()

    # 3. Query the updated vector database using semantic matching
    results = collection.query(
        query_texts=[vague_prompt],
        n_results=5,
        include=["metadatas", "distances"]
    )

    root.config(cursor="")

    if not results['metadatas'] or not results['metadatas'][0]:
        listbox_results.insert(tk.END, " 🛑 No matches found. Try describing a different vibe!")
        return

    # 4. Render the top matches using our corrected Cosine percentage math
    for i in range(len(results['metadatas'][0])):
        metadata = results['metadatas'][0][i]
        distance = results['distances'][0][i]
        
        # Cosine Spacing Translation: Similarity = 1.0 - Distance
        similarity_score = 1.0 - distance
        confidence = round(max(0.0, min(1.0, similarity_score)) * 100, 1)
        
        current_matches.append(metadata)
        
        title = metadata.get('title', 'Unknown Title')
        author = metadata.get('author', 'Unknown Author')
        
        listbox_results.insert(tk.END, f" 🔍  [{confidence}% Match]   {title} — by {author}")

def open_selected_book():
    try:
        selected_index = listbox_results.curselection()[0]
        chosen_book = current_matches[selected_index]
    except IndexError:
        messagebox.showwarning("No Selection", "Please select a book from the list first!")
        return

    isbn = chosen_book.get("isbn", "")
    title = chosen_book.get("title", "Unknown Title")
    author = chosen_book.get("author", "Unknown Author")
    
    base = "https://byui.ent.sirsi.net/client/en_US/main/search/results"
    if isbn:
        isbn_clean = " OR ".join(isbn.split())
        url = f"{base}?qu={isbn_clean}&te=ILS"
    else:
        url = f"{base}?qu={title} {author}"
        
    webbrowser.open(url)

# =====================================================================
# 3. INTERFACE DESIGN & STYLING
# =====================================================================
root = tk.Tk()
root.title("BYUI Library AI Semantic Book Finder")
root.geometry("700x550")

APP_BG = "#396795"       
BYUI_BLUE = "#003366"    
ACTION_GREEN = "#1E7122" 

root.configure(bg=APP_BG)

# Inject application assets using absolute file paths matching your test environment
try:
    icon_image = tk.PhotoImage(file="c:/Users/Kaitl/OneDrive/Desktop/AIProject/new_test_versions/favicon-32x32.png")
    root.iconphoto(False, icon_image)
except Exception:
    pass 

style = ttk.Style()
style.theme_use("clam")
style.configure("TEntry", fieldbackground="white", bordercolor=APP_BG, padding=8)
style.configure("Search.TButton", background=BYUI_BLUE, foreground="white", font=("Segoe UI", 10, "bold"), padding=8)
style.map("Search.TButton", background=[("active", "#002244")])
style.configure("Action.TButton", background=ACTION_GREEN, foreground="white", font=("Segoe UI", 11, "bold"), padding=10)
style.map("Action.TButton", background=[("active", "#1B5E20")])

main_container = tk.Frame(root, bg=APP_BG)
main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

# Branding Module Header
try:
    large_logo = tk.PhotoImage(file="c:/Users/Kaitl/OneDrive/Desktop/AIProject/new_test_versions/android-chrome-192x192.png")
    logo_image = large_logo.subsample(4, 4)
except Exception:
    logo_image = None

label_title = tk.Label(main_container, text="  BYUI Library AI Book Finder", image=logo_image, compound=tk.LEFT, bg=APP_BG, fg="white", font=("Segoe UI", 16, "bold"))
if logo_image:
    label_title.image = logo_image  
label_title.pack(anchor=tk.W, pady=(0, 2))

label_subtitle = tk.Label(main_container, text="Describe a narrative plot or general vibe to search our local collection.", bg=APP_BG, fg="#E0E0E0", font=("Segoe UI", 9))
label_subtitle.pack(anchor=tk.W, pady=(0, 20))

# Search Input Component Row
frame_search = tk.Frame(main_container, bg=APP_BG)
frame_search.pack(fill=tk.X, pady=(0, 20))

entry_search = ttk.Entry(frame_search, font=("Segoe UI", 11), style="TEntry")
entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry_search.bind("<Return>", lambda event: run_ai_search())

btn_search = ttk.Button(frame_search, text="Find Matches", style="Search.TButton", command=run_ai_search)
btn_search.pack(side=tk.RIGHT)

# Bottom Anchor Navigation Row
frame_action = tk.Frame(main_container, bg=APP_BG)
frame_action.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

btn_open = ttk.Button(frame_action, text="🔗  Open Chosen Edition in BYUI Library Catalog", style="Action.TButton", command=open_selected_book)
btn_open.pack(fill=tk.X)

# Viewport Matrix Container Box
frame_results = tk.Frame(main_container, bg=APP_BG)
frame_results.pack(fill=tk.BOTH, expand=True)

label_results = tk.Label(frame_results, text="Top 5 Most Likely Matches:", bg=APP_BG, fg="white", font=("Segoe UI", 10, "bold"))
label_results.pack(anchor=tk.W, pady=(0, 5))

listbox_results = tk.Listbox(
    frame_results, 
    font=("Segoe UI", 11), 
    bg="white", 
    fg="#333333",
    selectbackground=BYUI_BLUE, 
    selectforeground="white",
    activestyle="none",
    highlightcolor=BYUI_BLUE,
    bd=1,
    relief="solid"
)
listbox_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 10))

root.mainloop()