from flask import Flask, render_template
app = Flask(__name__)


@app.route('/', strict_slashes=False)
def landing_page():
    return (render_template('landing_page.html'))


@app.route('/login', strict_slashes=False)
def login_page():
    return ("comming soon..")


@app.route('/signup', strict_slashes=False)
def sign_up_page():
    return ("coming soon..")


if __name__ == "__main__":
    app.run(debug=True)
