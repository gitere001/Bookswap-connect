from flask import Flask, render_template, request, jsonify, redirect, flash
from flask import current_app
from flask import session
from models import storage
from models.user import User
from models.book import Book
from models.swap_request import SwapRequest
from sqlalchemy.exc import IntegrityError
from utils.text_utils import normalize_text
from fuzzywuzzy import fuzz
from utils.file_utils import allowed_file
import requests
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.secret_key = '4769bd47b01107b11132b278b09cb4b61d710edc6fc19aa2'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


@app.route('/', strict_slashes=False)
def landing_page():
    return (render_template('landing_page.html'))


@app.route('/login', strict_slashes=False, methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = storage.find(User, User.email == email)
        if users:
            user = users[0]
            if user and user.password == password:
                session['user_id'] = user.id
                session['email'] = user.email
                flash('login successful', 'success')
                return redirect('/home')
            else:
                flash('Invalid email or password', 'error')
                return redirect('/login')
        else:
            flash('Invalid email or password', 'error')
            return redirect('/login')
    return (render_template('login.html'))


@app.route('/logout', strict_slashes=False)
def logout():
    session.clear()
    return redirect('/login')


@app.route('/signup', strict_slashes=False)
def sign_up_page():
    return (render_template('sign_up.html'))


@app.route('/home', strict_slashes=False, methods=['GET'])
def home_page():
    if 'user_id' not in session:
        flash('You need to login first', 'error')
        return redirect('/login')
    return (render_template('home_page.html'))


@app.route('/check_email', strict_slashes=False, methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email', None)

    if not email:
        return jsonify({'error': 'Email not provided'}), 400
    user = storage.find(User, User.email == email)

    if user:
        return jsonify({'exists': True}), 200
    else:
        return jsonify({'exists': False}), 200


@app.route('/sign_up', strict_slashes=False, methods=['POST'])
def signup():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['confirm_password']

    if password != password2:
        flash('password didnt match', 'error')
        return redirect('/signup')

    if storage.find(User, User.email == email):
        flash('Email already exists', 'error')
        return redirect('/signup')

    user = User(first_name=first_name, last_name=last_name, email=email,
                password=password)
    try:
        storage.new(user)
        storage.save()
        flash('Successfully signed up! please login', 'success')
        return redirect('/login')
    except IntegrityError:
        storage.rollback()
        flash('An error occured. please try again', 'error')
        return redirect('/signup')


@app.route('/home/add_book/', strict_slashes=False, methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        condition = request.form['condition']
        description = request.form['description']
        user_id = session['user_id']

        normalized_title = normalize_text(title)
        normalized_author = normalize_text(author)

        user_books = storage.find(Book, Book.user_id == user_id)

        for book in user_books:
            if (fuzz.ratio(normalize_text(book.title), normalized_title) > 90
                    and normalize_text(book.author) == normalized_author):
                return jsonify({'message': f'You have already added a similar '
                                f'book: "{book.title}"', 'success':
                                    False}), 400

        cover = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                cover = upload_file(file)
                if cover is None:
                    return jsonify({'message': 'Invalid file type. Please '
                                    'upload an image file (png, jpg,'
                                    'jpeg, gif).', 'success': False}), 400
            else:
                return jsonify({'message': 'No file part or invalid file type.'
                                ' Please upload an image file'
                                ' (png, jpg, jpeg, gif).', 'success':
                                    False}), 400

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            condition=condition,
            description=description,
            user_id=user_id,
            cover=cover,
        )
        try:
            storage.new(new_book)
            storage.save()
            return jsonify({'message': 'Successfully added a book',
                            'success': True}), 200
        except IntegrityError:
            storage.rollback()
            return jsonify({'message': 'An error occurred while adding the'
                            ' book', 'success': False}), 500

    return render_template('add_book.html')


@app.route('/search', strict_slashes=False, methods=['GET'])
def search_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify([]), 200
    user_id = session['user_id']

    normalized_query = normalize_text(query)
    books_by_title = storage.find(Book, Book.title.ilike
                                  (f'%{normalized_query}%'))
    books_by_author = storage.find(Book, Book.author.ilike
                                   (f'%{normalized_query}%'))

    all_books = {book.id: book for book in books_by_title + books_by_author}
    filtered_books = [book for book in all_books.values() if book.user_id !=
                      user_id]

    books_list = [
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'condition': book.condition,
            'description': book.description,
            'cover': book.cover,
        }
        for book in filtered_books
    ]
    return jsonify(books_list), 200


@app.route('/book/<book_id>', strict_slashes=False, methods=['GET'])
def get_book_details(book_id):
    book = storage.get(Book, book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    book_details = {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre if book.genre else '',
        'condition': book.condition,
        'description': book.description if book.description else '',
    }
    return jsonify(book_details), 200


@app.route('/recommended_books', strict_slashes=False, methods=['GET'])
def recommended_books():
    if 'user_id' not in session:
        return jsonify('Error: user must be logged in'), 401
    user_id = session['user_id']
    all_books = storage.find(Book)
    filtered_books = [book for book in all_books if book.user_id != user_id]
    random_books = random.sample(filtered_books, min(len(filtered_books), 3))

    random_list = []
    for book in random_books:
        book_details = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre if book.genre else '',
            'condition': book.condition,
            'description': book.description if book.description else '',
            'cover': book.cover if book.cover else '',
            }
        random_list.append(book_details)
    return jsonify(random_list)


@app.route('/home/available_books', strict_slashes=False, methods=['GET'])
def available_books():
    return render_template('available_books.html')


@app.route('/fetch_all_books', strict_slashes=False, methods=['GET'])
def fetch_all_books():
    user_id = session['user_id']
    all_books = storage.find(Book)
    filtered_books = [book for book in all_books if book.user_id != user_id]
    all_books_list = []
    for book in filtered_books:
        books_details = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre if book.genre else '',
            'condition': book.condition,
            'description': book.description if book.description else '',
            }
        all_books_list.append(books_details)
    return jsonify(all_books_list)


