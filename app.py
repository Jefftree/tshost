from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

from flask import make_response, request, current_app, Response
from flask.ext.login import LoginManager, UserMixin, login_required
from functools import update_wrapper

from datetime import datetime
import pickle

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

def insert_timestamp():
    return datetime.now().isoformat()

"""
tasks_format = {
        1: {
            'id': 1,
            'title': u'Todo Project',
            'description': u'Create a todo project with blah blah',
            'status' : 'Backlog',
            'what' : ["Fun"],
            'when' : 'Now',
            'where' : ["Desktop"],
            'done': False
            }
        }
"""

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"qwerty": ("qwerty", "s")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None

with open('tasks.pickle', 'rb') as handle:
  tasks = pickle.load(handle)

def persist():
    # Move to redis when performance becomes an issue
    with open('tasks.pickle', 'wb') as handle:
        pickle.dump(tasks, handle)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/tasks/', methods=['GET'])
@login_required
def get_tasks():
    # return jsonify({'tasks': [make_public_task(task) for task in tasks]})
    return jsonify({'tasks': [task for task in tasks.values() if task['status'] != "Completed"]})


@app.route('/todo/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    if task_id not in tasks:
        abort(404)
    return jsonify({'task': tasks[task_id]})

@app.route('/todo/tasks/', methods=['POST'])
@login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
            'id': len(tasks) + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'when': request.json.get('when', ""),
            'what': request.json.get('what', ""),
            'status': 'Backlog',
            'created': insert_timestamp(),
            'updated': insert_timestamp(),
            }
    tasks[len(tasks) + 1] = task;
    persist()
    return jsonify({'task': task}), 201

@app.route('/todo/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    if task_id not in tasks:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)

    tasks[task_id]['title'] = request.json.get('title', tasks[task_id]['title'])
    tasks[task_id]['description'] = request.json.get('description', tasks[task_id]['description'])
    tasks[task_id]['when'] = request.json.get('when', tasks[task_id]['when'])
    tasks[task_id]['what'] = request.json.get('what', tasks[task_id]['what'])
    tasks[task_id]['status'] = request.json.get('status', tasks[task_id]['status'])
    tasks[task_id]['updated'] = insert_timestamp()
    persist()
    return jsonify({'task': tasks[task_id]})

@app.route('/todo/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    if task_id in tasks: tasks[task_id]['status'] = "Completed"
    tasks[task_id]['completed'] = insert_timestamp()
    persist()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
