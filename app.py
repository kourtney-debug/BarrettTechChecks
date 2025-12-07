from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import csv
from io import StringIO
import os

app = Flask(__name__)
app.secret_key = "barretttechchecks-secret"

DB_PATH = "checkins.db"


def init_db():
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team TEXT NOT NULL,
            accomplishments TEXT,
            goals TEXT,
            challenges TEXT,
            tool_name TEXT,
            tool_description TEXT,
            tool_link TEXT,
            tool_rating TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        team = request.form["team"]
        accomplishments = request.form["accomplishments"]
        goals = request.form["goals"]
        challenges = request.form["challenges"]
        tool_name = request.form["tool_name"]
        tool_description = request.form["tool_description"]
        tool_link = request.form["tool_link"]
        tool_rating = request.form["tool_rating"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO checkins 
            (name, team, accomplishments, goals, challenges, 
             tool_name, tool_description, tool_link, tool_rating, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                team,
                accomplishments,
                goals,
                challenges,
                tool_name,
                tool_description,
                tool_link,
                tool_rating,
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM checkins ORDER BY datetime(created_at) DESC"
    )
    rows = c.fetchall()
    conn.close()
    return render_template("dashboard.html", entries=rows)


@app.route("/export")
def export():
    """Export all entries as CSV."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM checkins ORDER BY datetime(created_at) DESC"
    )
    rows = c.fetchall()
    conn.close()

    si = StringIO()
    writer = csv.writer(si)
    headers = [
        "ID",
        "Name",
        "Team/Department",
        "Weekly Accomplishments",
        "Goals for Upcoming Week",
        "Challenges/Blockers",
        "Tool/Tech Name",
        "Tool Description",
        "Tool Link",
        "Tool Rating",
        "Created At (UTC)",
    ]
    writer.writerow(headers)
    writer.writerows(rows)

    output = si.getvalue()
    si.close()

    return send_file(
        StringIO(output),
        mimetype="text/csv",
        as_attachment=True,
        download_name="barretttechchecks.csv",
    )


# 👇 This line makes sure the table is created BOTH locally and on Railway
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
