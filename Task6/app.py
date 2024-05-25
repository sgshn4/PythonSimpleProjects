from flask import Flask, render_template
import json

app = Flask(__name__)
f = open('posts/db.json', 'r')
db = json.load(f)
print(db)


@app.route('/')
@app.route('/home')
def index():

    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/user/<string:name>/<string:id>/')
def user(name, id):
    return 'User page: ' + name + ' - ' + id


if __name__ == '__main__':
    app.app_context()
    app.run(debug=True)
