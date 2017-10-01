"""
League of Lords' Flask app
"""

from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def main():
    """This the the homepage"""
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
