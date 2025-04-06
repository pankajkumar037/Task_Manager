import sqlite3
from datetime import datetime, timedelta


conn = sqlite3.connect("task_manager.db", check_same_thread=False)
c = conn.cursor()

# DB setup
def init_db():
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT UNIQUE,
            department TEXT NOT NULL,
            joining_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            date TEXT,
            task_description TEXT,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    conn.commit()


def add_employee(emp_id, name, phone, email, department, join_date):
    try:
        c.execute("INSERT INTO employees (id, name, phone, email, department, joining_date) VALUES (?, ?, ?, ?, ?, ?)",
                  (emp_id, name, phone, email, department, join_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_employee(emp_id):
    c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    c.execute("DELETE FROM tasks WHERE employee_id = ?", (emp_id,))
    conn.commit()

def get_employees(department):
    c.execute("SELECT id, name FROM employees WHERE department = ?", (department,))
    return c.fetchall()


def add_task(emp_id, description, is_done):
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT id FROM tasks WHERE employee_id = ? AND date = ?", (emp_id, date))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE tasks SET task_description = ?, is_done = ? WHERE id = ?",
                  (description, int(is_done), existing[0]))
    else:
        c.execute("INSERT INTO tasks (employee_id, date, task_description, is_done) VALUES (?, ?, ?, ?)",
                  (emp_id, date, description, int(is_done)))
    conn.commit()

def get_summary(department):
    last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    c.execute('''
        SELECT e.name, e.joining_date, t.date, t.task_description, t.is_done
        FROM employees e
        LEFT JOIN tasks t ON e.id = t.employee_id
        WHERE e.department = ? AND t.date >= ?
        ORDER BY t.date DESC
    ''', (department, last_month))
    return c.fetchall()
