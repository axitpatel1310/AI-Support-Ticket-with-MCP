from flask import Flask, render_template,request,session,redirect,url_for
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
from agent.ollama_client import chat_ollama
from caching.cache import cache_response,get_cached_response
from caching.save_conv import save_message, create_conversation

app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route("/")
def home():
    conn = sqlite3.connect("db.sqlite")
    conversations = conn.execute("select * from conversations").fetchall()
    conn.close()
    return render_template("index.html",conversations=conversations)

@app.route("/dashboard")
def dashboard():
    return render_template("teams/dashboard.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect("db.sqlite")
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (username,hashed_password)
        )
        conn.commit()
        conn.close()
        return f"User {username} is registered successfully"
        
    return render_template("auth/register.html")
    
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("db.sqlite")
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user[2],password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")
        return "Invalid username or password"
    return render_template("auth/login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/chat/<int:conversation_id>", methods=["GET", "POST"])
def chat_page(conversation_id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("db.sqlite")
    conn.row_factory = sqlite3.Row
    conversation = conn.execute(
        """
        SELECT *
        FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, session["user_id"])
    ).fetchone()

    if not conversation:
        conn.close()
        return "Conversation not found", 404

    if request.method == "POST":
        message = request.form["message"]
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, "user", message)
        )
        conn.commit()
        response = chat_ollama(message)
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, "assistant", response)
        )
        conn.execute(
            """
            UPDATE conversations
            SET last_activity = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,)
        )
        conn.commit()
    messages = conn.execute(
        """
        SELECT *
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
        """,
        (conversation_id,)
    ).fetchall()
    conn.close()
    return render_template(
        "chat.html",
        messages=messages,
        conversation_id=conversation_id
    )

if __name__ == "__main__":
    app.run(debug=True)