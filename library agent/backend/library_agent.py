import os
import re
import sqlite3

from datetime import date, timedelta
from difflib import get_close_matches
from io import StringIO
from contextlib import redirect_stdout

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DB_PATH = os.path.join(
    DATABASE_DIR,
    "library.db"
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)

CORS(app)


@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        FRONTEND_DIR,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        FRONTEND_DIR,
        "script.js"
    )


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cur = conn.cursor()

# ============================================================
# LIBRARY RULES
# ============================================================

LOAN_DAYS = 14
FINE_PER_DAY = 5
TYPO_CUTOFF = 0.75


# ============================================================
# DATABASE SETUP
# ============================================================

cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    total_copies INTEGER NOT NULL,
    available_copies INTEGER NOT NULL
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    borrower TEXT NOT NULL,
    due_date TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id)
)
""")


# ============================================================
# BOOK DATA
# ============================================================

BOOKS = [
    ("The Jungle Book", "Rudyard Kipling", 3),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", 4),
    ("The Alchemist", "Paulo Coelho", 2),
    ("Wings of Fire", "A.P.J. Abdul Kalam", 3),
    ("Malgudi Days", "R.K. Narayan", 2),
    ("The Guide", "R.K. Narayan", 2),
    ("The Blue Umbrella", "Ruskin Bond", 2),
    ("Gulliver's Travels", "Jonathan Swift", 2),
    ("Alice's Adventures in Wonderland", "Lewis Carroll", 2),
    ("Around the World in 80 Days", "Jules Verne", 2),
    ("Panchatantra", "Vishnu Sharma", 3),
    ("The Secret Garden", "Frances Hodgson Burnett", 2),
]


# ============================================================
# SAMPLE LOANS
# ============================================================

SAMPLE_LOANS = [
    ("The Alchemist", "Riya", 5),
    ("The Alchemist", "Kiran", -3),
    ("The Guide", "Asha", 10),
    ("The Guide", "Ravi", 2),
    ("Gulliver's Travels", "Meena", -7),
    ("Gulliver's Travels", "Arjun", 6),
    ("Harry Potter and the Philosopher's Stone", "Priya", 4),
    ("Harry Potter and the Philosopher's Stone", "Rohan", -1),
    ("The Jungle Book", "Sam", -5),
]


# ============================================================
# SEED DATABASE
# ============================================================

def seed_books_if_needed():
    """
    Insert the sample books and sample loans if the database
    does not already contain the expected inventory.
    """

    rows = cur.execute(
        "SELECT total_copies, available_copies FROM books"
    ).fetchall()

    old_data = (
        len(rows) == len(BOOKS)
        and all(
            total == 1 and avail in (0, 1)
            for total, avail in rows
        )
    )

    if rows and not old_data:
        return

    cur.execute("DELETE FROM books")
    cur.execute("DELETE FROM loans")

    cur.executemany(
        """
        INSERT INTO books
        (title, author, total_copies, available_copies)
        VALUES (?, ?, ?, ?)
        """,
        [
            (title, author, copies, copies)
            for title, author, copies in BOOKS
        ],
    )

    for title, borrower, days in SAMPLE_LOANS:

        due = (
            date.today() + timedelta(days=days)
        ).isoformat()

        cur.execute(
            """
            INSERT INTO loans
            (book_id, borrower, due_date)
            SELECT id, ?, ?
            FROM books
            WHERE title = ?
            """,
            (borrower, due, title),
        )

        cur.execute(
            """
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE title = ?
            """,
            (title,),
        )

    conn.commit()


seed_books_if_needed()


# ============================================================
# CHATBOT KEYWORDS
# ============================================================

KEYWORDS = [
    "borrow",
    "borrowed",
    "return",
    "overdue",
    "late",
    "available",
    "copies",
    "copy",
    "many",
    "number",
    "count",
    "list",
    "books",
    "help",
    "menu",
    "thanks",
    "thank",
    "hello",
]


IGNORE_WORDS = {
    "the",
    "a",
    "an",
    "of",
    "in",
    "and",
    "book",
    "books",
    "copy",
    "copies",
}


MENU = """
---------------- MENU ----------------
1. Search for a book
2. Show available books
3. Show all books
4. Show borrowed books
5. Show overdue books
6. Find books by an author
7. Borrow a book
8. Return a book
9. Check no. of copies for a book
10. Help
0. Exit
--------------------------------------
"""


HELP = """
Pick a number from the menu, or just ask in your own words.
Spelling mistakes are fine.

