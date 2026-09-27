from flask import Flask, render_template,request,session,redirect
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    username = "Axit"
    ticket = 5
    return render_template("teams/dashboard.html",username= username,ticket= ticket)

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
    
@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("chat.html")    

if __name__ == "__main__":
    app.run(debug=True)