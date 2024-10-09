import sqlite3
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request
from discordwebhook import Discord


app = Flask(__name__)


def get_db():
    conn = sqlite3.connect('discord.db')
    return conn


# ENDPOINT 1
@app.route('/', methods=['GET', 'POST'])
def get_input_messages():
    conn = get_db()
    cursor = conn.cursor()


    # Correctly create the table with a timestamp column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            email TEXT, 
            message TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Send message to Discord
        discord = Discord(
            url="https://discord.com/api/webhooks/1292420736962662400/f8aLo_5fz--G3N1bdRDl5PLZiyIAhUOem54Gp25rNo5hv-a_q5aaCRuubAKJjHqXx9Nn")
        discord.post(content=message)

        # Insert new data into the database
        cursor.execute("INSERT INTO users (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    conn.close()
    return render_template('users.html', users=rows)


# ENDPOINT 3
@app.route('/get_messages', methods=['GET'])
def get_messages():
    conn = get_db()
    conn.row_factory = sqlite3.Row  # This ensures rows are returned as dictionary-like objects
    cursor = conn.cursor()

    now = datetime.now(timezone.utc)
    thirty_minutes_ago = now - timedelta(minutes=30)

    # Use the correct column name for the timestamp
    cursor.execute("SELECT message FROM users WHERE timestamp >= ?", (thirty_minutes_ago,))
    messages = cursor.fetchall()

    formatted_messages = [row['message'] for row in messages]

    conn.close()

    if formatted_messages:
        discord_message_content = "\n".join([f"Message: {msg}" for msg in formatted_messages])

        print(f"Messages in the last 30 minutes: {discord_message_content}")

        # Send to Discord
        discord = Discord(
            url="https://discord.com/api/webhooks/1292420736962662400/f8aLo_5fz--G3N1bdRDl5PLZiyIAhUOem54Gp25rNo5hv-a_q5aaCRuubAKJjHqXx9Nn")
        discord.post(content=f"Messages in the last 30 minutes:\n{discord_message_content}")
    else:
        print("No messages were sent in the last 30 minutes.")

    return "Check the console for the messages."


if __name__ == '__main__':
    app.run()
