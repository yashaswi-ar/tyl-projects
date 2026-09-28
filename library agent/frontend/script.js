const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const chatBox =
    document.getElementById("chat-box");

const menuResult =
    document.getElementById("menu-result");


/* ============================================================
   ADD MESSAGE TO CHAT
   ============================================================ */

function addMessage(message, sender) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");


    if (sender === "user") {

        messageDiv.classList.add(
            "user-message"
        );

    } else {

        messageDiv.classList.add(
            "bot-message"
        );
    }


    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);


    /* Always move chat to latest message */

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


/* ============================================================
   NORMAL CHAT
   ============================================================ */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (message === "") {
        return;
    }


    /* Add typed message to conversation */

    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    sendButton.disabled = true;


    try {

        const response =
            await fetch("/api/chat", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: message
                })

            });


        const data =
            await response.json();


        addMessage(
            data.response,
            "bot"
        );


    } catch (error) {

        addMessage(
            "Unable to connect to the Library Agent backend.",
            "bot"
        );

    } finally {

        sendButton.disabled = false;

        messageInput.focus();
    }
}


/* ============================================================
   SHOW MENU RESULT
   ============================================================ */

/*
   Menu results are NOT added to chat.

   Every new menu option replaces the
   previous menu result.
*/

function showMenuResult(title, content) {

    menuResult.innerHTML = `
        <strong>${title}</strong>

        <div style="margin-top: 7px;">
            ${content}
        </div>
    `;
}


/* ============================================================
   MENU REQUEST
   ============================================================ */

async function menuRequest(message, title) {

    showMenuResult(
        title,
        "Please wait..."
    );


    try {

        const response =
            await fetch("/api/chat", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: message
                })

            });


        const data =
            await response.json();


        const formatted =
            escapeHtml(data.response)
                .replace(/\n/g, "<br>");


        showMenuResult(
            title,
            formatted
        );


    } catch (error) {

        showMenuResult(
            title,
            "Unable to connect to the Library Agent backend."
        );
    }
}


/* ============================================================
   MENU ACTIONS
   ============================================================ */

function menuAction(action) {


    /* -----------------------------------------
       AVAILABLE
       ----------------------------------------- */

    if (action === "available") {

        menuRequest(
            "Show available books",
            "Available Books"
        );

        return;
    }


    /* -----------------------------------------
       ALL BOOKS
       ----------------------------------------- */

    if (action === "all") {

        menuRequest(
            "Show all books",
            "All Books"
        );

        return;
    }


    /* -----------------------------------------
       BORROWED
       ----------------------------------------- */

    if (action === "borrowed") {

        menuRequest(
            "Show borrowed books",
            "Borrowed Books"
        );

        return;
    }


    /* -----------------------------------------
       OVERDUE
       ----------------------------------------- */

    if (action === "overdue") {

        menuRequest(
            "What is overdue?",
            "Overdue Books"
        );

        return;
    }


    /* -----------------------------------------
       SEARCH
       ----------------------------------------- */

    if (action === "search") {

        showMenuResult(
            "Search Books",
            `
                <p>
                    Which book would you like to search for?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter book title"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'search')"
                >

                <button
                    onclick="submitMenuInput('search')"
                >
                    Search
                </button>
            `
        );


        focusMenuInput();

        return;
    }


    /* -----------------------------------------
       COPIES
       ----------------------------------------- */

    if (action === "copies") {

        showMenuResult(
            "Check Copies",
            `
                <p>
                    Which book would you like to check?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter book title"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'copies')"
                >

                <button
                    onclick="submitMenuInput('copies')"
                >
                    Check Copies
                </button>
            `
        );


        focusMenuInput();

        return;
    }


    /* -----------------------------------------
       BORROW
       ----------------------------------------- */

    if (action === "borrow") {

        showMenuResult(
            "Borrow Book",
            `
                <p>
                    Which book would you like to borrow?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter book title"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'borrow-book')"
                >

                <button
                    onclick="submitMenuInput('borrow-book')"
                >
                    Continue
                </button>
            `
        );


        focusMenuInput();

        return;
    }


    /* -----------------------------------------
       RETURN
       ----------------------------------------- */

    if (action === "return") {

        showMenuResult(
            "Return Book",
            `
                <p>
                    Which book would you like to return?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter book title"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'return-book')"
                >

                <button
                    onclick="submitMenuInput('return-book')"
                >
                    Continue
                </button>
            `
        );


        focusMenuInput();

        return;
    }
}


