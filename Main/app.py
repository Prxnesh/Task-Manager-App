from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

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


