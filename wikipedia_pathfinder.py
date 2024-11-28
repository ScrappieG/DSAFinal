from collections import deque
import requests
from sqlite_handler import SQLiteHandler


class WikipediaPathfinder:
    def __init__(self, db_path="wikipedia_links.db", schema_file="db_setup.sql"):
        """
        initialize the WikipediaPathfinder with a database handler
        """
        self.db_handler = SQLiteHandler(db_path=db_path, schema_file=schema_file)

    def addVertice(self, title):
        """
        adds a vertex database if it doesn't already exist
        returns the unique id for the vertex
        """
        return self.db_handler.get_page_id(title)

    def insertEdge(self, source_id, target_id):
        """
        adds a directed edge between two pages in the database
        """
        self.db_handler.insert_link(source_id, target_id)

    def fetch_last_revision(self, page_title):
        """
        fetches the last revision date of a wikipedia page using the mediawiki API
        """
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": page_title,
            "rvslots": "*",
            "rvprop": "timestamp",
            "format": "json"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                revisions = page_data.get("revisions", [])
                if revisions:
                    return revisions[0]["timestamp"]
        except requests.RequestException as e:
            print(f"Error fetching revision for page '{page_title}': {e}")
        return None

    def fetch_links_from_api(self, page_title):
        """
        fetches links from the Wikipedia API for a given page title and updates the database
        """
        print(f"Fetching links for: {page_title}")
        page_id = self.addVertice(page_title)

        params = {
            "action": "query",
            "titles": page_title,
            "prop": "links",
            "plnamespace": "0",  # only include main namespace links
            "pllimit": "max",    # maximum number of links grabbed
            "format": "json",
            "redirects": 1,
        }

        links = []
        while True:
            try:
                response = requests.get("https://en.wikipedia.org/w/api.php", params=params, timeout=10).json()
                pages = response.get("query", {}).get("pages", {})
                for _, page_data in pages.items():
                    if "links" in page_data:
                        for link in page_data["links"]:
                            links.append(link["title"])

                if "continue" in response:
                    params.update(response["continue"])
                else:
                    break
            except requests.RequestException as e:
                print(f"Error fetching links for '{page_title}': {e}")
                break

        return links

    def load_links_for_db(self, page_title):
        """
        fetches links and the last time it was revised from a wiki page
        """
        last_stored_revision = self.db_handler.get_last_revision(page_title)
        current_revision = self._fetch_last_revision(page_title)

        if last_stored_revision == current_revision:
            print(f"page '{page_title}' is up-to-date (revision: {current_revision}).")
            return

        print(f"fetching links for '{page_title}' (New Revision: {current_revision}).")
        links = self.fetch_links_from_api(page_title)
        source_id = self.db_handler.add_or_update_page(page_title, current_revision)

        for target_title in links:
            target_id = self.addVertice(target_title)
            self.insertEdge(source_id, target_id)

    def load_links_recursively(self, page_title, depth=2):
        """
        recursively loads links from a wikipedia page, if revision is up to date it skips it
        """
        if depth == 0:
            print(f"Skipping page '{page_title}' (depth={depth}).")
            return

        print(f"Loading links for: {page_title} (depth={depth})")
        self.load_links_with_revision(page_title)

        source_id = self.db_handler.get_page_id_by_title(page_title)
        if not source_id:
            print(f"page '{page_title}' not found in the database: skipping recursion.")
            return

        neighbors = self.db_handler.get_neighbors(source_id)
        for neighbor_id in neighbors:
            neighbor_title = self.db_handler.get_page_title_by_id(neighbor_id)
            self.load_links_recursively(neighbor_title, depth - 1)

    def bfs(self, start_title, target_title):
        """
        performs a BFS to find any path between start_title and target_title
        """
        start_id = self.db_handler.get_page_id_by_title(start_title)
        target_id = self.db_handler.get_page_id_by_title(target_title)

        if start_id is None or target_id is None:
            print(f"start or target page not found in the database.")
            return None, set()

        queue = deque([(start_id, [start_id])])
        visited = set()

        while queue:
            current_id, path = queue.popleft()

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == target_id:
                return [self.db_handler.get_page_title_by_id(pid) for pid in path], visited

            for neighbor_id in self.db_handler.get_neighbors(current_id):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        print(f"no path found between '{start_title}' and '{target_title}'.")
        return None, visited
