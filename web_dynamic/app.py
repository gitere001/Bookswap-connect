from flask import Flask, render_template, request, jsonify, redirect, flash
from flask import current_app, url_for
from flask import session
from models import storage
from models.user import User
from models.book import Book
from models.message import Message
from models.swap_request import SwapRequest
from sqlalchemy.exc import IntegrityError
from utils.text_utils import normalize_text
from fuzzywuzzy import fuzz
from utils.file_utils import allowed_file
import requests
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

app = Flask(__name__)
app.secret_key = '4769bd47b01107b11132b278b09cb4b61d710edc6fc19aa2'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def upload_file(file):
    """
    Uploads a file if it is an allowed file type.

    Args:
        file (werkzeug.datastructures.FileStorage): The file to be uploaded.

    Returns:
        str: The file path if the upload is successful, None otherwise.
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


@app.route('/', strict_slashes=False)
def landing_page():
    """
    Renders the landing page.

    Returns:
        Response: The landing page HTML.
    """
    return (render_template('landing_page.html'))


@app.route('/login', strict_slashes=False, methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    Returns:
        Response: The login page HTML on GET, or a redirect to the home page on POST.
    """
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
    """
    Logs out the current user by clearing the session.

    Returns:
        Response: Redirect to the login page.
    """
    session.clear()
    return redirect('/login')


@app.route('/signup', strict_slashes=False)
def sign_up_page():
    """
    Renders the sign-up page.

    Returns:
        Response: The sign-up page HTML.
    """
    return (render_template('sign_up.html'))


@app.route('/home', strict_slashes=False, methods=['GET'])
def home_page():
    """
    Renders the home page for logged-in users.

    Returns:
        Response: The home page HTML if the user is logged in, otherwise redirect to login page.
    """
    if 'user_id' not in session:
        flash('You need to login first', 'error')
        return redirect('/login')
    return (render_template('home_page.html'))


@app.route('/check_email', strict_slashes=False, methods=['POST'])
def check_email():
    """
    Checks if an email is already registered.

    Returns:
        Response: JSON indicating whether the email exists.
    """
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
    """
    Handles user sign-up.

    Returns:
        Response: Redirect to login page on success, otherwise redirect to sign-up page with error messages.
    """
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


@app.route('/home/add_book', strict_slashes=False, methods=['GET', 'POST'])
def add_book():
    """
    Adds a book to the user's collection.

    Returns:
        Response: The add book page HTML on GET, JSON response on POST.
    """
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        condition = request.form['condition']
        description = request.form['description']
        location = request.form['location']
        user_id = session['user_id']

        normalized_title = normalize_text(title)
        normalized_author = normalize_text(author)

        user_books = storage.find(Book, Book.user_id == user_id)
        for book in user_books:
            if (fuzz.ratio(normalize_text(book.title), normalized_title) > 90
                    and normalize_text(book.author) == normalized_author):
                return jsonify({
                    'message': f'You have already added '
                    f'a similar book: "{book.title}"',
                    'success': False
                }), 400

        cover = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                cover = upload_file(file)
                if cover is None:
                    return jsonify({
                        'message': 'Invalid file type. Please upload'
                        ' an image file (png, jpg, jpeg, gif).',
                        'success': False
                    }), 400

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            condition=condition,
            description=description,
            user_id=user_id,
            cover=cover,
            location=location,
            swapped=False,
        )

        try:

            storage.new(new_book)
            storage.save()
            return jsonify({
                'message': 'Successfully added a book',
                'success': True
            }), 200
        except IntegrityError:
            storage.rollback()
            return jsonify({
                'message': 'An error occurred while adding the book',
                'success': False
            }), 500

    return render_template('add_book.html')


@app.route('/search', strict_slashes=False, methods=['GET'])
def search_books():
    """
    Searches for books by title or author.

    Returns:
        Response: JSON list of books matching the query.
    """
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
            'location': book.location,
        }
        for book in filtered_books
    ]
    return jsonify(books_list), 200


@app.route('/book/<book_id>', strict_slashes=False, methods=['GET'])
def get_book_details(book_id):
    """
    Gets details of a specific book.

    Args:
        book_id (str): The ID of the book.

    Returns:
        Response: JSON details of the book.
    """
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
        'location': book.location,
    }
    return jsonify(book_details), 200


