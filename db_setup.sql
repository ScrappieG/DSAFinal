CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS links (
    source_id INTEGER,
    target_id INTEGER,
    PRIMARY KEY (source_id, target_id),
    FOREIGN KEY (source_id) REFERENCES pages(id),
    FOREIGN KEY (target_id) REFERENCES pages(id)
);
