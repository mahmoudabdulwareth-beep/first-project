import sqlite3
import bcrypt
import random
import tkinter as tk
from tkinter import ttk, messagebox



# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to register a new user
def register_user(username, password) -> tuple [bool,list[str]]:
    errors =[]
    if len(password)<8 :
        errors.append("password should have at least 8 characters")
    if not any(c.isupper() for c in password):# check if the password has atleast one capital letter
        errors.append("password should include at least one capital letter")
    if not any(c.islower() for c in password):
        errors.append("password should include at least one small letter")
    if not any(c.isdigit() for c in password ):
        errors.append("password should include at least one digit")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must include at least one special character")
    if password == username:
        errors.append("password should not be the same as username")
    if username.lower() in password.lower():# check if the username is in the password
        errors.append("password should not contain the username")

    if errors:
        return (False, errors)

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("Username already exists!")
        conn.close()
        return (False, ["Username already exists!"])

    # Hash the password before saving
    hashed_password = hash_password(password)

    # Insert new user into the users table
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    print("User registered successfully!")
    return (True, [])


# Function to verify password
def verify_password(stored_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password)


# Function to log in an existing user
def login_user(username, password):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Retrieve user by username
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        # Check if password matches the stored hashed password
        if verify_password(user[2], password):  # user[2] is the stored hashed password
            print(f"Login successful! Welcome, {username}!")
            conn.close()
            return True
        else:
            print("Incorrect password!")
            conn.close()
            return False
    else:
        print("User not found!")
        conn.close()
        return False


def add_book(title, author, genre):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)", (title, author, genre))
    conn.commit()
    conn.close()
    print("Book added successfully!")


def view_books(self):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # View all books, including borrowed ones
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()

    # Display books in the GUI
    if not books:
        messagebox.showinfo("No Books", "No books found in the library.")
        return

    book_list = "\n".join([f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}, Status: {'Borrowed' if book[5] == 1 else 'Available'}" for book in books])

    # Show the list of books in a message box or update the text area
    self.show_books(book_list)


def show_books(self, book_list):
    self.clear_screen()

    tk.Label(self.root, text="Books in Library", font=("Arial", 16)).pack(pady=10)

    # Show the list of books in a text widget
    book_text = tk.Text(self.root, height=10, width=50)
    book_text.insert(tk.END, book_list)
    book_text.config(state=tk.DISABLED)
    book_text.pack(pady=5)

    tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=5)


