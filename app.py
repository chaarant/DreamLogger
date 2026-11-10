from flask import Flask, render_template, request, jsonify, session, redirect
import os
import psycopg2
from psycopg2.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dreamlogger-secret-key"


def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("index.html")


@app.route("/save-dream", methods=["POST"])
def save_dream():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO dreams (date, text, mood, theme, user_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            data["date"],
            data["text"],
            data["mood"],
            data["theme"],
            session["user_id"]
        )
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Dream saved successfully"})


@app.route("/dreams")
def get_dreams():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, date, text, mood, theme
        FROM dreams
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    dreams = []

    for row in rows:
        dreams.append({
            "id": row[0],
            "date": row[1],
            "text": row[2],
            "mood": row[3],
            "theme": row[4]
        })

    return jsonify(dreams)


@app.route("/delete-dream/<int:dream_id>", methods=["DELETE"])
def delete_dream(dream_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM dreams
        WHERE id = %s AND user_id = %s
        """,
        (dream_id, session["user_id"])
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Dream deleted successfully"})


@app.route("/edit-dream/<int:dream_id>", methods=["PUT"])
def edit_dream(dream_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE dreams
        SET text = %s, mood = %s, theme = %s
        WHERE id = %s AND user_id = %s
        """,
        (
            data["text"],
            data["mood"],
            data["theme"],
            dream_id,
            session["user_id"]
        )
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Dream updated successfully"})


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (username, password)
                VALUES (%s, %s)
                """,
                (username, hashed_password)
            )

            connection.commit()

            cursor.close()
            connection.close()

            return "Account created successfully!"

        except UniqueViolation:
            connection.rollback()

            cursor.close()
            connection.close()

            return "That username already exists."

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        return "Invalid username or password."

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
