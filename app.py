from flask import Flask, render_template, request, redirect, url_for
import json
import logging
from jinja2.exceptions import TemplateNotFound
from html import escape

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_posts():
    """Load blog posts from posts.json or return default posts if file is missing."""
    try:
        with open('posts.json', 'r') as file:
            posts = json.load(file)
        # Validate posts structure
        if not isinstance(posts, list):
            raise ValueError("posts.json must contain a list")
        for post in posts:
            if not all(isinstance(post.get(key), str) for key in ['author', 'title', 'content']):
                raise ValueError("Invalid post data in posts.json")
            if not isinstance(post.get('id'), int):
                raise ValueError("Invalid post ID in posts.json")
            if not isinstance(post.get('likes'), int):
                raise ValueError("Invalid likes value in posts.json")
        return posts
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Failed to load posts: {str(e)}")
        return [
            {
                "id": 1,
                "author": "John Doe",
                "title": "First Post",
                "content": "This is my first post.",
                "likes": 0
            },
            {
                "id": 2,
                "author": "Jane Doe",
                "title": "Second Post",
                "content": "This is another post.",
                "likes": 0
            }
        ]


def save_posts(posts):
    """Save blog posts to posts.json."""
    try:
        with open('posts.json', 'w') as file:
            json.dump(posts, file, indent=4)
    except (IOError, PermissionError) as e:
        logging.error(f"Failed to save posts: {str(e)}")
        return False
    return True


def fetch_post_by_id(post_id):
    """Fetch a single post by its ID or return None if not found."""
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            return post
    return None


def validate_post_data(author, title, content):
    """Validate post data, ensuring non-empty and reasonable length."""
    max_lengths = {'author': 100, 'title': 200, 'content': 10000}
    if not all([author, title, content]):
        return False, "All fields are required."
    if any(len(field) > max_lengths[key] for field, key in [
        (author, 'author'), (title, 'title'), (content, 'content')
    ]):
        return False, "Input exceeds maximum length."
    return True, ""


@app.route('/')
def index():
    """Display the list of blog posts."""
    try:
        posts = load_posts()
        return render_template('index.html', posts=posts)
    except TemplateNotFound as e:
        logging.error(f"Template not found: {str(e)}")
        return render_template('error.html', message="Template not found", status=500)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Handle adding a new blog post."""
    if request.method == 'POST':
        # Get and sanitize form data
        author = escape(request.form.get('author', ''))
        title = escape(request.form.get('title', ''))
        content = escape(request.form.get('content', ''))

        # Validate inputs
        is_valid, error = validate_post_data(author, title, content)
        if not is_valid:
            return render_template('error.html', message=error, status=400)

        # Load existing posts
        posts = load_posts()

        # Generate unique ID (max ID + 1)
        new_id = max([post['id'] for post in posts], default=0) + 1

        # Create new post
        new_post = {
            "id": new_id,
            "author": author,
            "title": title,
            "content": content,
            "likes": 0
        }

        # Add new post and save to JSON
        posts.append(new_post)
        if not save_posts(posts):
            logging.error("Failed to save new post")
            return render_template('error.html', message="Failed to save post", status=500)

        return redirect(url_for('index'))

    try:
        return render_template('add.html')
    except TemplateNotFound as e:
        logging.error(f"Template not found: {str(e)}")
        return render_template('error.html', message="Template not found", status=500)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    """Delete a blog post by its ID."""
    # Check if post exists
    if fetch_post_by_id(post_id) is None:
        logging.error(f"Post not found: ID {post_id}")
        return render_template('error.html', message="Post not found", status=404)

    # Load existing posts
    posts = load_posts()

    # Remove post with matching ID
    posts = [post for post in posts if post['id'] != post_id]

    # Save updated posts
    if not save_posts(posts):
        logging.error("Failed to save posts after deletion")
        return render_template('error.html', message="Failed to save changes", status=500)

    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    """Handle updating an existing blog post."""
    # Fetch the post by ID
    post = fetch_post_by_id(post_id)
    if post is None:
        logging.error(f"Post not found: ID {post_id}")
        return render_template('error.html', message="Post not found", status=404)

    if request.method == 'POST':
        # Get and sanitize form data
        author = escape(request.form.get('author', ''))
        title = escape(request.form.get('title', ''))
        content = escape(request.form.get('content', ''))

        # Validate inputs
        is_valid, error = validate_post_data(author, title, content)
        if not is_valid:
            return render_template('error.html', message=error, status=400)

        # Load existing posts
        posts = load_posts()

        # Update the post
        for post in posts:
            if post['id'] == post_id:
                post['author'] = author
                post['title'] = title
                post['content'] = content
                break

        # Save updated posts
        if not save_posts(posts):
            logging.error("Failed to save updated post")
            return render_template('error.html', message="Failed to save changes", status=500)

        return redirect(url_for('index'))

    try:
        # Display the update form with current post data
        return render_template('update.html', post=post)
    except TemplateNotFound as e:
        logging.error(f"Template not found: {str(e)}")
        return render_template('error.html', message="Template not found", status=500)


@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    """Increment the likes count for a blog post by its ID."""
    # Check if post exists
    post = fetch_post_by_id(post_id)
    if post is None:
        logging.error(f"Post not found: ID {post_id}")
        return render_template('error.html', message="Post not found", status=404)

    # Load existing posts
    posts = load_posts()

    # Increment likes for the post
    for post in posts:
        if post['id'] == post_id:
            post['likes'] = post.get('likes', 0) + 1
            break

    # Save updated posts
    if not save_posts(posts):
        logging.error("Failed to save posts after liking")
        return render_template('error.html', message="Failed to save changes", status=500)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)