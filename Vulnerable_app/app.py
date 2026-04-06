"""
Intentionally Vulnerable Flask Application
For testing the AI-Driven DevSecOps Pipeline
DO NOT DEPLOY TO PRODUCTION - FOR TESTING ONLY
"""

from flask import Flask, request, render_template_string, redirect, session, make_response
import sqlite3
import os
import subprocess
import pickle
import hashlib
import random

app = Flask(__name__)

# CWE-798: Hardcoded Secret
app.secret_key = "super_secret_key_12345"  # Hardcoded secret key
API_KEY = "sk_live_1234567890abcdef"  # Hardcoded API key
DATABASE_PASSWORD = "admin123"  # Hardcoded database password

# CWE-489: Debug mode enabled
DEBUG_MODE = True

# CWE-614: Insecure cookie configuration - no Secure, HttpOnly, or SameSite flags
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None

# In-memory store for comments (stored XSS demo)
comments_store = []


@app.after_request
def remove_security_headers(response):
    """CWE-693: Intentionally missing security headers for DAST detection"""
    # Leak server version info
    response.headers['Server'] = 'Flask/2.3.2 Python/3.11.0'
    response.headers['X-Powered-By'] = 'Flask'
    # Explicitly remove any security headers
    response.headers.pop('X-Content-Type-Options', None)
    response.headers.pop('X-Frame-Options', None)
    response.headers.pop('Content-Security-Policy', None)
    response.headers.pop('Strict-Transport-Security', None)
    response.headers.pop('X-XSS-Protection', None)
    response.headers.pop('Referrer-Policy', None)
    response.headers.pop('Permissions-Policy', None)
    return response

# Initialize database
def init_db():
    conn = sqlite3.connect('vulnerable_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            user_id INTEGER
        )
    ''')
    # Insert test data
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 1)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'password', 'user@example.com', 0)")
    conn.commit()
    conn.close()

init_db()


# Home page
@app.route('/')
def index():
    html = '''
    <html>
        <head><title>Vulnerable App</title></head>
        <body>
            <h1>Welcome to Vulnerable App</h1>
            <p>This application contains intentional security vulnerabilities for testing.</p>
            <ul>
                <li><a href="/login">Login</a></li>
                <li><a href="/search">Search Users</a></li>
                <li><a href="/upload">Upload File</a></li>
                <li><a href="/ping">Ping Utility</a></li>
                <li><a href="/calculate">Calculator (CRITICAL)</a></li>
                <li><a href="/deserialize">Deserializer (CRITICAL)</a></li>
                <li><a href="/admin">Admin Panel</a></li>
                <li><a href="/profile?name=Guest">View Profile</a></li>
                <li><a href="/comments">Comments Board</a></li>
                <li><a href="/register">Register</a></li>
                <li><a href="/token">Generate Token</a></li>
                <li><a href="/info">Server Info</a></li>
            </ul>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-89: SQL Injection vulnerability
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Vulnerable SQL query using string formatting
        conn = sqlite3.connect('vulnerable_app.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = user[4]
                return redirect('/dashboard')
            else:
                return "Login failed!"
        except Exception as e:
            # CWE-209: Information disclosure through error messages
            return f"Database error: {str(e)}"
    
    html = '''
    <html>
        <body>
            <h2>Login</h2>
            <form method="POST">
                Username: <input name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Login">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-79: Cross-Site Scripting (XSS) vulnerability
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search', '')
        
        # Vulnerable: Direct rendering of user input without escaping
        html = f'''
        <html>
            <body>
                <h2>Search Results for: {search_term}</h2>
                <p>No results found for {search_term}</p>
                <a href="/search">Search again</a>
            </body>
        </html>
        '''
        return render_template_string(html)
    
    html = '''
    <html>
        <body>
            <h2>User Search</h2>
            <form method="POST">
                Search: <input name="search">
                <input type="submit" value="Search">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-78: OS Command Injection vulnerability
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form.get('host', '')
        
        # Vulnerable: Using shell=True with user input
        try:
            result = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT)
            output = result.decode()
        except Exception as e:
            output = str(e)
        
        html = f'''
        <html>
            <body>
                <h2>Ping Results</h2>
                <pre>{output}</pre>
                <a href="/ping">Ping again</a>
            </body>
        </html>
        '''
        return render_template_string(html)
    
    html = '''
    <html>
        <body>
            <h2>Ping Utility</h2>
            <form method="POST">
                Host: <input name="host" value="localhost">
                <input type="submit" value="Ping">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-22: Path Traversal vulnerability
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        filename = request.form.get('filename', 'default.txt')
        content = request.form.get('content', '')
        
        # Vulnerable: No path validation
        file_path = f"uploads/{filename}"
        
        try:
            os.makedirs('uploads', exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            return f"File saved to {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    html = '''
    <html>
        <body>
            <h2>File Upload</h2>
            <form method="POST">
                Filename: <input name="filename" value="test.txt"><br>
                Content: <textarea name="content"></textarea><br>
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-95: Remote Code Execution via eval() - CRITICAL
@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        expression = request.form.get('expression', '')
        
        # CRITICAL VULNERABILITY: eval() with user input allows arbitrary code execution
        try:
            result = eval(expression)  # Extremely dangerous!
            output = f"Result: {result}"
        except Exception as e:
            output = f"Error: {str(e)}"
        
        html = f'''
        <html>
            <body>
                <h2>Calculator Results</h2>
                <p>{output}</p>
                <a href="/calculate">Calculate again</a>
            </body>
        </html>
        '''
        return render_template_string(html)
    
    html = '''
    <html>
        <body>
            <h2>Calculator</h2>
            <form method="POST">
                Expression: <input name="expression" value="2+2">
                <input type="submit" value="Calculate">
            </form>
            <p>Try: 2+2, 10*5, etc.</p>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-502: Insecure Deserialization - CRITICAL
@app.route('/deserialize', methods=['GET', 'POST'])
def deserialize():
    if request.method == 'POST':
        data = request.form.get('data', '')
        
        # CRITICAL VULNERABILITY: pickle.loads() with user input allows RCE
        try:
            import base64
            decoded = base64.b64decode(data)
            obj = pickle.loads(decoded)  # Extremely dangerous!
            output = f"Deserialized object: {obj}"
        except Exception as e:
            output = f"Error: {str(e)}"
        
        html = f'''
        <html>
            <body>
                <h2>Deserialization Results</h2>
                <p>{output}</p>
                <a href="/deserialize">Try again</a>
            </body>
        </html>
        '''
        return render_template_string(html)
    
    html = '''
    <html>
        <body>
            <h2>Object Deserializer</h2>
            <form method="POST">
                Base64 Data: <input name="data" size="50">
                <input type="submit" value="Deserialize">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-306: Missing Authentication
