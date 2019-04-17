from flask import Flask, render_template, session, request, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SESSION_PERMANENT'] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

chats = []
users = []
words = {"1": ""}
@app.route('/')
def index():

    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
    name = request.form.get("name")
    if name not in users:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@socketio.on("chat")
def chat_render(data):
    text = data["text"]
    user = data["user"]
    chat = f"{user}: {text}"
    chats.append(chat)
    emit("new_message", {"chat": chat}, broadcast=True)


if __name__ == "__main__":
    app.run(debug=True)
