from flask import Flask, render_template, request, send_file
import csv, os
from datetime import datetime

APP_TITLE = "Scholarship Eligibility Checker"
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "eligible_students.csv")

BRANCHES = ["CSE"]
SECTIONS = ["A", "B", "C"]

app = Flask(__name__)

CSV_HEADERS = ["Timestamp","Name","Roll No","College","Year of Study","Branch","Section","Percentage","Income (INR)","Status"]

def ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def validate_inputs(name, rollno, college, year, branch, section, percentage, income):
    errors = []
    if not name.strip(): errors.append("Name required.")
    if not rollno.strip(): errors.append("Roll No required.")
    if not college.strip(): errors.append("College required.")
    if branch not in BRANCHES: errors.append("Invalid branch.")
    if section not in SECTIONS: errors.append("Invalid section.")
    try: pct = float(percentage)
    except: pct = None; errors.append("Percentage must be a number.")
    try: inc = int(income)
    except: inc = None; errors.append("Income must be an integer.")
    return errors, pct, inc

def is_eligible(percentage, income):
    return percentage >= 65 and income <= 500000

def append_to_csv(row):
    ensure_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         row["name"], row["rollno"], row["college"], row["year"],
                         row["branch"], row["section"], row["percentage"], row["income"],
                         "Eligible for Scholarship"])

def read_csv(branch=None, section=None):
    ensure_csv()
    rows = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if branch and r["Branch"] != branch: continue
            if section and r["Section"] != section: continue
            rows.append(r)
    return rows

@app.route("/", methods=["GET","POST"])
def index():
    context = {"title": APP_TITLE, "branches": BRANCHES, "sections": SECTIONS, "errors": [], "prefill": {}}
    if request.method=="POST":
        name = request.form.get("name","")
        rollno = request.form.get("rollno","")
        college = request.form.get("college","")
        year = request.form.get("year_of_study","")
        branch = request.form.get("branch","")
        section = request.form.get("section","")
        percentage = request.form.get("percentage","")
        income = request.form.get("income","")

        errors, pct, inc = validate_inputs(name, rollno, college, year, branch, section, percentage, income)
        if errors:
            context["errors"] = errors
            context["prefill"] = {"name":name,"rollno":rollno,"college":college,"year_of_study":year,"branch":branch,"section":section,"percentage":percentage,"income":income}
            return render_template("index.html", **context)

        decision = "Eligible for Scholarship" if is_eligible(pct, inc) else "Not Eligible for Scholarship"
        if "Eligible" in decision:
            append_to_csv({"name":name,"rollno":rollno,"college":college,"year":year,"branch":branch,"section":section,"percentage":pct,"income":inc})

        return render_template("result.html", title=APP_TITLE, decision=decision, data={"name":name,"rollno":rollno,"college":college,"year_of_study":year,"branch":branch,"section":section,"percentage":pct,"income":inc})
    return render_template("index.html", **context)

@app.route("/reports")
def reports():
    branch = request.args.get("branch","CSE")
    section = request.args.get("section","")
    rows = read_csv(branch, section) if branch and section else []
    return render_template("report.html", title=APP_TITLE, branches=BRANCHES, sections=SECTIONS, current_branch=branch, current_section=section, rows=rows)

@app.route("/download")
def download_csv():
    ensure_csv()
    return send_file(CSV_PATH, as_attachment=True)

if __name__ == "__main__":
    ensure_csv()
    app.run(debug=True)