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

tasks = {
        1: {
            'id': 1,
            'title': u'Todo Project',
            'description': u'Create a todo project with blah blah',
            'status' : 'Backlog',
            'what' : ["Fun"],
            'when' : 'Now',
            'where' : ["Computer"],
            'done': False
            },
        2: {
            'id': 2,
            'title': u'Learn Python',
            'description': u'Need to find a good Python tutorial on the web',
            'status' : 'Backlog',
            'what' : ["Project", "Fun"],
            'when' : 'Daily',
            'where' : ["Computer"],
            'done': False
            },
        3: {
            'id': 3,
            'title': u'Fun',
            'description': u'Fun stuff',
            'status' : 'Backlog',
            'what' : ["Project", "Fun"],
            'when' : 'Daily',
            'where' : ["Computer"],
            'done': False
            }

        }

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/tasks/', methods=['GET'])
def get_tasks():
    # return jsonify({'tasks': [make_public_task(task) for task in tasks]})
    return jsonify({'tasks': list(tasks.values())})


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
            'status': 'Backlog'
            }
    tasks[len(tasks) + 1] = task;
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
    return jsonify({'task': tasks[task_id]})

@app.route('/todo/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id in tasks: del tasks[task_id]
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
