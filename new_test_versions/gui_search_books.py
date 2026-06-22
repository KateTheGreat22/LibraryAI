import tkinter as tk
from tkinter import ttk  # Upgraded themed widgets package!
from tkinter import messagebox
import chromadb
from chromadb.utils import embedding_functions
import webbrowser
import ctypes  # Talk directly to Windows graphics

# Tell Windows to use native, crisp High-DPI scaling
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  # Safely skip if running on a non-Windows machine

# =====================================================================
# 1. DATABASE SETUP
# =====================================================================
client = chromadb.PersistentClient(path="chroma_db")
embedding = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="books", embedding_function=embedding)

current_matches = []

# =====================================================================
# 2. LOGIC FUNCTIONS
# =====================================================================
def run_ai_search():
    vague_prompt = entry_search.get().strip()
    if not vague_prompt:
        messagebox.showwarning("Empty Query", "Please type a plot or vibe description first!")
        return

    listbox_results.delete(0, tk.END)
    current_matches.clear()

    results = collection.query(
        query_texts=[vague_prompt],
        n_results=5,
        include=["metadatas", "distances"]
    )

    for i in range(len(results['metadatas'][0])):
        metadata = results['metadatas'][0][i]
        distance = results['distances'][0][i]
        confidence = round((1 - distance) * 100, 1)
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
        search_query = f"{title} {author}"
        url = f"{base}?qu={search_query}"
        
    webbrowser.open(url)

# =====================================================================
# 3. INTERFACE DESIGN & STYLING
# =====================================================================
root = tk.Tk()
root.title("BYUI Library AI Semantic Book Finder")
root.geometry("700x550")

# Unified color scheme constants
APP_BG = "#396795"       # Consistent blue background color
BYUI_BLUE = "#003366"    # Primary focus blue
ACTION_GREEN = "#1E7122" # Action execution green

root.configure(bg=APP_BG)

# Load the sharp 32x32 icon for high-DPI scaling windows
try:
    icon_image = tk.PhotoImage(file="c:/Users/Kaitl/OneDrive/Desktop/AIProject/new_test_versions/favicon-32x32.png")
    root.iconphoto(False, icon_image)
except Exception:
    pass # Prevents crashing if the file moves

# Configure TTK styles for consistent UI elements
style = ttk.Style()
style.theme_use("clam")

# Configure Text Entry Style
style.configure("TEntry", fieldbackground="white", bordercolor=APP_BG, padding=8)

# Configure Modern Buttons
style.configure("Search.TButton", background=BYUI_BLUE, foreground="white", font=("Segoe UI", 10, "bold"), padding=8)
style.map("Search.TButton", background=[("active", "#002244")])

style.configure("Action.TButton", background=ACTION_GREEN, foreground="white", font=("Segoe UI", 11, "bold"), padding=10)
style.map("Action.TButton", background=[("active", "#1B5E20")])

# --- APP CONTAINER FRAME ---
main_container = tk.Frame(root, bg=APP_BG)
main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

# --- TITLE SECTION ---
try:
    large_logo = tk.PhotoImage(file="c:/Users/Kaitl/OneDrive/Desktop/AIProject/new_test_versions/android-chrome-192x192.png")
    # Subsampling by 4 drops it perfectly from 192x192 down to a sharp 48x48 layout header
    logo_image = large_logo.subsample(4, 4)
except Exception:
    logo_image = None

label_title = tk.Label(
    main_container, 
    text="  BYUI Library AI Book Finder", 
    image=logo_image,                     
    compound=tk.LEFT,                     
    bg=APP_BG, 
    fg="white", 
    font=("Segoe UI", 16, "bold")
)
if logo_image:
    label_title.image = logo_image  # Keep variable memory reference
label_title.pack(anchor=tk.W, pady=(0, 2))

label_subtitle = tk.Label(main_container, text="Describe a narrative plot or general vibe to search our local collection.", bg=APP_BG, fg="#E0E0E0", font=("Segoe UI", 9))
label_subtitle.pack(anchor=tk.W, pady=(0, 20))

# --- SEARCH CONTROL ROW ---
frame_search = tk.Frame(main_container, bg=APP_BG)
frame_search.pack(fill=tk.X, pady=(0, 20))

entry_search = ttk.Entry(frame_search, font=("Segoe UI", 11), style="TEntry")
entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry_search.bind("<Return>", lambda event: run_ai_search())

btn_search = ttk.Button(frame_search, text="Find Matches", style="Search.TButton", command=run_ai_search)
btn_search.pack(side=tk.RIGHT)

# --- RESPONSIVE LAYOUT ENGINE MANAGEMENT ---
# By packing the floor elements BEFORE the central matches frame, 
# we ensure the green layout never gets squeezed or clipped out of view.

# 1. BOTTOM SYSTEM ACTION BUTTON (Locks to the floor)
frame_action = tk.Frame(main_container, bg=APP_BG)
frame_action.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

btn_open = ttk.Button(frame_action, text="🔗  Open Chosen Edition in BYUI Library Catalog", style="Action.TButton", command=open_selected_book)
btn_open.pack(fill=tk.X)

# 2. RESULTS LISTBOX ROW (Expands dynamically to fill remaining space)
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