/* ============================================================
   FOCUS MENU INPUT
   ============================================================ */

function focusMenuInput() {

    setTimeout(() => {

        const input =
            document.getElementById(
                "menu-input"
            );

        if (input) {
            input.focus();
        }

    }, 50);
}


/* ============================================================
   ENTER KEY FOR MENU INPUT
   ============================================================ */

function menuEnter(event, action) {

    if (event.key === "Enter") {

        submitMenuInput(action);

    }
}


/* ============================================================
   MENU INPUT
   ============================================================ */

async function submitMenuInput(action) {

    const input =
        document.getElementById(
            "menu-input"
        );


    if (!input) {
        return;
    }


    const value =
        input.value.trim();


    if (value === "") {
        return;
    }


    /* -----------------------------------------
       SEARCH
       ----------------------------------------- */

    if (action === "search") {

        await menuRequest(
            `Search for ${value}`,
            "Search Books"
        );

        return;
    }


    /* -----------------------------------------
       COPIES
       ----------------------------------------- */

    if (action === "copies") {

        await menuRequest(
            `How many copies of ${value} are there?`,
            "Check Copies"
        );

        return;
    }


    /* -----------------------------------------
       BORROW BOOK
       ----------------------------------------- */

    if (action === "borrow-book") {

        showMenuResult(
            "Borrow Book",
            `
                <p>
                    Book:
                    <strong>${escapeHtml(value)}</strong>
                </p>

                <p>
                    What is your name?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter your name"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'borrow-name')"
                >

                <button
                    onclick="submitBorrowName('${escapeAttribute(value)}')"
                >
                    Borrow Book
                </button>
            `
        );


        focusMenuInput();

        return;
    }


    /* -----------------------------------------
       RETURN BOOK
       ----------------------------------------- */

    if (action === "return-book") {

        showMenuResult(
            "Return Book",
            `
                <p>
                    Book:
                    <strong>${escapeHtml(value)}</strong>
                </p>

                <p>
                    What is your name?
                </p>

                <input
                    type="text"
                    id="menu-input"
                    placeholder="Enter your name"
                    autocomplete="off"
                    onkeydown="menuEnter(event, 'return-name')"
                >

                <button
                    onclick="submitReturnName('${escapeAttribute(value)}')"
                >
                    Return Book
                </button>
            `
        );


        focusMenuInput();

        return;
    }
}


/* ============================================================
   BORROW NAME
   ============================================================ */

async function submitBorrowName(book) {

    const input =
        document.getElementById(
            "menu-input"
        );


    if (!input) {
        return;
    }


    const name =
        input.value.trim();


    if (name === "") {
        return;
    }


    showMenuResult(
        "Borrow Book",
        "Processing..."
    );


    await menuRequest(
        `Borrow ${book} by ${name}`,
        "Borrow Book"
    );
}


/* ============================================================
   RETURN NAME
   ============================================================ */

async function submitReturnName(book) {

    const input =
        document.getElementById(
            "menu-input"
        );


    if (!input) {
        return;
    }


    const name =
        input.value.trim();


    if (name === "") {
        return;
    }


    showMenuResult(
        "Return Book",
        "Processing..."
    );


    await menuRequest(
        `Return ${book} by ${name}`,
        "Return Book"
    );
}


/* ============================================================
   HTML SAFETY
   ============================================================ */

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


function escapeAttribute(text) {

    return text
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'");
}


/* ============================================================
   SEND BUTTON
   ============================================================ */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* ============================================================
   ENTER KEY FOR CHAT
   ============================================================ */

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            sendMessage();

        }

    }
);