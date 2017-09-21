from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello John from flask!"

if __name__ == 'main':
	app.run(host='0.0.0.0',port=5000)

