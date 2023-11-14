import sqlite3
import click

from flask import Flask, request, Response, redirect, render_template, g, flash

app = Flask(__name__, instance_relative_config=True)

def get_db():
  if 'db' not in g:
    g.db = sqlite3.connect(
      'tasks.sqlite',
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row

  return g.db

def close_db(e=None):
  db = g.pop('db', None)
  if db is not None:
    db.close()

def init_db():
  db = get_db()
  with app.open_resource('schema.sql') as f:
    db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
  init_db()
  click.echo('Initialized DB')

# Register application
app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

@app.route("/")
def home():
  print("we did it")
  return render_template("index.html")

@app.route("/get-tasks", methods=['GET'])
def get_tasks():
  db = get_db()
  records = db.execute('SELECT * FROM tasks').fetchall()
  task_ids = [row[0] for row in records]
  tasks = [row[1] for row in records]
  res = {task_ids[i]: tasks[i] for i in range(len(task_ids))}
  return render_template("tasks.html", tasks=res)

@app.route("/add-task", methods=['PUT'])
def add_task():
  task = request.form.get("newTask")
  db = get_db()
  db.execute("INSERT INTO tasks(task) VALUES (?)",
      (task,)
      )
  db.commit()
  return render_template("index.html")

@app.route("/delete-task/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
  db = get_db()
  db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
  db.commit()
  return '', 200

if __name__ == '__main__':
  app.run(port = 5000, debug = True)