@app.route('/searc/suggestions', strict_slashes=False, methods=['GET'])
def search_suggestion():
    query = request.args.get('query', '')
    if not query:
        return jsonify([]), 200
    normalized_query = normalize_text(query)

    all_books = storage.find(Book)
    suggestions = []
    for book in all_books:
        title_score = fuzz.ratio(normalize_text(book.title), normalized_query)
        author_score = fuzz.ratio(normalize_text(book.author),
                                  normalized_query)

        if title_score > 70 or author_score > 70:
            suggestions.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'condition': book.condition,
                'description': book.description,
                'cover': book.cover,
                'score': max(title_score, author_score)
            })
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(suggestions), 200


@app.route('/home/request_swap', strict_slashes=False)
def render_swap_request():
    return render_template('request_swap.html')


@app.route('/submit_swap_request', strict_slashes=False, methods=['POST'])
def submit_swap_request():
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to submit a swap request'}), 401

    user_id = session['user_id']
    data = request.get_json()

    requested_book_id = data.get('requested_book_id')
    offered_book_id = data.get('offered_book_id')
    message = data.get('message', '')

    existing_requests = storage.find(SwapRequest,
                                     SwapRequest.requester_id == user_id,
                                     SwapRequest.requested_book_id ==
                                     requested_book_id,
                                     SwapRequest.status == 'pending')

    if existing_requests:
        return jsonify({'message': 'You already have a pending swap request '
                        'for this book', 'success': False}), 400

    swap_request = SwapRequest(
        requester_id=user_id,
        requested_book_id=requested_book_id,
        offered_book_id=offered_book_id,
        message=message,
        status='pending',
    )
    try:
        storage.new(swap_request)
        storage.save()
        return jsonify({'message': 'Swap request submitted successfully', 'success': True}), 201
    except IntegrityError:
        storage.rollback()
        return jsonify({'message': 'An error occurred while sending'
                        ' your swap request', 'success': False}), 500


@app.route('/user_books', strict_slashes=False)
def get_users_books():
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to view '
                        'their books'}), 401

    user_id = session['user_id']
    all_books = storage.find(Book)
    users_books = [book for book in all_books if book.user_id == user_id]

    users_book_list = []
    for book in users_books:
        book_details = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'condition': book.condition,
            'description': book.description,
            'cover': book.cover,
        }
        users_book_list.append(book_details)

    return jsonify(users_book_list), 200


@app.route('/home/swap_requests', strict_slashes=False)
def render_swap_history():
    return render_template('/swap_history.html')


@app.route('/swap_records', methods=['GET'])
def get_swap_records():
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to view their swap '
                        'records'}), 401
    user_id = session['user_id']
    filtered_swaps = storage.find(SwapRequest, SwapRequest.requester_id == user_id)
    swap_requests_list = []
    for swap in filtered_swaps:
        offered_book = storage.get(Book, swap.offered_book_id)
        requested_book = storage.get(Book, swap.requested_book_id)
        swap_details = {
            'id': swap.id,
            'requester_id': swap.requester_id,
            'requested_book_id': swap.requested_book_id,
            'offered_book_id': swap.offered_book_id,
            'status': swap.status,
            'message': swap.message,
            'created_at': swap.created_at,
            'requested_book_title': requested_book.title if requested_book else 'Book not found',
            'offered_book_title': offered_book.title if offered_book else 'Book not found',
        }
        swap_requests_list.append(swap_details)
    return jsonify(swap_requests_list), 200


@app.route('/cancel_swap_request/<request_id>', methods=['DELETE'])
def cancel_swap_request(request_id):
    if 'user_id' not in session:
        return jsonify({'error': 'user must be logged in'}), 401

    swap_request = storage.get(SwapRequest, request_id)

    if not swap_request:
        return jsonify({'error': 'swap request not found'}), 404

    if swap_request.requester_id != session['user_id']:
        return jsonify({'error': 'you are not authorised to cancel this swap request'}), 403

    storage.delete(swap_request)
    storage.save()

    return jsonify({'message': 'swap request cancelled successfully'}), 200


if __name__ == "__main__":
    storage.reload()
    app.run(debug=True, port=5002)
