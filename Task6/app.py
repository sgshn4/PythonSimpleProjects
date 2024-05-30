from flask import Flask, render_template
import utils
import random

app = Flask(__name__)

db = utils.open_db()


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', db=generate_random())


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<string:id>/')
def post(id):
    return render_template('post.html', post=get_post(id))


def generate_random():
    selected_nums = []
    result = []
    i = 0
    while i < 10:
        rand = random.randint(0, len(db) - 1)
        if not rand in selected_nums:
            result.append(db[rand])
            selected_nums.append(rand)
            i += 1
    return make_text_shorter(result, 50)


def make_text_shorter(db, lenght):
    for i in db:
        if len(i.name) > 50:
            i.name = i.name[:lenght - 3] + '...'
    return db


def get_post(id):
    for i in db:
        if i.id == id:
            return i


if __name__ == '__main__':
    app.app_context()
    app.run(debug=True)
