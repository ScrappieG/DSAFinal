# Quick Start

1) CD into the directory of the project 
<br>
2) Install dependencies: pip install -r requirements.txt
<br>
3) python app.py (will run the website locally)
<br>
# About the repository

This project uses flask, thus we maintain the flask file system. <br>
  - static (stores static files such as images) <br>
  - templates (stores html templates)<br>
  - app.py (where the backend comes together)<br>
  - requirements.txt (stores a list of the dependencies)
Other files
  - sqlite_handler - handles out sql db
  - wikipedia_pathfinder.py - handles the api fetching along with traversals
  - wikipedia_links.db - this is our database
  - db_setup.sql - if the database isn't setup, the contents of this file is executed as a sql query