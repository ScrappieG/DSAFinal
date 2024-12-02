from collections import deque
import requests
from sqlite_handler import SQLiteHandler
import heapq


class WikipediaPathfinder:
    def __init__(self, db_path="wikipedia_links.db", schema_file="db_setup.sql"):
        """
        initialize the WikipediaPathfinder with a database handler
        """
        self.db_handler = SQLiteHandler(db_path=db_path, schema_file=schema_file)

    def addVertice(self, title):
        """
        adds a vertex to the database if it doesn't already exist
        """
        return self.db_handler.get_page_id(title)

    def insertEdge(self, source_id, target_id):
        """
        adds a directed edge between two pages in the database
        """
        self.db_handler.insert_link(source_id, target_id)

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
            "plnamespace": "0",  # Only include main namespace links
            "pllimit": "max",    # Maximum number of links grabbed
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

        # Insert fetched links into the database
        for target_title in links:
            target_id = self.addVertice(target_title)
            self.insertEdge(page_id, target_id)

        return links

    def load_links_for_page(self, page_title):
        """
        Loads links for a page. If the links are not already in the database, fetches them from the API.
        """
        page_id = self.db_handler.get_page_id(page_title)
        neighbors = self.db_handler.get_neighbors(page_id)

        if not neighbors:
            print(f"Links for page '{page_title}' not found in the database. Fetching from API...")
            self.fetch_links_from_api(page_title)
        else:
            print(f"Links for page '{page_title}' already exist in the database.")

    def bfs(self, start_title, target_title):
        """
        performs BFS traversal to find any path between start_title and target_title
        """
        start_id = self.db_handler.get_page_id(start_title)
        target_id = self.db_handler.get_page_id(target_title)

        if start_id is None:
            print(f"Start page '{start_title}' not found in the database. Fetching...")
            self.fetch_links_from_api(start_title)
            start_id = self.db_handler.get_page_id(start_title)

        if target_id is None:
            print(f"Target page '{target_title}' not found in the database. Fetching...")
            self.fetch_links_from_api(target_title)
            target_id = self.db_handler.get_page_id(target_title)

        queue = deque([(start_id, [start_id])])
        visited = set()

        while queue:
            current_id, path = queue.popleft()

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == target_id:
                return [self.db_handler.get_page_title_by_id(pid) for pid in path], visited

            neighbors = self.db_handler.get_neighbors(current_id)
            if not neighbors:
                print(f"No neighbors found for page ID {current_id}. Fetching links...")
                self.fetch_links_from_api(self.db_handler.get_page_title_by_id(current_id))
                neighbors = self.db_handler.get_neighbors(current_id)

            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        print(f"No path found between '{start_title}' and '{target_title}'.")
        return None, visited

    def dijkstra(self, start_title, target_title):
        """
        performs Dijkstras algorithm to find the shortest path between two pages
        """
        start_id = self.db_handler.get_page_id(start_title)
        target_id = self.db_handler.get_page_id(target_title)

        if start_id is None:
            print(f"Start page '{start_title}' not found in the database. Fetching...")
            self.fetch_links_from_api(start_title)
            start_id = self.db_handler.get_page_id(start_title)

        if target_id is None:
            print(f"Target page '{target_title}' not found in the database. Fetching...")
            self.fetch_links_from_api(target_title)
            target_id = self.db_handler.get_page_id(target_title)

        priority_queue = [(0, start_id, [start_id])]
        visited = set()
        shortest_distances = {start_id: 0}

        while priority_queue:
            current_cost, current_id, path = heapq.heappop(priority_queue)

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == target_id:
                return [self.db_handler.get_page_title_by_id(pid) for pid in path], visited

            neighbors = self.db_handler.get_neighbors(current_id)
            if not neighbors:
                print(f"No neighbors found for page ID {current_id}. Fetching links...")
                self.fetch_links_from_api(self.db_handler.get_page_title_by_id(current_id))
                neighbors = self.db_handler.get_neighbors(current_id)

            for neighbor_id in neighbors:
                if neighbor_id in visited:
                    continue
                new_cost = current_cost + 1
                if neighbor_id not in shortest_distances or new_cost < shortest_distances[neighbor_id]:
                    shortest_distances[neighbor_id] = new_cost
                    heapq.heappush(priority_queue, (new_cost, neighbor_id, path + [neighbor_id]))

        print(f"No path found between '{start_title}' and '{target_title}'.")
        return None, visited
