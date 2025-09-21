from flask import Flask, render_template, request, redirect, url_for
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


# Function to save blog posts to JSON file
def save_posts(posts):
    with open('posts.json', 'w') as file:
        json.dump(posts, file, indent=4)


@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Get form data
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')

        # Load existing posts
        posts = load_posts()

        # Generate unique ID (max ID + 1)
        new_id = max([post['id'] for post in posts], default=0) + 1

        # Create new post
        new_post = {
            "id": new_id,
            "author": author,
            "title": title,
            "content": content
        }

        # Add new post and save to JSON
        posts.append(new_post)
        save_posts(posts)

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:post_id>')
def delete(post_id):
    # Load existing posts
    posts = load_posts()

    # Remove post with matching ID
    posts = [post for post in posts if post['id'] != post_id]

    # Save updated posts
    save_posts(posts)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)