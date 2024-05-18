from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/', strict_slashes=False)
def landing_page():
    return (render_template('landing_page.html'))


@app.route('/login', strict_slashes=False)
def login_page():
    return (render_template('login.html'))


@app.route('/signup', strict_slashes=False)
def sign_up_page():
    return (render_template('sign_up.html'))


@app.route('/sign_up', strict_slashes=False, methods=['POST'])
def signup():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']


if __name__ == "__main__":
    app.run(debug=True)
