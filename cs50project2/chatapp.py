from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

users = ["user", "admin"]
channels = []
rooms = []


class User:
    def __init__(self, name):
        self.name = name


class ChatRoom:

    def __init__(self, room_name):
        self.chats = []
        self.name = room_name

        @socketio.on(room_name)
        def chat_render(data):
            print(f"recived signal from room:{room_name}")
            text = data["text"]
            user = session["user_name"]
            chat = f"{user}: {text}"
            self.chats.append(chat)
            if len(self.chats) > 100:
                del self.chats[0]
            emit(room_name, {"chat": chat}, broadcast=True)


def create_newroom(roomname):
    room = ChatRoom(room_name=roomname)
    channels.append(room.name)
    rooms.append(room)


@app.route('/createRoom')
def create_room():
    return render_template("create_room.html")


@app.route('/roomStatus', methods=["POST"])
def room_status():
    name = request.form.get("name")
    if name not in channels:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@app.route("/creatingRoom", methods=["POST"])
def creating_room():
    name = request.form.get("roomName")
    print(name)
    create_newroom(roomname=name)
    return redirect(url_for("index"))


@app.route('/')
def index():
    if session.get("login") is None:
        session["login"] = False
        return render_template("login.html")

    if session["user_name"] in users:
        if session["room"] is not None:
            return redirect(url_for("chat_room", roomName=session['room']))

        return render_template("index.html", users=users, username=session["user_name"], channel=channels)
    else:
        return redirect(url_for("choose_name"))


@app.route('/chooseName', methods=["GET"])
def choose_name():
    return render_template("login.html")


@app.route('/logging', methods=["post"])
def logging():
    user_name = request.form.get("user")
    if user_name not in users:
        user = User(name=user_name)
        users.append(user.name)
        session["login"] = True
        session["user_name"] = user_name
        session["room"] = None
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@app.route("/chatroom/<roomName>", methods=["GET"])
def chat_room(roomName):
    for room in rooms:

        if roomName == room.name:
            session["room"] = room.name
            user = session["user_name"]
            #  message = f"{user} has joined the chat"
            #  emit("console", {"message": message}, broadcast=True)

            return render_template("chatroom.html", user=user, code=roomName, chats=room.chats)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")

    if name not in users:
        return jsonify({"success": True})

    else:
        return jsonify({"success": False})


@app.route("/leavechat")
def leave_chat():
    session["room"] = None
    return redirect(url_for("index"))


create_newroom("default)_room")


if __name__ == "__main__":
    app.run(debug=True)