@app.route('/recommended_books', strict_slashes=False, methods=['GET'])
def recommended_books():
    """
    Gets a list of recommended books for the logged-in user.

    Returns:
        Response: JSON list of recommended books.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in '
                        'to view recommended books'}), 401

    user_id = session['user_id']
    all_books = storage.find(Book)
    filtered_books = [book for book in all_books if book.user_id != user_id]

    # Ensure that there are enough books to sample from
    if len(filtered_books) < 3:
        random_books = filtered_books
    else:
        random_books = random.sample(filtered_books, 3)

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
    """
    renders the html for all available books for swap in the platform
    """
    return render_template('available_books.html')


@app.route('/fetch_all_books', strict_slashes=False, methods=['GET'])
def fetch_all_books():
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged '
                        'in to view all books'}), 401

    user_id = session['user_id']
    all_books = storage.find(Book)
    filtered_books = [book for book in all_books if book.user_id != user_id]

    all_books_list = []
    for book in filtered_books:
        book_details = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre if book.genre else '',
            'condition': book.condition,
            'description': book.description if book.description else '',
        }
        all_books_list.append(book_details)

    return jsonify(all_books_list)


@app.route('/searc/suggestions', strict_slashes=False, methods=['GET'])
def search_suggestion():
    """
    enhance user experience by suggesting books based on their search query
    """
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
    """
    render the page where the user can initiate swap
    """
    return render_template('request_swap.html')


@app.route('/submit_swap_request', strict_slashes=False, methods=['POST'])
def submit_swap_request():
    """
    send a bookswap request by first checking is the user is logged in,
    check if requested book or offered book is available and creates
    a swap_request object.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to '
                        'submit a swap request'}), 401

    user_id = session['user_id']
    data = request.get_json()

    requested_book_id = data.get('requested_book_id')
    offered_book_id = data.get('offered_book_id')

    requested_book = storage.get(Book, requested_book_id)
    if not requested_book:
        return jsonify({'message': 'Requested book not '
                        'found', 'success': False}), 404

    offered_book = storage.get(Book, offered_book_id)
    if not offered_book:
        return jsonify({'message': 'Offered book not '
                        'found', 'success': False}), 404

    recipient_id = requested_book.user_id

    swap_request = SwapRequest(
        requester_id=user_id,
        recipient_id=recipient_id,
        requested_book_id=requested_book_id,
        offered_book_id=offered_book_id,
        status='pending',
        swapped=False,
        viewed=False,
    )

    try:
        storage.new(swap_request)
        storage.save()
        return jsonify({'message': 'Swap request submitted '
                        'successfully', 'success': True}), 201
    except IntegrityError:
        storage.rollback()
        return jsonify({'message': 'An error occurred while sending your swap'
                        ' request', 'success': False}), 500


@app.route('/user_books', strict_slashes=False)
def get_users_books():
    """
    gets books added by the current user which they can use for swapping with
    other users
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to view '
                        'their books'}), 401

    user_id = session['user_id']
    users_books = storage.find(Book, Book.user_id == user_id)

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
            'location': book.location,
        }
        users_book_list.append(book_details)

    return jsonify(users_book_list), 200


@app.route('/home/swap_requests', strict_slashes=False)
def render_swap_history():
    """renders a html where the user can view the swap request"""
    return render_template('/swap_history.html')


@app.route('/swap_records', methods=['GET'])
def get_swap_records():
    """
    get the swap record both incoming and users own requests
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to view'
                        ' swap requests'}), 401

    user_id = session['user_id']

    incoming_requests = storage.find(SwapRequest, SwapRequest.recipient_id ==
                                     user_id)
    your_requests = storage.find(SwapRequest, SwapRequest.requester_id ==
                                 user_id)

    def format_request(record):
        requested_book = storage.get(Book, record.requested_book_id)
        offered_book = storage.get(Book, record.offered_book_id)

        if not requested_book and not offered_book:
            return

        return {
            'id': record.id,
            'requested_date': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'requested_book_title': requested_book.title,
            'offered_book_title': offered_book.title,
            'location': offered_book.location,
            'status': record.status,
            'requester_id': record.requester_id,
            'viewed': record.viewed,
        }

    incoming_requests_data = [format_request(record) for record in
                              incoming_requests]
    your_requests_data = [format_request(record) for record in your_requests]

    unviewed_count = sum(1 for record in incoming_requests if record.viewed ==
                         0)

    return jsonify({
        'user_id': user_id,
        'incoming_requests': incoming_requests_data,
        'your_requests': your_requests_data,
        'unviewed_count': unviewed_count,
    })