Examples:

Is Harry Potter available?
Who wrote Malgudi Days?
Books by R.K. Narayan
How many copies of The Jungle Book are there?
Borrow The Jungle Book by Alex
Return The Jungle Book by Alex
What is overdue?

Type 'menu' to see the menu again, or 'exit' to stop.
"""


# ============================================================
# UNDERSTANDING USER WORDS
# ============================================================

def words_of(text):
    """
    'Philosopher's Stone!' -> ['philosophers', 'stone']
    """
    return re.findall(
        r"[a-z0-9]+",
        text.lower().replace("'", "")
    )


def word_matches(word, candidates):
    """
    Return the candidate that equals word or is a close spelling.
    """

    if word in candidates:
        return word

    if len(word) >= 4:

        close = get_close_matches(
            word,
            candidates,
            n=1,
            cutoff=TYPO_CUTOFF
        )

        if close:
            return close[0]

    return None


def fix_typos(words):
    """
    Fix misspelled command words.
    Words after 'by' are names and are left alone.
    """

    fixed = []
    after_by = False

    for word in words:

        after_by = after_by or word == "by"

        fixed.append(
            word
            if after_by
            else word_matches(word, KEYWORDS) or word
        )

    return fixed


def split_title_and_name(words, fixed, command):
    """
    Example:
    'please borrow the guide by Asha'
    -> ('the guide', 'Asha')
    """

    rest = words[fixed.index(command) + 1:]

    lowered = [w.lower() for w in rest]

    if "by" in lowered:

        i = lowered.index("by")

        return (
            " ".join(rest[:i]),
            " ".join(rest[i + 1:]).strip("?.!, ")
        )

    return " ".join(rest), ""


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_books(where="", params=()):
    """
    Return books as:
    (id, title, author, total, available)
    """

    cur.execute(
        f"""
        SELECT id, title, author, total_copies, available_copies
        FROM books
        {where}
        ORDER BY title
        """,
        params,
    )

    return cur.fetchall()


def find_books(query):
    """
    Find books by title or author.
    Allows minor spelling mistakes.
    """

    books = get_books()

    query_words = [
        w
        for w in words_of(query)
        if len(w) > 1 and w not in IGNORE_WORDS
    ]

    scores = []

    for _, title, author, _, _ in books:

        book_words = words_of(
            title + " " + author
        )

        score = 0

        for w in query_words:

            if w in book_words:
                score += 2

            elif word_matches(w, book_words):
                score += 1

        scores.append(score)

    best = max(scores, default=0)

    return [
        book
        for book, score in zip(books, scores)
        if best > 0 and score == best
    ]


def pick_book(title):
    """
    Return exactly one matching book.
    """

    matches = find_books(title)

    if not matches:

        print("I couldn't find that book.")
        return None

    elif len(matches) > 1:

        print(
            "Please be more specific. I found: "
            + ", ".join(b[1] for b in matches)
        )

        return None

    else:

        return matches[0]


def days_late(due):
    """
    Number of days past due date.
    """

    return max(
        0,
        (date.today() - date.fromisoformat(due)).days
    )


def late_note(due):

    late = days_late(due)

    if late:

        return (
            f"   <-- {late} day(s) late, "
            f"fine Rs. {late * FINE_PER_DAY}"
        )

    return ""


# ============================================================
# BOOK DISPLAY
# ============================================================

def print_books(books):

    if not books:

        print("Nothing found.")
        return

    for book_id, title, author, total, available in books:

        print(
            f"{title} by {author} - "
            f"{available}/{total} available"
        )

        cur.execute(
            """
            SELECT borrower, due_date
            FROM loans
            WHERE book_id = ?
            """,
            (book_id,),
        )

        for borrower, due in cur.fetchall():

            print(
                f"    borrowed by {borrower}, "
                f"due {due}{late_note(due)}"
            )


def print_book_copy_counts(book):

    if book is not None:

        _, title, author, total, available = book

        print(
            f"{title} by {author} - "
            f"{total} total copies, "
            f"{available} available"
        )


def show_available():

    print_books(
        get_books("WHERE available_copies > 0")
    )


def show_loans(only_overdue=False):

    query = """
        SELECT
            b.title,
            l.borrower,
            l.due_date
        FROM loans l
        JOIN books b ON b.id = l.book_id
    """

    params = ()

    if only_overdue:

        query += " WHERE l.due_date < ?"

        params = (
            date.today().isoformat(),
        )

    cur.execute(
        query + " ORDER BY l.due_date",
        params
    )

    rows = cur.fetchall()

    if not rows:

        print("Nothing found.")
        return

    for title, borrower, due in rows:

        print(
            f"{title} - {borrower}, "
            f"due {due}{late_note(due)}"
        )


# ============================================================
# BORROW BOOK
# ============================================================

def borrow_book(title, borrower, interactive=True):

    if not title:

        if interactive:

            title = input(
                "Which book would you like to borrow? "
            )

        else:

            print(
                "Please provide the book title."
            )

            return

    book = pick_book(title)

    if book is None:
        return

    if book[4] == 0:

        print(
            f"Sorry, no copies of {book[1]} "
            f"are available right now."
        )

        return

    if not borrower:

        if interactive:

            borrower = input(
                "What is your name? "
            ).strip()

        else:

            print(
                "Please provide your name using "
                "'Borrow Book Name by YourName'."
            )

            return

    if not borrower:

        print(
            "I need a name to issue the book."
        )

        return

    due = (
        date.today() +
        timedelta(days=LOAN_DAYS)
    ).isoformat()

    cur.execute(
        """
        INSERT INTO loans
        (book_id, borrower, due_date)
        VALUES (?, ?, ?)
        """,
        (
            book[0],
            borrower,
            due
        ),
    )

    cur.execute(
        """
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE id = ?
        """,
        (book[0],),
    )

    conn.commit()

    print(
        f"Done! {book[1]} is borrowed by "
        f"{borrower}. Please return it by {due}."
    )


# ============================================================
# RETURN BOOK
# ============================================================

def return_book(title, borrower, interactive=True):

    if not title:

        if interactive:

            title = input(
                "Which book are you returning? "
            )

        else:

            print(
                "Please provide the book title."
            )

            return

    book = pick_book(title)

    if book is None:
        return

    cur.execute(
        """
        SELECT id, borrower, due_date
        FROM loans
        WHERE book_id = ?
        """,
        (book[0],),
    )

    loans = cur.fetchall()

    if not borrower and len(loans) > 1:

        if interactive:

            borrower = input(
                "More than one person has this book. "
                "Your name: "
            ).strip()

        else:

            print(
                "More than one person has this book. "
                "Please use 'Return Book by YourName'."
            )

            return

    matches = [
        l
        for l in loans
        if not borrower
        or l[1].lower() == borrower.lower()
    ]

    if not matches:

        print(
            f"No matching loan found for {book[1]}."
        )

        return

    loan_id, actual_borrower, due = matches[0]

    cur.execute(
        "DELETE FROM loans WHERE id = ?",
        (loan_id,),
    )

    cur.execute(
        """
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE id = ?
        """,
        (book[0],),
    )

    conn.commit()

    print(
        f"Thank you! {book[1]} has been returned "
        f"({actual_borrower})."
    )

    late = days_late(due)

    if late:

        print(
            f"It was {late} day(s) late. "
            f"Please pay a fine of "
            f"Rs. {late * FINE_PER_DAY}."
        )


# ============================================================
# MENU
# ============================================================

def menu_choice(choice):

    if choice == "1":

        print_books(
            find_books(
                input("Book title: ")
            )
        )

    elif choice == "2":

        show_available()

    elif choice == "3":

        print_books(get_books())

    elif choice == "4":

        show_loans()

    elif choice == "5":

        show_loans(only_overdue=True)

    elif choice == "6":

        print_books(
            find_books(
                input("Author name: ")
            )
        )

    elif choice == "7":

        borrow_book(
            input("Book title: "),
            input("Your name: ").strip()
        )

    elif choice == "8":

        return_book(
            input("Book title: "),
            input(
                "Your name (or press Enter to skip): "
            ).strip()
        )

    elif choice == "9":

        print_book_copy_counts(
            pick_book(
                input("Book title: ")
            )
        )

    elif choice == "10":

        print(HELP)

    else:

        print(
            "Please choose a number from 0 to 10."
        )


# ============================================================
# CHATBOT ANSWER
# ============================================================

def answer(question, interactive=True):
    """
    Understand a typed question.
    Works for both CLI and web frontend.
    """

    words = question.split()

    if not words:

        print(
            "Please pick a number or type a question."
        )

        return

    fixed = fix_typos(
        [
            w.lower().strip("?.,!")
            for w in words
        ]
    )

    q = " ".join(fixed)

    def has(*keywords):

        return any(
            k in fixed
            for k in keywords
        )

    if (
        fixed[0] in
        ("hi", "hii", "hey", "hello")
        and len(fixed) <= 2
    ):

        print(
            "Hello! Type 'menu' to see the options "
            "or 'help' for examples."
        )

    elif (
        has("thanks", "thank")
        and len(fixed) <= 3
    ):

        print("You're welcome!")

    elif q == "menu":

        print(MENU)

    elif (
        has("help")
        and len(fixed) <= 3
    ):

        print(HELP)

    elif has("borrow"):

        title, borrower = split_title_and_name(
            words,
            fixed,
            "borrow"
        )

        borrow_book(
            title,
            borrower,
            interactive
        )

    elif has("return"):

        title, borrower = split_title_and_name(
            words,
            fixed,
            "return"
        )

        return_book(
            title,
            borrower,
            interactive
        )

    elif has("overdue", "late"):

        show_loans(
            only_overdue=True
        )

    elif has("borrowed"):

        matches = find_books(q)

        if matches:

            print_books(matches)

        else:

            show_loans()

    elif (
        has(
            "copies",
            "copy",
            "many",
            "number",
            "count"
        )
        and find_books(q)
    ):

        print_book_copy_counts(
            pick_book(q)
        )

    else:

        matches = find_books(q)

        if matches:

            print_books(matches)

        elif has("available"):

            show_available()

        elif has(
            "all",
            "books",
            "list",
            "everything"
        ):

            print_books(
                get_books()
            )

        else:

            print(
                "Sorry, I didn't understand that. "
                "Type 'menu' or 'help' to see what I can do."
            )


# ============================================================
# FRONTEND API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "response": "Invalid request."
        }), 400

    message = data.get("message", "").strip()

    if not message:

        return jsonify({
            "response": "Please enter a message."
        }), 400

    # Menu numbers require interactive terminal input,
    # so the web frontend uses natural-language questions.
    if message.isdigit():

        return jsonify({
            "response":
                "Please use a natural-language question "
                "in the web chatbot. For example: "
                "'Show available books'."
        })

    output = StringIO()

    try:

        with redirect_stdout(output):

            answer(
                message,
                interactive=False
            )

        response = output.getvalue().strip()

        return jsonify({
            "response": response
        })

    except Exception as e:

        return jsonify({
            "response":
                f"An error occurred: {str(e)}"
        }), 500


# ============================================================
# CLI CHATBOT
# ============================================================

def main():

    print("=" * 40)
    print("     SCHOOL LIBRARY CHATBOT")
    print("=" * 40)

    print(
        "\nWelcome! I can help you "
        "with your library needs."
    )

    print(MENU)

    print(
        "\nPick a number, or just ask in "
        "your own words. Type 'help' for examples.\n"
    )

    try:

        while True:

            question = input(
                "You: "
            ).strip()

            if question.lower() in (
                "0",
                "exit",
                "quit",
                "bye"
            ):

                print(
                    "Chatbot: Goodbye!"
                )

                break

            if not question:

                print(
                    "Please pick a number or "
                    "type a question."
                )

            elif question.isdigit():

                menu_choice(question)

            else:

                answer(question)

            print()

    except (
        KeyboardInterrupt,
        EOFError
    ):

        print(
            "\nChatbot: Goodbye!"
        )

    finally:

        conn.close()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    # Run the web backend.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )