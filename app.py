from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dreamlogger-secret-key"


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("index.html")


@app.route("/save-dream", methods=["POST"])
def save_dream():

    data = request.get_json()

    connection = sqlite3.connect("dreams.db")
    cursor = connection.cursor()

    cursor.execute(
    """
    INSERT INTO dreams (date, text, mood, theme, user_id)
    VALUES (?, ?, ?, ?, ?)
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
    connection.close()

    return jsonify({"message": "Dream saved successfully"})


@app.route("/dreams")
def get_dreams():

    connection = sqlite3.connect("dreams.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, date, text, mood, theme
    FROM dreams
    WHERE user_id = ?
    ORDER BY id DESC
""", (session["user_id"],))

    rows = cursor.fetchall()

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

    connection = sqlite3.connect("dreams.db")
    cursor = connection.cursor()

    cursor.execute(
    "DELETE FROM dreams WHERE id = ? AND user_id = ?",
    (dream_id, session["user_id"])
)

    connection.commit()
    connection.close()

    return jsonify({"message": "Dream deleted successfully"})
@app.route("/edit-dream/<int:dream_id>", methods=["PUT"])
def edit_dream(dream_id):

    data = request.get_json()

    connection = sqlite3.connect("dreams.db")
    cursor = connection.cursor()

    cursor.execute(
    """
    UPDATE dreams
    SET text = ?, mood = ?, theme = ?
    WHERE id = ? AND user_id = ?
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
    connection.close()

    return jsonify({"message": "Dream updated successfully"})
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = sqlite3.connect("dreams.db")
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (username, password)
                VALUES (?, ?)
                """,
                (username, hashed_password)
            )

            connection.commit()
            connection.close()

            return "Account created successfully!"

        except sqlite3.IntegrityError:

            connection.close()

            return "That username already exists."

    return render_template("signup.html")
@app.route("/login", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("dreams.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()

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
    