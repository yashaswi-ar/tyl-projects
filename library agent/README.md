# Library Agent

## Description

The Library Agent is a chatbot that helps users interact with a school library database.

Users can search for books, check availability, find books by an author, check borrowed and overdue books, borrow books, and return books.

The project contains a web frontend connected to a Python Flask backend and SQLite database.

---

## Features

- Search for books by title or keyword
- Check book availability
- Find books by author
- Display available books
- Display all books
- Check borrowed books
- Check overdue books
- Borrow a book
- Return a book
- Check the number of copies
- Handles minor spelling mistakes
- SQLite database
- Web-based frontend
- Python backend API

---

## Technologies Used

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask
- Flask-CORS

### Database

- SQLite

---

## Project Structure

```text
Library Agent/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   └── student_library_chatbot.py
│
├── database/
│   └── library.db
│
├── requirements.txt
├── .env.example
└── README.md