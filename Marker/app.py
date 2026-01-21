from flask import Flask, render_template, request, redirect, session
import json
import zipfile
from flask import send_file
import os

app = Flask(__name__)
app.secret_key = "secret"

STUDENTS_FILE = "data/students.json"
CRITERIA_FILE = "data/criteria.json"
GRADES_FILE = "data/grades.json"

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/student/<int:student_id>/")
def login(student_id):
    session["student"] = student_id
    return redirect("/student/")


@app.route("/student/", methods=["GET", "POST"])
def student_page():
    student_id = session.get("student")
    if not student_id:
        return "Вы не вошли как студент"

    criteria = load(CRITERIA_FILE, [])
    active = load("data/active_target.json", {"target_student": None})
    target = active["target_student"]

    if not target:
        return "Сейчас оценивание не активно"

    if target == student_id:
        return "Вы не можете оценивать сами себя"

    if request.method == "POST":
        grades = load(GRADES_FILE, [])

        for c in criteria:
            value = request.form.get(f"criterion_{c['id']}")
            if value:
                grades.append({
                    "from": student_id,
                    "to": target,
                    "criterion": c["id"],
                    "value": int(value)
                })

        save(GRADES_FILE, grades)
        return "Оценка сохранена"

    return render_template(
        "student.html",
        student_id=student_id,
        criteria=criteria,
        target=target
    )

@app.route("/admin/download/")
def download_data():
    zip_path = "data/grades_backup.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir("data"):
            if filename.endswith(".json"):
                zipf.write(
                    f"data/{filename}",
                    arcname=filename
                )

    return send_file(
        zip_path,
        as_attachment=True,
        download_name="grades_data.zip"
    )




@app.route("/criteria/", methods=["GET", "POST"])
def criteria_page():
    criteria = load(CRITERIA_FILE, [])

    if request.method == "POST":
        name = request.form["name"]
        new_id = max([c["id"] for c in criteria], default=0) + 1
        criteria.append({"id": new_id, "name": name})
        save(CRITERIA_FILE, criteria)

    return render_template("criteria.html", criteria=criteria)

@app.route("/admin/", methods=["GET", "POST"])
def admin_page():
    students = load(STUDENTS_FILE, [])
    active = load("data/active_target.json", {"target_student": None})

    if request.method == "POST":
        value = request.form.get("target")
        active["target_student"] = int(value) if value else None
        save("data/active_target.json", active)

    return render_template(
        "admin.html",
        students=students,
        active=active["target_student"]
    )


if __name__ == "__main__":
    app.run(debug=True)
