from flask import Flask, request, redirect, session, render_template_string
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import json, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

USER_FILE = 'users.json'
SUGGESTION_FILE = 'suggestions.json'

chatbot = ChatBot(
    'CollegeBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english.greetings", "chatterbot.corpus.english.conversations")

list_trainer = ListTrainer(chatbot)
list_trainer.train([
    "What is the college timetable?",
    "You can check the timetable on the college portal or ask your department head."
])
list_trainer.train([
    "How can I apply for hostel?",
    "Please fill the hostel application form available on the website."
])
list_trainer.train([
    "What is the admission process?",
    "You can apply through our official website. Admissions are based on entrance exam and merit list."
])
list_trainer.train([
    "Are there placement opportunities?",
    "Yes, top companies visit our campus for placements every year."
])
list_trainer.train([
    "scholarship information?"
    "state scholarship portal"
])
list_trainer.train([
    "how many courses are available in suk?"
    "total 48 courses are available including graduate,post graduate & phd."
])
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_json(USER_FILE)
        email = request.form['email']
        if any(user['email'] == email for user in users):
            return "Email already registered!"
        users.append({
            'name': request.form['name'],
            'email': email,
            'password': request.form['password']
        })
        save_json(USER_FILE, users)
        return redirect('/login')
    return render_template_string(BASE_HTML, page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json(USER_FILE)
        email = request.form['email']
        password = request.form['password']
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        if user:
            session['user'] = user['email']
            return redirect('/chat')
        return "Invalid credentials"
    return render_template_string(BASE_HTML, page='login')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect('/login')
    message = ''
    response = ''
    if request.method == 'POST':
        message = request.form['message']
        response = chatbot.get_response(message)
    return render_template_string(BASE_HTML, page='chat', message=message, response=response)

@app.route('/suggest', methods=['POST'])
def suggest():
    if 'user' not in session:
        return redirect('/login')
    suggestions = load_json(SUGGESTION_FILE)
    suggestions.append({
        'email': session['user'],
        'message': request.form['message']
    })
    save_json(SUGGESTION_FILE, suggestions)
    return "Suggestion submitted successfully"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Unified HTML + CSS in one string
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>College Chatbot</title>
    <style>
        body {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url('https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            font-family: 'Segoe UI', sans-serif;
            color: white;
            margin: 0;
            padding: 0;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.6);
            padding: 30px;
            margin: 80px auto;
            width: 60%;
            border-radius: 15px;
            box-shadow: 0 0 10px #000;
            text-align: center;
        }
        input, textarea, button {
            width: 80%;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        a {
            color: #00ffff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if page == 'login' %}
            <h2>Login</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <button type="submit">Login</button>
            </form>
            <p>Don't have an account? <a href="/register">Register here</a></p>
        {% elif page == 'register' %}
            <h2>Register</h2>
            <form method="POST">
                <input type="text" name="name" placeholder="Full Name" required><br>
                <input type="email" name="email" placeholder="Email" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <button type="submit">Register</button>
            </form>
            <p>Already have an account? <a href="/login">Login here</a></p>
        {% elif page == 'chat' %}
            <h1>🎓 Welcome to College Chatbot</h1>
            <form method="POST">
                <textarea name="message" placeholder="Ask me anything..." required></textarea><br>
                <button type="submit">Send</button>
            </form>
            {% if message %}
                <p><strong>You:</strong> {{ message }}</p>
                <p><strong>Bot:</strong> {{ response }}</p>
            {% endif %}
            <form method="POST" action="/suggest">
                <input type="text" name="message" placeholder="Suggest a question or improvement" required>
                <button type="submit">Submit Suggestion</button>
            </form>
            <br>
            <a href="/logout">Logout</a>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
