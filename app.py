import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_FILE = 'forum.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Επιτρέπει την πρόσβαση σε στήλες με το όνομά τους (π.χ. post['title'])
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    conn.commit()
    conn.close()


init_db()

@app.route('/')
def index():
    """Η αρχική σελίδα που δείχνει τη φόρμα δημιουργίας και όλες τις ερωτήσεις."""
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    username = request.form.get('username') or 'Ανώνυμος'  # Αν είναι κενό, βάζει "Ανώνυμος"
    
    if title and content:
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content, username) VALUES (?, ?, ?)',
                     (title, content, username))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    """Προβάλλει μια συγκεκριμένη ερώτηση και τα σχόλιά της. Χειρίζεται και την υποβολή νέου σχολίου."""
    conn = get_db_connection()
    
    
    if request.method == 'POST':
        content = request.form.get('content')
        username = request.form.get('username') or 'Ανώνυμος'
        if content:
            conn.execute('INSERT INTO comments (post_id, content, username) VALUES (?, ?, ?)',
                         (post_id, content, username))
            conn.commit()
            
    
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC', (post_id,)).fetchall()
    conn.close()
    
    if post is None:
        return "Η ερώτηση δεν βρέθηκε", 404
        
    return render_template('post.html', post=post, comments=comments)

if __name__ == '__main__':
    # Χρήσιμο για τοπικές δοκιμές, στο Render θα παρακαμφθεί από το gunicorn
    app.run(host='0.0.0.0', port=10000)
