from flask import Flask, render_template
import json

app = Flask(__name__)

# Function to load blog posts from JSON file
def load_posts():
    try:
        with open('posts.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return default posts if file doesn't exist
        return [
            {"id": 1, "author": "John Doe", "title": "First Post", "content": "This is my first post."},
            {"id": 2, "author": "Jane Doe", "title": "Second Post", "content": "This is another post."}
        ]

@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)