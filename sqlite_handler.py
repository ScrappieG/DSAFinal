import sqlite3


class SQLiteHandler:
    def __init__(self, db_path="wikipedia_links.db", schema_file="db_setup.sql"):
        self.db_path = db_path
        self.schema_file = schema_file
        self.setup_database()
        self.conn = sqlite3.connect(self.db_path)

    def database_connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def database_close(self):
        self.conn.close()

    def setup_database(self):
        self.database_connect()
        try:
            with open(self.schema_file, 'r') as file:
                schema = file.read()
            self.cursor.executescript(schema)
            self.conn.commit()
            print("Database schema initialized successfully.")
        except Exception as e:
            print(f"Error initializing database schema: {e}")
        finally:
            self.database_close()

    def get_page_id(self, title):
        self.database_connect()
        title = title.strip().lower()
        try:
            self.cursor.execute("SELECT id FROM pages WHERE title = ?", (title,))
            result = self.cursor.fetchone()
            if result:
                return result["id"]
            else:
                self.cursor.execute("INSERT INTO pages (title) VALUES (?)", (title,))
                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error in get_page_id: {e}")
            return None
        finally:
            self.database_close()

    def insert_link(self, source_id, target_id):
        self.database_connect()
        try:
            self.cursor.execute("INSERT OR IGNORE INTO links (source_id, target_id) VALUES (?, ?)", (source_id, target_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error in insert_link: {e}")
        finally:
            self.database_close()

    def add_or_update_page(self, title):
        self.database_connect()
        try:
            title = title.strip().lower()
            # Check if the page already exists
            self.cursor.execute("SELECT id FROM pages WHERE title = ?", (title,))
            result = self.cursor.fetchone()
            if result:
                return result["id"]  # Return the existing ID
            else:
                # Insert the new page
                self.cursor.execute("INSERT INTO pages (title) VALUES (?)", (title,))
                self.conn.commit()
                return self.cursor.lastrowid  # Return the new ID
        except sqlite3.Error as e:
            print(f"Error in add_or_update_page: {e}")
            return None
        finally:
            self.database_close()

    def get_neighbors(self, page_id):
        self.database_connect()
        try:
            self.cursor.execute("SELECT target_id FROM links WHERE source_id = ?", (page_id,))
            return [row["target_id"] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_neighbors: {e}")
            return []
        finally:
            self.database_close()

    def get_page_title_by_id(self, page_id):
        self.database_connect()
        try:
            self.cursor.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
            result = self.cursor.fetchone()
            return result["title"] if result else None
        except sqlite3.Error as e:
            print(f"Error in get_page_title_by_id: {e}")
            return None
        finally:
            self.database_close()

    def get_page_id_by_title(self, title):
        self.database_connect()
        title = title.strip().lower()
        try:
            self.cursor.execute("SELECT id FROM pages WHERE title = ?", (title,))
            result = self.cursor.fetchone()
            return result["id"] if result else None
        except sqlite3.Error as e:
            print(f"Error in get_page_id_by_title: {e}")
            return None
        finally:
            self.database_close()
