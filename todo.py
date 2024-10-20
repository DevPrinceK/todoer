from datetime import datetime

from flask import (
    Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .auth import login_required

from .db import get_db

bp = Blueprint('todo', __name__, url_prefix='/todo')



@bp.route('/')
@login_required
def index():
    db = get_db()
    todos = db.execute(
        'SELECT t.id, u.username, title, detail, duedate, sts '
        'FROM todo t JOIN user u ON t.author_id = u.id '
        'WHERE author_id = ? '
        'ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
   
    return render_template('todo/index.html', todos=todos)


@bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip()
    db = get_db()
    
    # If the query is empty, show all todos
    if query.strip() == "":
        todos = db.execute(
            'SELECT t.id, u.username, title, detail, duedate, sts '
            'FROM todo t JOIN user u ON t.author_id = u.id '
            'WHERE author_id = ? '
            'ORDER BY created DESC',
            (g.user['id'],)
        ).fetchall()
    else:
        # If there is a search query, filter by the title (case-insensitive search)
        todos = db.execute(
            'SELECT t.id, u.username, title, detail, duedate, sts'
            ' FROM todo t JOIN user u ON t.author_id = u.id'
            ' WHERE title LIKE ?'
            'AND t.author_id = ?'
            ' ORDER BY created DESC',
            ('%' + query + '%', g.user['id'],)
        ).fetchall()

    return render_template('todo/index.html', todos=todos)



# @bp.route('/todos')
# @login_required
# def todos():
#     db = get_db()
#     todos = db.execute(
#         'SELECT u.username, title, detail, duedate, sts'
#         ' FROM todo t JOIN user u ON t.author_id = u.id'
#         ' ORDER BY created DESC'
#     ).fetchall()
   
#     return render_template('todo/index.html', todos=todos)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title'].strip()
        detail = request.form['detail'].strip()
        duedate = request.form['duedate']

        print(f"Due date before format: {duedate}")

        # validation
        if title == "":
            flash("Title is required")
            return redirect(url_for('todo.index'))
        elif detail == "":
            detail = title

        # Reformat the duedate to the proper format for SQLite
        try:
            duedate = datetime.strptime(duedate, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid due date format", category="danger")
            return redirect(url_for('todo.index'))
        
        print(f"Due date after format: {duedate}")


        db = get_db()
        db.execute(
            'INSERT INTO todo (title, detail, author_id, sts, duedate)'
            ' VALUES (?, ?, ?, ?, ?)',
            (title, detail, g.user['id'], 'Pending', duedate)
        )
        db.commit()
        return redirect(url_for('todo.index'))
    # get request / method
    return render_template('todo/create_todo.html')
        

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    todo = get_todo(id)
    if request.method == "POST":
        title = request.form['title'].strip()
        detail = request.form['detail'].strip()
        status = request.form['status'].strip()
        duedate = request.form['duedate']

        # validation
        if title == "":
            flash("Title can't be blank")
            return redirect(url_for('todo.index'))
        elif detail == "":
            detail = title

        # Reformat the duedate to the proper format for SQLite
        try:
            duedate = datetime.strptime(duedate, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid due date format", category="danger")
            return redirect(url_for('todo.index'))

        db = get_db()
        db.execute(
              'UPDATE todo SET title = ?, detail = ?, sts = ?, duedate = ?'
                ' WHERE id = ?'
                'AND author_id = ?',
                (title, detail, status, duedate, id, g.user['id'],)
        )
        db.commit()
        flash("Todo updated successfully", category="success")
        return redirect(url_for('todo.index'))
    print(f"Todo: {todo}")
    # get request / method
    return render_template('todo/update_todo.html', todo=todo)



@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_todo(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ? AND author_id = ?', (id, g.user['id'],))
    db.commit()
    flash("Todo deleted successfully", category="info")
    return redirect(url_for('todo.index'))



def get_todo(id, check_author=True):
    post = get_db().execute(
        'SELECT id, title, detail, author_id, sts, duedate'
        ' FROM todo'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post