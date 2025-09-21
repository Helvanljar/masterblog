from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)


def load_posts():
    """Load blog posts from posts.json or return default posts if file is missing."""
    try:
        with open('posts.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default posts if file doesn't exist or is invalid
        return [
            {
                "id": 1,
                "author": "John Doe",
                "title": "First Post",
                "content": "This is my first post."
            },
            {
                "id": 2,
                "author": "Jane Doe",
                "title": "Second Post",
                "content": "This is another post."
            }
        ]


def save_posts(posts):
    """Save blog posts to posts.json."""
    try:
        with open('posts.json', 'w') as file:
            json.dump(posts, file, indent=4)
    except (IOError, PermissionError):
        # Log error or handle gracefully (for now, return False to indicate failure)
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
    posts = load_posts()
    return render_template('index.html', posts=posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Handle adding a new blog post."""
    if request.method == 'POST':
        # Get form data
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')

        # Validate inputs
        is_valid, error = validate_post_data(author, title, content)
        if not is_valid:
            return error, 400

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
        if not save_posts(posts):
            return "Failed to save post", 500

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:post_id>')
def delete(post_id):
    """Delete a blog post by its ID."""
    # Check if post exists
    if fetch_post_by_id(post_id) is None:
        return "Post not found", 404

    # Load existing posts
    posts = load_posts()

    # Remove post with matching ID
    posts = [post for post in posts if post['id'] != post_id]

    # Save updated posts
    if not save_posts(posts):
        return "Failed to save changes", 500

    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    """Handle updating an existing blog post."""
    # Fetch the post by ID
    post = fetch_post_by_id(post_id)
    if post is None:
        return "Post not found", 404

    if request.method == 'POST':
        # Get form data
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')

        # Validate inputs
        is_valid, error = validate_post_data(author, title, content)
        if not is_valid:
            return error, 400

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
            return "Failed to save changes", 500

        return redirect(url_for('index'))

    # Display the update form with current post data
    return render_template('update.html', post=post)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)