def issue_book(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE id = ? AND borrowed = 0", (book_id,))
    book = cursor.fetchone()

    if book:
        borrow_id = random.randint(1000, 9999)
        cursor.execute("UPDATE books SET borrowed = 1, borrow_id = ? WHERE id = ?", (borrow_id, book_id))
        conn.commit()
        conn.close()
        return borrow_id
    conn.close()
    return None


def return_book(borrow_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE borrow_id = ?", (borrow_id,))
    book = cursor.fetchone()

    if book:
        cursor.execute("UPDATE books SET borrowed = 0, borrow_id = NULL WHERE borrow_id = ?", (borrow_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def delete_book(self, book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    if cursor.rowcount == 0:
        print("Book ID not found!")
    else:
        print("Book deleted successfully!")
    conn.commit()
    conn.close()


class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")

        # Set color scheme
        self.colors = {
            'primary': '#2c3e50',  # Dark blue-grey
            'secondary': '#3498db',  # Bright blue
            'accent': '#e74c3c',  # Red
            'background': '#ecf0f1',  # Light grey
            'text': '#2c3e50',  # Dark blue-grey
            'white': '#ffffff',
            'black':'#0a0a0a'
        }

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Modern.TButton',
                             padding=10,
                             font=('Helvetica', 10))

        self.style.configure('Title.TLabel',
                             font=('Helvetica', 24, 'bold'),
                             foreground=self.colors['primary'])

        self.style.configure('Subtitle.TLabel',
                             font=('Helvetica', 16),
                             foreground=self.colors['primary'])

        # Set background color
        self.root.configure(bg=self.colors['background'])

        self.login_screen()

    def create_entry(self, parent, placeholder):
        """Create a modern looking entry widget"""
        frame = tk.Frame(parent, bg=self.colors['background'])
        frame.pack(pady=5)

        entry = ttk.Entry(frame, width=30, font=('Helvetica', 10))
        entry.insert(0, placeholder)
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(e, entry, placeholder))
        entry.bind('<FocusOut>', lambda e: self.on_focus_out(e, entry, placeholder))
        entry.pack(pady=5)

        return entry

    def on_entry_click(self, event, entry, placeholder):
        """Handle entry widget focus in"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if 'Password' in placeholder:
                entry.configure(show='*')

    def on_focus_out(self, event, entry, placeholder):
        """Handle entry widget focus out"""
        if entry.get() == '':
            entry.insert(0, placeholder)
            if 'Password' in placeholder:
                entry.configure(show='')

    def create_button(self, parent, text, command, is_primary=True):
        """Create a modern looking button"""
        btn = ttk.Button(parent, text=text, command=command, style='Modern.TButton')
        btn.pack(pady=10)
        return btn

    def login_screen(self):
        self.clear_screen()

        # Create main container
        container = tk.Frame(self.root, bg=self.colors['background'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        # Logo/Title
        ttk.Label(container, text="📚", font=('Helvetica', 48), style='Title.TLabel').pack(pady=10)
        ttk.Label(container, text="Library Management System", style='Title.TLabel').pack(pady=5)
        ttk.Label(container, text="Login to your account", style='Subtitle.TLabel').pack(pady=20)

        # Login form
        self.username_entry = self.create_entry(container, "Username")
        self.password_entry = self.create_entry(container, "Password")

        # Buttons container
        button_frame = tk.Frame(container, bg=self.colors['background'])
        button_frame.pack(pady=20)

        def login_action():
            username = self.username_entry.get()
            password = self.password_entry.get()

            if username == "Username" or password == "Password":
                messagebox.showerror("Error", "Please fill in all fields!")
                return

            if login_user(username, password):
                self.library_screen()
            else:
                messagebox.showerror("Login Failed", "Incorrect username or password.")

        # Create buttons with different styles
        self.create_button(button_frame, "Login", login_action, True)
        self.create_button(button_frame, "Register", self.register_screen, False)

    def register_screen(self):
        self.clear_screen()

        # Create main container
        container = tk.Frame(self.root, bg=self.colors['background'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        # Title
        ttk.Label(container, text="Create New Account", style='Title.TLabel').pack(pady=20)

        # Registration form
        username_entry = self.create_entry(container, "Username")
        password_entry = self.create_entry(container, "Password")
        confirm_password_entry = self.create_entry(container, "Confirm Password")

        def register_action():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if username == "Username" or password == "Password" or confirm_password == "Confirm Password":
                messagebox.showerror("Error", "Please fill in all fields!")
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return

            success, errors = register_user(username, password)

            if success:
                messagebox.showinfo("Success", "Registration successful!")
                self.login_screen()
            else:
                error_msg = "\n".join(f"• {e}" for e in errors)
                messagebox.showerror("Registration Failed", error_msg)
        # Buttons
        button_frame = tk.Frame(container, bg=self.colors['background'])
        button_frame.pack(pady=20)

        self.create_button(button_frame, "Register", register_action, True)
        self.create_button(button_frame, "Back to Login", self.login_screen, False)

    def library_screen(self):
        self.clear_screen()

        # Create header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        ttk.Label(header, text="Library Management System",
                  font=('Helvetica', 16, 'bold'),
                  foreground=self.colors['black']).pack(side='left', padx=20)

        ttk.Button(header, text="Logout",
                   command=self.login_screen,
                   style='Modern.TButton').pack(side='right', padx=20, pady=10)

        # Create main content area
        content = tk.Frame(self.root, bg=self.colors['background'])
        content.pack(fill='both', expand=True, padx=40, pady=40)

        # Create grid of buttons
        actions = [
            ("Add Book", self.add_book_screen),
            ("View Books", self.view_books),
            ("Issue Book", self.issue_book_screen),
            ("Return Book", self.return_book_screen),
            ("Borrow Details", self.borrow_details_screen),
            ("Delete Book", self.delete_book_screen)
        ]

        for i, (text, command) in enumerate(actions):
            frame = tk.Frame(content, bg=self.colors['white'],
                             padx=20, pady=20, relief='raised', bd=1)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky='nsew')

            # Icon (you can replace these with actual icons)
            icons = {"Add Book": "📝", "View Books": "📚",
                     "Issue Book": "📤", "Return Book": "📥",
                     "Borrow Details": "📋", "Delete Book": "🗑️"}

            ttk.Label(frame, text=icons[text],
                      font=('Helvetica', 32)).pack(pady=10)
            ttk.Label(frame, text=text,
                      font=('Helvetica', 12, 'bold')).pack(pady=5)
            ttk.Button(frame, text="Open",
                       command=command,
                       style='Modern.TButton').pack(pady=10)

        # Configure grid weights
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=1)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_book_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Add Book", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Title: ").pack(pady=5)
        title_entry = tk.Entry(self.root)
        title_entry.pack(pady=5)

        tk.Label(self.root, text="Author: ").pack(pady=5)
        author_entry = tk.Entry(self.root)
        author_entry.pack(pady=5)

        tk.Label(self.root, text="Genre: ").pack(pady=5)
        genre_entry = tk.Entry(self.root)
        genre_entry.pack(pady=5)

        def add_book_action():
            title = title_entry.get()
            author = author_entry.get()
            genre = genre_entry.get()
            add_book(title, author, genre)
            self.library_screen()

        tk.Button(self.root, text="Add Book", command=add_book_action).pack(pady=20)

        tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=5)

    def view_books(self):
        self.clear_screen()

        # Create header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        ttk.Label(header, text="Library Books",
                  font=('Helvetica', 16, 'bold'),
                  foreground=self.colors['black']).pack(side='left', padx=20)

        ttk.Button(header, text="Back",
                   command=self.library_screen,
                   style='Modern.TButton').pack(side='right', padx=20, pady=10)

        # Main content container
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Search and filter container
        filter_frame = tk.Frame(main_container, bg=self.colors['white'], padx=10, pady=10)
        filter_frame.pack(fill='x', pady=10)

        # Search box
        search_frame = tk.Frame(filter_frame, bg=self.colors['white'])
        search_frame.pack(side='left', padx=10)

        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side='left', padx=5)

        # Filter options
        filter_options_frame = tk.Frame(filter_frame, bg=self.colors['white'])
        filter_options_frame.pack(side='left', padx=10)

        ttk.Label(filter_options_frame, text="Filter by:").pack(side='left', padx=5)
        filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_options_frame, text="All", value="all",
                        variable=filter_var).pack(side='left', padx=5)
        ttk.Radiobutton(filter_options_frame, text="Available", value="available",
                        variable=filter_var).pack(side='left', padx=5)
        ttk.Radiobutton(filter_options_frame, text="Borrowed", value="borrowed",
                        variable=filter_var).pack(side='left', padx=5)

        # Sort options
        sort_frame = tk.Frame(filter_frame, bg=self.colors['white'])
        sort_frame.pack(side='right', padx=10)

        ttk.Label(sort_frame, text="Sort by:").pack(side='left', padx=5)
        sort_var = tk.StringVar(value="ID")
        sort_options = ttk.Combobox(sort_frame, textvariable=sort_var, width=10,
                                    values=["ID", "Title", "Author", "Genre"])
        sort_options.pack(side='left', padx=5)

        # Create Treeview for books
        tree_frame = tk.Frame(main_container, bg=self.colors['white'])
        tree_frame.pack(fill='both', expand=True, pady=10)

        # Create Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')

        tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Author", "Genre", "Status"),
                            show='headings', selectmode='browse',
                            yscrollcommand=tree_scroll.set)

        tree_scroll.config(command=tree.yview)

        # Configure column headings
        tree.heading("ID", text="ID", command=lambda: self.sort_treeview(tree, "ID", False))
        tree.heading("Title", text="Title", command=lambda: self.sort_treeview(tree, "Title", False))
        tree.heading("Author", text="Author", command=lambda: self.sort_treeview(tree, "Author", False))
        tree.heading("Genre", text="Genre", command=lambda: self.sort_treeview(tree, "Genre", False))
        tree.heading("Status", text="Status", command=lambda: self.sort_treeview(tree, "Status", False))

        # Configure column widths
        tree.column("ID", width=50)
        tree.column("Title", width=200)
        tree.column("Author", width=150)
        tree.column("Genre", width=100)
        tree.column("Status", width=100)

        tree.pack(fill='both', expand=True)

        # Statistics frame
        stats_frame = tk.Frame(main_container, bg=self.colors['white'], padx=10, pady=10)
        stats_frame.pack(fill='x', pady=10)

        self.stats_labels = {
            'total': ttk.Label(stats_frame, text="Total Books: 0"),
            'available': ttk.Label(stats_frame, text="Available: 0"),
            'borrowed': ttk.Label(stats_frame, text="Borrowed: 0")
        }

        for label in self.stats_labels.values():
            label.pack(side='left', padx=20)

        def update_display(*args):
            # Clear the treeview
            for item in tree.get_children():
                tree.delete(item)

            # Get books from database
            conn = sqlite3.connect("library.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            conn.close()

            # Filter and search books
            filtered_books = []
            search_text = search_entry.get().lower()
            filter_status = filter_var.get()

            for book in books:
                # Apply search filter
                if search_text and not any(search_text in str(field).lower() for field in book[1:4]):
                    continue

                # Apply status filter
                if filter_status == "available" and book[5] == 1:
                    continue
                if filter_status == "borrowed" and book[5] == 0:
                    continue

                filtered_books.append(book)

            # Sort books
            sort_column = sort_var.get().lower()
            column_indices = {"id": 0, "title": 1, "author": 2, "genre": 3}
            if sort_column in column_indices:
                # Special handling for ID column to sort numerically
                if sort_column == "id":
                    filtered_books.sort(key=lambda x: int(x[column_indices[sort_column]]))
                elif sort_column == "title":
                    filtered_books.sort(key=lambda x: x[column_indices[sort_column]].lower())
                elif sort_column == "author":
                    filtered_books.sort(key=lambda x: x[column_indices[sort_column]].lower())
                elif sort_column == "genre":
                    filtered_books.sort(key=lambda x: x[column_indices[sort_column]].lower())
                else:
                    filtered_books.sort(key=lambda x: x[column_indices[sort_column]])


            # Update treeview
            for book in filtered_books:
                status = "Borrowed" if book[5] == 1 else "Available"
                tree.insert("", "end", values=(book[0], book[1], book[2], book[3], status))

            # Update statistics
            total_books = len(books)
            borrowed_books = sum(1 for book in books if book[5] == 1)
            available_books = total_books - borrowed_books

            self.stats_labels['total'].config(text=f"Total Books: {total_books}")
            self.stats_labels['available'].config(text=f"Available: {available_books}")
            self.stats_labels['borrowed'].config(text=f"Borrowed: {borrowed_books}")


        # Bind update function to search and filter changes
        search_entry.bind('<KeyRelease>', update_display)
        filter_var.trace('w', update_display)
        sort_var.trace('w', update_display)

        # Initial display
        update_display()

    def sort_treeview(self, tree, col, reverse):
        """Sort treeview content when clicking on headers"""
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tree.move(k, "", index)

        # Reverse sort next time
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def show_books(self, book_list):
        self.clear_screen()

        tk.Label(self.root, text="Books in Library", font=("Arial", 16)).pack(pady=10)

        book_text = tk.Text(self.root, height=10, width=50)
        book_text.insert(tk.END, book_list)
        book_text.config(state=tk.DISABLED)
        book_text.pack(pady=5)

        tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=5)

    def issue_book_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Issue Book", font=("Arial", 16)).pack(pady=10)

        # Show available books first
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, genre FROM books WHERE borrowed = 0")
        available_books = cursor.fetchall()
        conn.close()

        if available_books:
            # Display available books in a scrollable frame
            tk.Label(self.root, text="Available Books:", font=("Arial", 12, "bold")).pack(pady=5)

            # Create a frame for the list and scrollbar
            list_frame = tk.Frame(self.root)
            list_frame.pack(pady=5, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            book_list = tk.Text(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
            book_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=book_list.yview)

            # Insert book details into the text widget
            book_list.insert(tk.END, "ID\tTitle\tAuthor\tGenre\n")
            book_list.insert(tk.END, "-" * 50 + "\n")
            for book in available_books:
                book_list.insert(tk.END, f"{book[0]}\t{book[1]}\t{book[2]}\t{book[3]}\n")
            book_list.config(state=tk.DISABLED)
        else:
            tk.Label(self.root, text="No books available for borrowing", fg="red").pack(pady=10)

        # Book ID input section
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Enter Book ID to Issue:").pack(side=tk.LEFT)
        book_id_entry = tk.Entry(input_frame, width=10)
        book_id_entry.pack(side=tk.LEFT, padx=5)

        def issue_book_action():
            book_id = book_id_entry.get()
            if not book_id.isdigit():
                messagebox.showerror("Error", "Please enter a valid numeric Book ID")
                return

            borrow_id = issue_book(book_id)
            if borrow_id:
                messagebox.showinfo("Success", f"Book issued successfully!\nBorrow ID: {borrow_id}")
                self.library_screen()
            else:
                messagebox.showerror("Error", "Invalid Book ID or Book already borrowed")

        tk.Button(self.root, text="Issue Book", command=issue_book_action).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=5)

    def borrow_details_screen(self):
        self.clear_screen()
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        # Get all borrowed books
        cursor.execute("SELECT id, title, author, genre, borrow_id FROM books WHERE borrowed = 1")
        borrowed_books = cursor.fetchall()
        conn.close()

        if not borrowed_books:
            messagebox.showinfo("Info", "No currently borrowed books")
            self.library_screen()
            return

        # Format the borrowed books information
        book_list = "\n\n".join(
            [f"Book ID: {book[0]}\nTitle: {book[1]}\nAuthor: {book[2]}\nGenre: {book[3]}\nBorrow ID: {book[4]}"
             for book in borrowed_books])

        # Display results
        tk.Label(self.root, text="Borrowed Books Details", font=("Arial", 16)).pack(pady=10)

        text_widget = tk.Text(self.root, height=12, width=50)
        text_widget.insert(tk.END, book_list)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(padx=10, pady=10)

        tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=10)

    def return_book_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Return Book", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Enter Borrow ID to Return: ").pack(pady=5)
        borrow_id_entry = tk.Entry(self.root)
        borrow_id_entry.pack(pady=5)

        def return_book_action():
            borrow_id = borrow_id_entry.get()
            if return_book(borrow_id):
                messagebox.showinfo("Success", "Book returned successfully!")
            else:
                messagebox.showerror("Error", "Book could not be returned. Please check the Borrow ID.")

        tk.Button(self.root, text="Return Book", command=return_book_action).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.library_screen).pack(pady=5)

    def delete_book_screen(self):
        self.clear_screen()

        # Create header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        ttk.Label(header, text="Delete Book",
                  font=('Helvetica', 16, 'bold'),
                  foreground=self.colors['black']).pack(side='left', padx=20)

        ttk.Button(header, text="Back",
                   command=self.library_screen,
                   style='Modern.TButton').pack(side='right', padx=20, pady=10)

        # Create main content area
        content = tk.Frame(self.root, bg=self.colors['background'])
        content.pack(fill='both', expand=True, padx=40, pady=20)

        # Show available books
        ttk.Label(content, text="Available Books",
                  style='Subtitle.TLabel').pack(pady=10)

        # Create a frame for the book list
        book_frame = tk.Frame(content, bg=self.colors['white'])
        book_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Create scrollable text widget for books
        book_list = tk.Text(book_frame, height=10, width=60,
                            font=('Helvetica', 10),
                            bg=self.colors['white'])
        scrollbar = ttk.Scrollbar(book_frame, orient="vertical",
                                  command=book_list.yview)
        book_list.configure(yscrollcommand=scrollbar.set)

        # Pack the text widget and scrollbar
        book_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Get books from database
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        conn.close()

        # Display books in the text widget
        if books:
            book_list.insert(tk.END, "ID\tTitle\tAuthor\tGenre\tStatus\n")
            book_list.insert(tk.END, "-" * 80 + "\n")
            for book in books:
                status = 'Borrowed' if book[5] == 1 else 'Available'
                book_list.insert(tk.END,
                                 f"{book[0]}\t{book[1]}\t{book[2]}\t{book[3]}\t{status}\n")
        else:
            book_list.insert(tk.END, "No books available in the library.")

        book_list.config(state='disabled')

        # Create delete section
        delete_frame = tk.Frame(content, bg=self.colors['background'])
        delete_frame.pack(pady=20)

        ttk.Label(delete_frame, text="Enter Book ID to Delete:").pack(side='left', padx=5)
        book_id_entry = ttk.Entry(delete_frame, width=10)
        book_id_entry.pack(side='left', padx=5)

        def confirm_delete():
            book_id = book_id_entry.get()

            if not book_id.strip():
                messagebox.showerror("Error", "Please enter a Book ID!")
                return

            if not book_id.isdigit():
                messagebox.showerror("Error", "Please enter a valid numeric Book ID!")
                return

            # Get book details for confirmation
            conn = sqlite3.connect("library.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            conn.close()

            if not book:
                messagebox.showerror("Error", "Book ID not found!")
                return

            if book[5] == 1:  # If book is borrowed
                messagebox.showerror("Error", "Cannot delete a borrowed book!")
                return

            # Create confirmation dialog
            confirm_window = tk.Toplevel(self.root)
            confirm_window.title("Confirm Delete")
            confirm_window.geometry("400x300")
            confirm_window.configure(bg=self.colors['background'])

            # Center the window
            confirm_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + 50,
                self.root.winfo_rooty() + 50))

            # Add book details
            ttk.Label(confirm_window,
                      text="Are you sure you want to delete this book?",
                      style='Subtitle.TLabel').pack(pady=10)

            details_frame = tk.Frame(confirm_window, bg=self.colors['white'],
                                     padx=20, pady=20, relief='raised', bd=1)
            details_frame.pack(padx=20, pady=10, fill='x')

            ttk.Label(details_frame, text="Book Details:",
                      font=('Helvetica', 12, 'bold')).pack(pady=5)
            ttk.Label(details_frame, text=f"ID: {book[0]}").pack()
            ttk.Label(details_frame, text=f"Title: {book[1]}").pack()
            ttk.Label(details_frame, text=f"Author: {book[2]}").pack()
            ttk.Label(details_frame, text=f"Genre: {book[3]}").pack()

            def perform_delete():
                conn = sqlite3.connect("library.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
                conn.commit()
                conn.close()

                confirm_window.destroy()
                messagebox.showinfo("Success", "Book deleted successfully!")
                self.delete_book_screen()  # Refresh the screen

            button_frame = tk.Frame(confirm_window, bg=self.colors['background'])
            button_frame.pack(pady=20)

            ttk.Button(button_frame, text="Confirm Delete",
                       command=perform_delete,
                       style='Modern.TButton').pack(side='left', padx=10)

            ttk.Button(button_frame, text="Cancel",
                       command=confirm_window.destroy,
                       style='Modern.TButton').pack(side='left', padx=10)

        ttk.Button(delete_frame, text="Delete Book",
                   command=confirm_delete,
                   style='Modern.TButton').pack(side='left', padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()