@app.route('/admin')
def admin():
    # Vulnerable: No authentication check
    html = '''
    <html>
        <body>
            <h2>Admin Panel</h2>
            <p>Welcome to the admin panel!</p>
            <p>Sensitive configuration data:</p>
            <ul>
                <li>Database: vulnerable_app.db</li>
                <li>API Key: sk_live_1234567890abcdef</li>
                <li>Debug: Enabled</li>
            </ul>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-352: CSRF vulnerability
@app.route('/transfer', methods=['POST'])
def transfer():
    # Vulnerable: No CSRF protection
    amount = request.form.get('amount', '0')
    to_account = request.form.get('to', 'unknown')
    
    return f"Transferred ${amount} to {to_account}"


# CWE-327: Weak cryptographic hash
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Vulnerable: Using MD5 for password hashing
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect('vulnerable_app.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password_hash}')")
            conn.commit()
            return "User registered!"
        except:
            return "Registration failed!"
        finally:
            conn.close()
    
    html = '''
    <html>
        <body>
            <h2>Register</h2>
            <form method="POST">
                Username: <input name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Register">
            </form>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-330: Insecure Random
@app.route('/token')
def generate_token():
    # Vulnerable: Using insecure random for security token
    token = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return f"Your token: {token}"


# CWE-295: SSL Verification Disabled
@app.route('/fetch', methods=['POST'])
def fetch_url():
    import requests
    url = request.form.get('url', '')
    
    # Vulnerable: SSL verification disabled
    try:
        response = requests.get(url, verify=False, timeout=5)
        return response.text[:500]
    except Exception as e:
        return f"Error: {str(e)}"


# Dashboard (requires login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    username = session.get('username', 'User')
    html = f'''
    <html>
        <body>
            <h2>Dashboard</h2>
            <p>Welcome, {username}!</p>
            <a href="/logout">Logout</a>
        </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# CWE-79: GET-based Reflected XSS (easy for ZAP spider to discover)
@app.route('/profile')
def profile():
    name = request.args.get('name', 'Guest')
    # Vulnerable: Directly reflecting GET parameter without escaping
    html = f'''
    <html>
        <head><title>Profile - {name}</title></head>
        <body>
            <h2>User Profile</h2>
            <p>Welcome, {name}!</p>
            <p>This is your profile page.</p>
            <form method="GET" action="/profile">
                Change name: <input name="name" value="{name}">
                <input type="submit" value="Update">
            </form>
            <a href="/">Home</a>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-79: Stored XSS via comments
@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        author = request.form.get('author', 'Anonymous')
        comment = request.form.get('comment', '')
        # Vulnerable: Storing and displaying user input without sanitization
        comments_store.append({'author': author, 'comment': comment})
    
    comments_html = ''
    for c in comments_store:
        # Vulnerable: Direct rendering without escaping
        comments_html += f'<div class="comment"><b>{c["author"]}</b>: {c["comment"]}</div>'
    
    html = f'''
    <html>
        <head><title>Comments</title></head>
        <body>
            <h2>Comments Board</h2>
            <form method="POST">
                Name: <input name="author" value="Anonymous"><br>
                Comment: <textarea name="comment"></textarea><br>
                <input type="submit" value="Post Comment">
            </form>
            <hr>
            <h3>Recent Comments</h3>
            {comments_html}
            <p><a href="/">Home</a></p>
        </body>
    </html>
    '''
    return render_template_string(html)


# CWE-200: Information Exposure - Server info endpoint
@app.route('/info')
def server_info():
    # Vulnerable: Exposing sensitive server information
    import sys
    import platform
    html = f'''
    <html>
        <head><title>Server Info</title></head>
        <body>
            <h2>Server Information</h2>
            <table border="1">
                <tr><td>Python Version</td><td>{sys.version}</td></tr>
                <tr><td>Platform</td><td>{platform.platform()}</td></tr>
                <tr><td>Architecture</td><td>{platform.machine()}</td></tr>
                <tr><td>Debug Mode</td><td>{DEBUG_MODE}</td></tr>
                <tr><td>Secret Key</td><td>{app.secret_key}</td></tr>
                <tr><td>Database Password</td><td>{DATABASE_PASSWORD}</td></tr>
            </table>
            <a href="/">Home</a>
        </body>
    </html>
    '''
    return render_template_string(html)


if __name__ == '__main__':
    # CWE-489: Running with debug=True in production
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)
