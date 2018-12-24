# encoding: utf-8
"""
transactions
 
Created by Donzok on 17/06/2017.
Copyright (c) 2017 . All rights reserved.
"""

import sqlite3
from datetime import datetime


def connect():
    conn = sqlite3.connect('files/passcodes.db')

    return conn


def disconnect(conn):
    conn.commit()

    conn.close()


def init_db():
    conn = connect()

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS passcodes (passcode  text primary key, date text, user text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fully_redeemed_votes (id integer primary key autoincrement, msg_id text, user text)''')

    disconnect(conn)


def insert_passcode(passcode, user):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("insert into passcodes values(?, ?, ?)",
                   (passcode, datetime.now().isoformat(), user))

    disconnect(conn)


def check_user_voted(msg_id, user_id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM fully_redeemed_votes WHERE msg_id=? AND user=?", (msg_id, user_id))

    count = cursor.fetchone()[0]

    disconnect(conn)

    return count


def remove_vote(msg_id, user_id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM fully_redeemed_votes WHERE msg_id=? AND user=?",
                   (msg_id, user_id))

    disconnect(conn)


def add_vote(msg_id, user_id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("INSERT INTO fully_redeemed_votes (msg_id, user) values(?, ?)",
                   (msg_id, user_id))

    disconnect(conn)


def count_votes(msg_id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM fully_redeemed_votes WHERE msg_id=?", (msg_id,))

    count = cursor.fetchone()[0]

    disconnect(conn)

    return count


def check_passcode_exists(passcode):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("SELECT count(*) from passcodes where passcode=?", (passcode,))

    count = cursor.fetchone()[0]

    disconnect(conn)

    return count


def get_last_n_passcodes(limit):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("select * from (select * from passcodes order by date DESC limit ?) order by date ASC", (limit,))

    passcodes = cursor.fetchall()

    disconnect(conn)

    return passcodes