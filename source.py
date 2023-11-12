import sqlite3
import click
import json

from flask import Flask, request, Response, redirect, render_template, g, flash

app = Flask(__name__)

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

@app.route("/get-tasks")
def get_tasks():
  db = get_db()
  records = db.execute('SELECT task FROM tasks').fetchall()
  tasks = [row[0] for row in records]
  return tasks 

@app.route("/add-task", methods=['PUT'])
def add_task():
  print("TRYING")
  task = request.form.get("newTask")
  print("Adding task: ", task)
  db = get_db()
  db.execute("INSERT INTO tasks(task) VALUES (?)",
      (task,)
      )
  db.commit()
  
  return task 

if __name__ == '__main__':
  app.run(port = 5000, debug = True)
