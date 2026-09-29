from flask import Flask, request, jsonify, send_from_directory
from datetime import date, datetime, timedelta
import sys
import os

# Allow Python to find study_planner.py in the main project folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import study_planner


app = Flask(
    __name__,
    static_folder=os.path.join(PROJECT_ROOT, "frontend"),
    static_url_path=""
)


# ============================================================
# DATE HELPER
# ============================================================

def parse_date(value):
    if not value or str(value).lower() == "none":
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            pass

    raise ValueError("Invalid date format.")


# ============================================================
# BUILD VTU SUBJECT
# Same remaining-module logic as study_planner.py
# ============================================================

def build_subject(name, credits, total_modules, studied_text):

    studied = []

    if studied_text:
        if str(studied_text).lower() != "none":
            try:
                for part in str(studied_text).split(","):
                    studied.append(float(part.strip()))
            except ValueError:
                studied = []

    remaining = []

    number = 1.0

    while number <= total_modules:
        if number not in studied:
            remaining.append(number)

        number = number + 1

    if total_modules % 1 != 0 and total_modules not in studied:
        remaining.append(total_modules)

    return {
        "name": name,
        "credits": credits,
        "modules": total_modules,
        "remaining": remaining
    }


# ============================================================
# BUILD ADDITIONAL STUDY
# ============================================================

def build_additional(name, topics, difficulty, target_date):

    return {
        "name": name,
        "topics": topics,
        "difficulty": difficulty,
        "date": target_date
    }


# ============================================================
# NUMBER DISPLAY
# ============================================================

def number_text(value):

    if value == int(value):
        return str(int(value))

    return str(value)


# ============================================================
# GENERATE WEEKLY GOALS
# Same idea as study_planner.py
# ============================================================

def build_weekly_goals(
    plan,
    today,
    vtu_revision,
    extra_revision
):

    weeks = (len(plan) + 6) // 7

    all_weeks = []

    for week in range(weeks):

        start = week * 7
        end = min(start + 7, len(plan))

        first_day = today + timedelta(days=start)
        last_day = today + timedelta(days=end - 1)

        goals = []

        units_by_name = {}

        for items in plan[start:end]:

            for item in items:

                name = item["name"]

                if name not in units_by_name:
                    units_by_name[name] = []

                if item["unit"] not in units_by_name[name]:
                    units_by_name[name].append(item["unit"])

        for name, units in units_by_name.items():

            goals.append({
                "name": name,
                "goal": ", ".join(units)
            })

        # Additional revision
        for offset in range(start, end):

            current_day = today + timedelta(days=offset)

            if current_day in extra_revision:

                for name in extra_revision[current_day]:

                    goals.append({
                        "name": name,
                        "goal": (
                            "Revision - All topics on "
                            + current_day.strftime("%d-%m")
                        )
                    })

        # VTU revision
        vtu_days = []

        for offset in range(start, end):

            current_day = today + timedelta(days=offset)

            if current_day in vtu_revision:

                vtu_days.append(
                    current_day.strftime("%d-%m")
                )

        if vtu_days:

            goals.append({
                "name": "VTU Revision",
                "goal": (
                    "All modules on "
                    + " and ".join(vtu_days)
                )
            })

        if not goals:

            goals.append({
                "name": "No study sessions",
                "goal": "Nothing new to study"
            })

        all_weeks.append({
            "week": week + 1,
            "start": first_day.strftime("%d-%m-%Y"),
            "end": last_day.strftime("%d-%m-%Y"),
            "goals": goals
        })

    return all_weeks


# ============================================================
# MAIN PLANNER API
# ============================================================