@app.route('/mark_request_viewed', strict_slashes=False, methods=['POST'])
def mark_request_viewed():
    """
    Marks all swap requests as viewed for the logged-in user.

    Returns:
        flask.Response: JSON response indicating success or failure.
            - 200 OK: All requests marked as viewed.
            - 401 Unauthorized: User must be logged in first.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in first'}), 401
    user_id = session['user_id']

    user_requests = storage.find(SwapRequest, SwapRequest.recipient_id ==
                                 user_id)

    for req in user_requests:
        if req.viewed == 0:
            req.viewed = 1
    storage.save()

    return jsonify({'message': 'All requests marked as viewed'}), 200


@app.route('/swap_request/<request_id>/<action>', methods=['POST'])
def update_swap_request_status(request_id, action):
    """
    Updates the status of a swap request.

    Args:
        request_id (str): The ID of the swap request to update.
        action (str): The action to perform on the swap request ('accept' or
        'decline').

    Returns:
        flask.Response: JSON response indicating success or failure.
            - 200 OK: Swap request accepted or declined successfully.
            - 400 Bad Request: Invalid action.
            - 401 Unauthorized: User must be logged in to update swap requests.
            - 403 Forbidden: Unauthorized action.
            - 404 Not Found: Swap request not found.
            - 500 Internal Server Error: An error occurred during processing.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in'
                        ' to update swap requests'}), 401

    user_id = session['user_id']
    swap_request = storage.get(SwapRequest, request_id)

    if not swap_request:
        return jsonify({'error': 'Swap request not found'}), 404

    requested_book = storage.get(Book, swap_request.requested_book_id)

    if requested_book.user_id != user_id:
        return jsonify({'error': 'Unauthorized action'}), 403

    if action == 'accept':
        swap_request.status = 'accepted'
        swap_request.swapped = True
    elif action == 'decline':
        swap_request.status = 'declined'
    else:
        return jsonify({'error': 'Invalid action'}), 400

    try:
        storage.save()
        return jsonify({'message': f'Swap request'
                        f' {action}ed successfully'}), 200
    except Exception as e:
        storage.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/cancel_swap_request/<request_id>', methods=['DELETE'])
def cancel_swap_request(request_id):
    """
    Cancels a swap request.

    Args:
        request_id (str): The ID of the swap request to cancel.

    Returns:
        flask.Response: JSON response indicating success or failure.
            - 200 OK: Swap request cancelled successfully.
            - 401 Unauthorized: User must be logged in.
            - 403 Forbidden: User is not authorized to cancel this swap
            request.
            - 404 Not Found: Swap request not found.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'user must be logged in'}), 401

    swap_request = storage.get(SwapRequest, request_id)

    if not swap_request:
        return jsonify({'error': 'swap request not found'}), 404

    if swap_request.requester_id != session['user_id']:
        return jsonify({'error': 'you are not authorised to '
                        'cancel this swap request'}), 403

    storage.delete(swap_request)
    storage.save()

    return jsonify({'message': 'swap request cancelled successfully'}), 200


@app.route('/home/messages', strict_slashes=False)
def render_messages_html():
    """
    Renders the messages.html template with optional recipient_id parameter.

    Query Parameters:
        recipient_id (str): Optional. The ID of the recipient user.

    Returns:
        flask.Response: HTML response rendering messages.html template.
            - Redirect to login page if user is not logged in.
    """
    recipient_id = request.args.get('recipient_id', None)
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    if recipient_id:
        chat_exists = storage.find(Message,
                                   ((Message.sender_id == user_id) &
                                    (Message.recipient_id == recipient_id)) |
                                   ((Message.sender_id == recipient_id) &
                                    (Message.recipient_id == user_id))
                                   )

        if not chat_exists:
            welcome_message = Message(
                sender_id=user_id,
                recipient_id=recipient_id,
                content="Hello! Let's start chatting."
            )
            storage.new(welcome_message)
            storage.save()

    return render_template('messages.html', recipient_id=recipient_id)


@app.route('/fetch_chats', strict_slashes=False, methods=['GET'])
def fetch_chats():
    """
    Fetches the list of chats (conversations) for the logged-in user.

    Returns:
        flask.Response: JSON response containing a list of chats.
            - 200 OK: List of chats fetched successfully.
            - 401 Unauthorized: User must be logged in to view chats.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged in to view chats'}), 401

    user_id = session['user_id']
    chats = []

    messages_sent = storage.find(Message, Message.sender_id == user_id)
    for message in messages_sent:
        if message.recipient_id not in chats:
            chats.append(message.recipient_id)

    messages_received = storage.find(Message, Message.recipient_id == user_id)
    for message in messages_received:
        if message.sender_id not in chats:
            chats.append(message.sender_id)

    chat_list = []

    for chat_id in chats:
        other_user = storage.get(User, chat_id)
        if other_user:
            chat_list.append({
                'id': chat_id,
                'other_user': other_user.first_name,
            })

    return jsonify(chat_list)


