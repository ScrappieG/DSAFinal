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

    start = request.form.get('start').strip()
    end = request.form.get('end').strip()

    print(f"Start: {start}, End: {end}")

    start_time = time.time()
    max_duration = 600

    # Perform BFS to find any path
    path, visited = pathfinder.bfs(start, end)
    if path:
        return render_template('results.html', path=path, checked_links=list(visited))
    else:
        return render_template(
            'results.html',
            path=None,
            checked_links=list(visited),
            error="No path found or process timed out."
        )


if __name__ == '__main__':
    app.run(debug=True)