@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        # ----------------------------------------------------
        # BASIC INFORMATION
        # ----------------------------------------------------

        name = str(data.get("name", "")).strip()

        if not name:
            return jsonify({
                "success": False,
                "message": "Please enter your name."
            }), 400

        hours_per_day = float(
            data.get("hours_per_day", 0)
        )

        if hours_per_day < 1:
            return jsonify({
                "success": False,
                "message": "Study time must be at least 1 hour."
            }), 400

        today = date.today()

        # ----------------------------------------------------
        # VTU EXAM DATE
        # ----------------------------------------------------

        exam_date = parse_date(
            data.get("exam_date")
        )

        # ----------------------------------------------------
        # VTU SUBJECTS
        # ----------------------------------------------------

        subjects = []

        for subject_data in data.get("subjects", []):

            subject_name = str(
                subject_data.get("name", "")
            ).strip()

            credits = int(
                subject_data.get("credits", 0)
            )

            modules = float(
                subject_data.get("modules", 0)
            )

            studied = str(
                subject_data.get(
                    "studied_modules",
                    "none"
                )
            ).strip()

            if not subject_name:
                continue

            if credits < 1:
                raise ValueError(
                    f"Invalid credits for {subject_name}."
                )

            if modules < 0.5:
                raise ValueError(
                    f"Invalid module count for {subject_name}."
                )

            subject = build_subject(
                subject_name,
                credits,
                modules,
                studied
            )

            subjects.append(subject)

        # ----------------------------------------------------
        # ADDITIONAL STUDIES
        # ----------------------------------------------------

        studies = []

        for study_data in data.get(
            "additional_studies",
            []
        ):

            study_name = str(
                study_data.get("name", "")
            ).strip()

            topics = study_data.get(
                "topics",
                []
            )

            difficulty = int(
                study_data.get(
                    "difficulty",
                    1
                )
            )

            target_date = parse_date(
                study_data.get("target_date")
            )

            if not study_name:
                continue

            if not isinstance(topics, list):
                topics = []

            topics = [
                str(topic).strip()
                for topic in topics
                if str(topic).strip()
            ]

            if not topics:
                topics = [
                    "General preparation"
                ]

            if difficulty < 1 or difficulty > 5:
                raise ValueError(
                    f"Difficulty for {study_name} must be 1-5."
                )

            study = build_additional(
                study_name,
                topics,
                difficulty,
                target_date
            )

            studies.append(study)

        # ----------------------------------------------------
        # USE YOUR EXISTING PLANNER LOGIC
        # ----------------------------------------------------

        plan_days = study_planner.count_plan_days(
            today,
            exam_date,
            studies
        )

        groups = study_planner.make_groups(
            subjects,
            studies,
            exam_date,
            today,
            plan_days
        )

        plan = study_planner.make_schedule(
            groups,
            plan_days,
            hours_per_day
        )

        # ----------------------------------------------------
        # VTU REVISION
        # ----------------------------------------------------

        vtu_revision = []

        if exam_date is not None:

            vtu_revision = [
                exam_date - timedelta(days=2),
                exam_date - timedelta(days=1)
            ]

        # ----------------------------------------------------
        # ADDITIONAL REVISION
        # ----------------------------------------------------

        extra_revision = {}

        for study in studies:

            if study["date"] is not None:

                revision_day = (
                    study["date"]
                    - timedelta(days=1)
                )

                if revision_day not in extra_revision:
                    extra_revision[revision_day] = []

                extra_revision[
                    revision_day
                ].append(study["name"])

        # ----------------------------------------------------
        # FORMAT DAILY PLAN FOR FRONTEND
        # ----------------------------------------------------

        daily_plan = []

        for day_number in range(plan_days):

            current_day = (
                today
                + timedelta(days=day_number)
            )

            items = []

            total_hours = 0.0

            # Normal study sessions
            for item in plan[day_number]:

                items.append({
                    "category": item["category"],
                    "name": item["name"],
                    "unit": item["unit"],
                    "hours": round(
                        item["hours"],
                        1
                    )
                })

                total_hours += item["hours"]

            # VTU revision
            if current_day in vtu_revision:

                revision_groups = {}

                for subject in subjects:

                    module_count = number_text(
                        subject["modules"]
                    )

                    if module_count not in revision_groups:
                        revision_groups[
                            module_count
                        ] = []

                    revision_groups[
                        module_count
                    ].append(
                        subject["name"]
                    )

                for module_count, names in revision_groups.items():

                    items.append({
                        "category": "VTU REVISION",
                        "name": ", ".join(names),
                        "unit": (
                            "Modules 1 to "
                            + module_count
                        ),
                        "hours": 0
                    })

            # Additional revision
            if current_day in extra_revision:

                for study_name in extra_revision[
                    current_day
                ]:

                    items.append({
                        "category": "ADDITIONAL REVISION",
                        "name": study_name,
                        "unit": "All topics",
                        "hours": 0
                    })

            daily_plan.append({
                "date": current_day.strftime(
                    "%d-%m-%Y"
                ),
                "items": items,
                "total_hours": round(
                    total_hours,
                    1
                )
            })

        # ----------------------------------------------------
        # LEFTOVERS / WARNING
        # ----------------------------------------------------

        leftovers = []

        for group in groups:

            if group["left"] > 0:

                leftovers.append({
                    "name": group["name"],
                    "items_left": len(
                        group["units"]
                    ),
                    "hours_left": round(
                        group["left"],
                        1
                    )
                })

        # ----------------------------------------------------
        # WEEKLY GOALS
        # ----------------------------------------------------

        weekly_goals = build_weekly_goals(
            plan,
            today,
            vtu_revision,
            extra_revision
        )

        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "student": {
                "name": name,
                "hours_per_day": hours_per_day
            },

            "plan_info": {
                "start_date": today.strftime(
                    "%d-%m-%Y"
                ),
                "days": plan_days,
                "exam_date": (
                    exam_date.strftime("%d-%m-%Y")
                    if exam_date
                    else None
                )
            },

            "daily_plan": daily_plan,

            "weekly_goals": weekly_goals,

            "leftovers": leftovers,

            "rules": [
                "Groups with an exam date come first, nearest exam first.",
                "Groups without a date use the time left.",
                "VTU subjects rotate according to their workload and credits.",
                "Hours per VTU module = credits × 0.5, with a minimum of 1 hour.",
                "Additional study time depends on difficulty.",
                "Every study session is at least 1 hour.",
                "VTU study ends 3 days before the exam.",
                "The final 2 VTU days are revision days.",
                "Each dated additional study gets a revision day."
            ]

        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# SERVE FRONTEND
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        app.static_folder,
        "index.html"
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=5001, debug=True)