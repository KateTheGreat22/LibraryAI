import requests
import csv
import time

OUTPUT_FILE = "books.csv"
MAX_BOOKS = 5000
RESULTS_PER_PAGE = 100

FIELDS = [
    "title",
    "author",
    "isbn",
    "characters",
    "places",
    "subjects",
    "description",
    "embedding_text"
]

def extract_description(book):
    """Safely extract description text"""
    fs = book.get("first_sentence")

    if isinstance(fs, list) and len(fs) > 0:
        return fs[0]

    if isinstance(fs, str):
        return fs

    return ""


def build_embedding_text(title, author, characters, places, subjects, description):
    """Combine fields into a strong embedding string"""
    return (
        f"Title: {title}. "
        f"Author: {author}. "
        f"Characters: {characters}. "
        f"Places: {places}. "
        f"Themes: {subjects}. "
        f"Description: {description}"
    )


def fetch_books():

    saved_books = 0
    page = 1
    seen_ids = set()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        while saved_books < MAX_BOOKS:

            url = (
                "https://openlibrary.org/search.json"
                f"?q=fiction"
                f"&language=eng"
                f"&limit={RESULTS_PER_PAGE}"
                f"&page={page}"
            )

            print(f"Fetching page {page}...")

            try:
                response = requests.get(url, timeout=10)
                data = response.json()
            except Exception as e:
                print("API request failed:", e)
                break

            docs = data.get("docs", [])

            if not docs:
                print("No more books found.")
                break

            for book in docs:

                title = book.get("title", "")
                author = ", ".join(book.get("author_name", []))

                isbn_list = book.get("isbn", [])
                # Join all available ISBNs into a single space-separated string
                isbn = " ".join(isbn_list) if isbn_list else ""

                # Avoid duplicates
                unique_id = isbn if isbn else title
                if unique_id in seen_ids:
                    continue

                seen_ids.add(unique_id)

                characters = ", ".join(book.get("person", []))
                places = ", ".join(book.get("place", []))
                subjects = ", ".join(book.get("subject", []))

                description = extract_description(book)

                embedding_text = build_embedding_text(
                    title,
                    author,
                    characters,
                    places,
                    subjects,
                    description
                )

                writer.writerow({
                    "title": title,
                    "author": author,
                    "isbn": isbn,
                    "characters": characters,
                    "places": places,
                    "subjects": subjects,
                    "description": description,
                    "embedding_text": embedding_text
                })

                saved_books += 1

                if saved_books >= MAX_BOOKS:
                    break

            print(f"Saved so far: {saved_books}")

            page += 1

            # prevent API abuse
            time.sleep(0.15)

    print(f"\nFinished. {saved_books} books saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_books()