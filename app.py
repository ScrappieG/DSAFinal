import time
from flask import Flask, render_template, request
from wikipedia_pathfinder import WikipediaPathfinder

app = Flask(__name__)

pathfinder = WikipediaPathfinder()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_path', methods=['POST'])
def find_path():
    print("find_path triggered")

    # fetch wiki pages from user
    start = request.form.get('start').strip()
    end = request.form.get('end').strip()
    algorithm = request.form.get('algorithm')  # grab the selected algo

    print(f"Start: {start}, End: {end}, Algorithm: {algorithm}")

    start_time = time.time()
    max_duration = 600

    path, visited = None, set()

    try:
        # user selection
        if algorithm == "bfs":
            print("Running BFS...")
            path, visited = pathfinder.bfs(start, end)
        elif algorithm == "dijkstra":
            print("Running Dijkstra's Algorithm...")
            path, visited = pathfinder.dijkstra(start, end)

        # render the results
        if path:
            return render_template('results.html', path=path, checked_links=list(visited))
        else:
            return render_template(
                'results.html',
                path=None,
                checked_links=list(visited),
                error="No path found or process timed out."
            )

    except Exception as e:
        print(f"Error during pathfinding: {e}")
        return render_template(
            'results.html',
            path=None,
            checked_links=list(visited),
            error=f"An error occurred: {e}"
        )


if __name__ == '__main__':
    app.run(debug=True)
