from flask import Flask, render_template, request, jsonify, redirect, flash, session
from models import storage
from models.user import User
from models.book import Book
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = '4769bd47b01107b11132b278b09cb4b61d710edc6fc19aa2'


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


@app.route('/signup', strict_slashes=False)
def sign_up_page():
    return (render_template('sign_up.html'))


@app.route('/home')
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

        if not title or not author or not condition:
            flash('Title, author, and condition are required fields', 'error')
            return redirect('/home/add_book')

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            condition=condition,
            description=description,
            user_id=user_id
        )
        try:
            storage.new(new_book)
            storage.save()
            flash('Successfully added a book', 'success')
            redirect('/home')
        except IntegrityError:
            storage.rollback()
            flash('An error occured while adding book', 'error')
            return redirect('/home/add_book')

    return (render_template('add_book.html'))


if __name__ == "__main__":
    storage.reload()
    app.run(debug=True, port=5001)
