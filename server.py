from flask import Flask, render_template, request, redirect, url_for
import os
import db

app = Flask(__name__)

@app.before_request
def init_db_once():
    db.setup()
    with db.get_db_cursor(True) as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

@app.teardown_appcontext
def shutdown_session(exception=None):
    # Optional: only needed if you want to close the pool when the app stops
    # db.close_pool()
    pass

@app.route("/")
def index():
    with db.get_db_cursor() as cur:
        cur.execute("SELECT name, message FROM guests ORDER BY id ASC;")
        guests = cur.fetchall()  # list of DictRows
    return render_template("hello.html", guests=guests)

@app.route("/submit_guest", methods=["POST"])
def submit_guest():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not message:
        return "Name and message are required!", 400
    with db.get_db_cursor(True) as cur:
        cur.execute(
            "INSERT INTO guests (name, message) VALUES (%s, %s)",
            (name, message),
        )
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3333"))
    app.run(host="0.0.0.0", port=port, debug=True)