@app.route('/fetch_messages/<chat_id>', methods=['GET'])
def fetch_messages(chat_id):
    """
    Fetches messages for a specific chat/conversation.

    Args:
        chat_id (str): The ID of the chat to fetch messages for.

    Returns:
        flask.Response: JSON response containing the messages for the
        specified chat.
            - 200 OK: Messages fetched successfully.
            - 401 Unauthorized: User must be logged in to view messages.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User must be logged'
                        ' in to view messages'}), 401

    user_id = session['user_id']

    messages = storage.find(Message,
                            ((Message.sender_id == user_id) &
                             (Message.recipient_id == chat_id)) |
                            ((Message.sender_id == chat_id) &
                             (Message.recipient_id == user_id))
                            )

    message_list = [{
        'sender_id': user_id,
        'sender_name': storage.get(User, message.sender_id).first_name,
        'content': message.content,
    } for message in messages]

    return jsonify(message_list)


@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Sends a message to a chat recipient.

    Request JSON Body:
        {
            "chat_id": "recipient_user_id",
            "content": "message_content"
        }

    Returns:
        flask.Response: JSON response indicating success or failure.
            - 200 OK: Message sent successfully.
            - 400 Bad Request: Missing chat ID or message content.
            - 401 Unauthorized: User must be logged in to send messages.
            - 500 Internal Server Error: An error occurred while sending the
            message.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User'
                        ' must be logged in to send messages'}), 401

    user_id = session['user_id']
    data = request.get_json()

    chat_id = data.get('chat_id')
    content = data.get('content')

    if not chat_id or not content:
        return jsonify({'message': 'Chat ID or message'
                        ' content missing', 'success': False}), 400

    new_message = Message(
        sender_id=user_id,
        recipient_id=chat_id,
        content=content,
    )

    try:
        storage.new(new_message)
        storage.save()
        return jsonify({'message': 'Message sent '
                        'successfully', 'success': True}), 200
    except IntegrityError:
        storage.rollback()
        return jsonify({'message': 'An error occurred while '
                        'sending the message', 'success': False}), 500


@app.route('/chat', strict_slashes=False)
def render_chat_html():
    """
    Renders the chat.html template with optional recipient_id parameter.

    Query Parameters:
        recipient_id (str): Optional. The ID of the recipient user.

    Returns:
        flask.Response: HTML response rendering chat.html template.
    """
    recipient_id = request.args.get('recipient_id')
    return render_template('chat.html', recipient_id=recipient_id)


@app.route('/unread_message_count', strict_slashes=False, methods=['GET'])
def unread_messages():
    """
    Retrieves the count of unread messages for the logged-in user.

    Returns:
        flask.Response: JSON response containing the count of unread messages.
            - 200 OK: Unread message count retrieved successfully.
            - 401 Unauthorized: User must be logged in first.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'you need to be logged in first'}), 401
    user_id = session['user_id']

    unread_count = storage.count(Message, recipient_id=user_id, is_read=0)

    return jsonify({'unread_message': unread_count})


@app.route('/mark_messages_as_read', strict_slashes=False, methods=['POST'])
def mark_messages_read():
    """
    Marks all unread messages as read for the logged-in user.

    Returns:
        flask.Response: JSON response indicating success or failure.
            - 200 OK: Messages marked as read successfully.
            - 401 Unauthorized: User must be logged in first.
            - 500 Internal Server Error: An error occurred while marking the
            messages.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'You need to be logged in first'}), 401
    user_id = session['user_id']

    unread_messages = storage.find(Message, Message.recipient_id ==
                                   user_id, Message.is_read == 0)

    for message in unread_messages:
        message.is_read = True

    try:
        storage.save()
        return jsonify({'message': 'Messages marked successfully'}), 200
    except IntegrityError:
        storage.rollback()
        return jsonify({'error': 'Error while marking the '
                        'messages', 'success': False}), 500


if __name__ == "__main__":
    storage.reload()
    app.run(debug=True, port=5002)
