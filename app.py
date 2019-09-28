from flask import Flask, render_template, url_for, request, redirect
from flask_socketio import SocketIO
import ast
import uuid
from contextlib import contextmanager
from datetime import datetime

# import os

# os.system('conda install -c anaconda mysql-connector-python -y')


import pandas as pd
from mysql import connector as mcn


@contextmanager
def get_mysql_connection(**kwargs):
    con = mcn.connect(**kwargs)
    yield con
    con.close()


@contextmanager
def get_cursor(con):
    cur = con.cursor()
    yield cur
    cur.close()

DATABASE_CONNECTION_PARAMS = {
    'user': 'animesh',
    'password': '12345',
    'database': 'hackathon',
    'autocommit': True,
    'host': 'localhost',
    'port': 3306
}

def insert_mesage(username, message):
    insert_query = """
    INSERT IGNORE INTO messages
        (username, message)
    VALUES
        (%s, %s)
    """
    with get_mysql_connection(**DATABASE_CONNECTION_PARAMS) as mysql_con, get_cursor(mysql_con) as cur:
        cur.execute(insert_query, [username, message])

def get_all_messages():
    with get_mysql_connection(**DATABASE_CONNECTION_PARAMS) as mysql_con:
        return pd.read_sql_query("SELECT * FROM messages", mysql_con)

app = Flask(__name__)
app.secret_key = 'BigDong69'
socketio = SocketIO(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/<selection>')
def image_page(selection):
    if selection == 'chat':
        return redirct(url_for('chat_room'))
    img = url_for('static', filename=f'images/{selection}.jpg')
    return render_template('image.html', app_name=selection, app_pic=img)


def messageReceived(methods=None):
    if methods is None:
        methods = ['GET', 'POST']
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=None):
    if methods is None:
        methods = ['GET', 'POST']
    print('received my event: ' + str(json))
    if 'user_name' in json and json.get('message', ''):
        insert_mesage(json['user_name'], json['message'])
    if json.get('data', '') == 'User Connected':
        return redirect(url_for('chat_room'))
    socketio.emit('my response', json, callback=messageReceived)


@app.route('/chat', methods=['GET', 'POST'])
def chat_room():
    
    previous = get_all_messages()
    # print(previous.user_name'])
    return render_template('chat.html', past_messages=previous)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
