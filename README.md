# Overview

This project was my first attempt to better understand how artifical intellegence is written and used. This project has three different parts:
old test versions, new test versions, and the api grabber. This shows the evalution of my understanding on how to code AI and the different
approaches that were recommended to me by professionals I worked with.

This project searches through a library database to identify books without using a title or author. The thought process behind it was that if 
a patron asks a librarian to find them a book, but the patron does not have main identifying information, the librarian could still look through the 
data base using context clues the patron provides. Finally, the bot will let the user select their book and then redirect to the David O Mckay Library
to see if the book is currently available. 


[Software Demo Video](http://youtube.link.goes.here)

# Development Environment

I used Python for the code, and it combines several libraries to create an 
AI-powered semantic book search application. The graphical user interface is built with Python's built-in Tkinter library 
(including ttk and messagebox) to provide a desktop application where users can search for books using plot descriptions or themes. 
The project uses ChromaDB as a persistent vector database and its default embedding function to convert book descriptions and user 
queries into numerical embeddings, allowing searches based on meaning rather than exact keywords. Additional built-in libraries,
including csv, webbrowser, ctypes, and time, handle data processing, opening library catalog links, Windows high-DPI display support, 
and API rate limiting, while the external requests library retrieves book metadata from the Open Library API. Together, 
these libraries create a complete workflow that collects book data, builds a searchable vector database, and provides an
intuitive AI-driven interface for discovering books through semantic search.


# Useful Websites

{Make a list of websites that you found helpful in this project}

- PyTorch Deep Learning: https://www.youtube.com/watch?v=V_xro1bcAuA
- The AI Alliance: https://thealliance.ai

# Future Work

- Make the Combined Version cleaner and more efficent 
- Add a full break down of the code in a seperate file so it is easier to read
- Fix the BYUI logo in the Tkinter bot

