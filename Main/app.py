from flask import Flask, request, jsonify
import sqlite3
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User model

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# Task Model (Modify to include user_id)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link tasks to users

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route: Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

# Route: Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({"message": "Login successful!"})
    return jsonify({"error": "Invalid credentials"}), 401

# Route: Logout User
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

# Route: Create a Task (Now Requires Login)
@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.json
    new_task = Task(title=data['title'], priority=data['priority'], user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully!"})

# Route: Get Tasks (Only User's Tasks)
@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([{"id": task.id, "title": task.title, "priority": task.priority} for task in tasks])




@app.route('/')
def home():
    return "Task Manager API is running! Access /tasks to view tasks."


# Create database and tasks table if it doesn't exist
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) NOT NULL DEFAULT 'Medium'
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Initialize DB when the app starts

# ✅ 1. Get all tasks

@app.route('/tasks', methods=['GET'])
def get_task():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    task_list = [{"id": t[0], "title": t[1], "completed": bool(t[2]), "priority": t[3]} for t in tasks]
    return jsonify(task_list)

# ✅ 2. Create a new task

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get("title")
    priority = data.get("priority", "Medium") # Default priority is "Medium"

    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    conn = sqlite3.connect("tasks.db") 
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, priority) VALUES (?,?)", (title, priority))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task created successfully"}), 201

# ✅ 3. Update a task (mark as completed)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    completed = data.get("completed")

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed =? WHERE id =?", (completed, task_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated successfully"}) 

# ✅ 4. Delete a task

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id =?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)


