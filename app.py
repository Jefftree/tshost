from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

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

with open('tasks.pickle', 'rb') as handle:
  tasks = pickle.load(handle)

def persist():
    with open('tasks.pickle', 'wb') as handle:
        pickle.dump(tasks, handle)





@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/tasks/', methods=['GET'])
def get_tasks():
    # return jsonify({'tasks': [make_public_task(task) for task in tasks]})
    return jsonify({'tasks': [task for task in tasks.values() if task['done']== False]})


@app.route('/todo/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    if task_id not in tasks:
        abort(404)
    return jsonify({'task': tasks[task_id]})

@app.route('/todo/tasks/', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
            'id': len(tasks) + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'when': request.json.get('when', ""),
            'status': 'Backlog',
            'done': False
            }
    tasks[len(tasks) + 1] = task;
    persist()
    return jsonify({'task': task}), 201

@app.route('/todo/tasks/<int:task_id>', methods=['PUT'])
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
    tasks[task_id]['status'] = request.json.get('status', tasks[task_id]['status'])
    persist()
    return jsonify({'task': tasks[task_id]})

@app.route('/todo/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id in tasks: tasks[task_id]['done'] = True
    persist()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
