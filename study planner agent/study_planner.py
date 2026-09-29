"""
STUDY PLANNER AGENT - day-by-day plan for VTU subjects and extra studies (NPTEL, aptitude ...)

  * Every VTU subject and every additional study is a "group" with a last study day.
  * Every day each group earns an equal share of time (total hours / days left), so the
    work is spread EVENLY and the subjects ROTATE.
  * Groups WITH an exam date come first (nearest exam first). Groups with NO date come last
    and use the time that is left. Every session is at least 1 hour.
"""

from datetime import date, datetime, timedelta

DATE_FORMATS = ["%d-%m-%Y", "%d-%m-%y", "%d/%m/%Y", "%d/%m/%y", "%d%m%Y", "%d%m%y"]
SESSION = 1.0   # smallest study session (hours)


# ============================================================
# 1. SMALL HELPER FUNCTIONS
# ============================================================

def show_title(text):
    print()
    print("=" * 60)
    print(text.center(60))
    print("=" * 60)


def number_text(value):
    """2.0 -> '2' and 2.5 -> '2.5'"""
    if value == int(value):
        return str(int(value))
    return str(value)


def ask_whole_number(prompt, low, high):
    """Keep asking until the user types a whole number from low to high."""
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print("Please enter a whole number from", low, "to", high)


def ask_decimal(prompt, low):
    """Keep asking until the user types a number that is at least `low`."""
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")
            continue
        if value >= low:
            return value
        print("Please enter at least", low)


def read_date(prompt, today):
    """Ask for a date like 27-10-2026 (27-10-26 or 271026 also work).
    Typing 'none' gives None. Dates in the past are not accepted."""
    while True:
        text = input(prompt).strip().lower()
        if text == "none" or text == "":
            return None

        chosen = None
        for date_format in DATE_FORMATS:
            try:
                chosen = datetime.strptime(text, date_format).date()
                break
            except ValueError:
                pass

        if chosen is None:
            print("Invalid date. Use DD-MM-YYYY, or type none.")
        elif chosen < today:
            print("That date has already passed. Enter a future date, or type none.")
        else:
            return chosen


def hours_for_difficulty(difficulty):
    """Harder topics need more time (never below 1 hour)."""
    if difficulty <= 2:
        return 1.0
    if difficulty <= 4:
        return 1.5
    return 2.0


def print_table(headers, rows):
    """Print a table with borders. A row that is None draws a separator line."""
    widths = []
    for header in headers:
        widths.append(len(header))
    for row in rows:
        if row is not None:
            for i in range(len(row)):
                if len(row[i]) > widths[i]:
                    widths[i] = len(row[i])

    line = "+"
    for width in widths:
        line = line + "-" * (width + 2) + "+"

    print(line)
    print(table_row(headers, widths))
    print(line)
    for row in rows:
        if row is None:
            print(line)
        else:
            print(table_row(row, widths))
    print(line)


def table_row(cells, widths):
    text = "|"
    for i in range(len(cells)):
        text = text + " " + cells[i].ljust(widths[i]) + " |"
    return text


# ============================================================
# 2. READING THE USER'S INFORMATION
# ============================================================

def read_subjects(count):
    subjects = []
    for i in range(count):
        print("\nSubject", i + 1)
        name = input("Subject name: ").strip()
        credits = ask_whole_number("Credits: ", 1, 10)
        total_modules = ask_decimal("How many modules does this subject have? ", 0.5)
        studied_text = input("Modules already studied (example: 1,2 or none): ").strip().lower()

        studied = []
        if studied_text != "none" and studied_text != "":
            try:
                for part in studied_text.split(","):
                    studied.append(float(part))
            except ValueError:
                print("Invalid module input. Assuming no modules studied.")
                studied = []

        # Modules are 1, 2, 3 ... (a last half module like 2.5 is allowed)
        remaining = []
        number = 1.0
        while number <= total_modules:
            if number not in studied:
                remaining.append(number)
            number = number + 1
        if total_modules % 1 != 0 and total_modules not in studied:
            remaining.append(total_modules)

        subjects.append({
            "name": name,
            "credits": credits,
            "modules": total_modules,
            "remaining": remaining,
        })
    return subjects


def read_additional(today):
    studies = []
    answer = input("Do you have any additional studies/exams? (yes/no): ").strip().lower()
    if answer != "yes":
        return studies

    count = ask_whole_number("How many additional studies? ", 0, 20)
    for i in range(count):
        print("\nAdditional Study", i + 1)
        name = input("Name: ").strip()

        topics = []
        for topic in input("Topics (comma separated): ").split(","):
            if topic.strip() != "":
                topics.append(topic.strip())
        if len(topics) == 0:
            topics = ["General preparation"]

        difficulty = ask_whole_number("Difficulty (1-5): ", 1, 5)
        target = read_date("Target/exam date (DD-MM-YYYY or none): ", today)

        studies.append({
            "name": name,
            "topics": topics,
            "difficulty": difficulty,
            "date": target,
        })
    return studies


# ============================================================
# 3. BUILDING THE STUDY GROUPS
# ============================================================

def group_order(group):
    """Groups WITH an exam date first (nearest first). Groups without a date go last."""
    return (not group["dated"], group["last_day"], -group["level"])   # False sorts before True


def new_group(category, name, units, last_day, level, dated):
    """A group = a list of units (modules/topics) that share one deadline."""
    if last_day < 0:
        last_day = 0  # the date is very close, so study today

    total = 0.0
    for unit in units:
        total = total + unit["hours"]

    return {
        "category": category,
        "name": name,
        "units": units,                    # modules/topics still to study, in order
        "left": total,                     # hours still to study
        "last_day": last_day,              # day number (0 = today) of the last study day
        "rate": total / (last_day + 1),    # fair share of hours per day
        "credit": 0.0,                     # study time earned but not yet used
        "level": level,                    # credits / difficulty, used to break ties
        "dated": dated,                    # True if this group has an exam date
    }


def count_plan_days(today, exam_date, studies):
    """The plan runs until the day before the last exam (and at least one week)."""
    if exam_date is None:
        last = today + timedelta(days=6)
    else:
        last = exam_date - timedelta(days=1)

    for study in studies:
        if study["date"] is not None:
            revision_day = study["date"] - timedelta(days=1)
            if revision_day > last:
                last = revision_day

    days = (last - today).days + 1
    if days < 1:
        days = 1
    return days


def make_groups(subjects, studies, exam_date, today, plan_days):
    groups = []

    # Last study day for anything that follows the VTU exam.
    # VTU exam given: 3 days before it (the last 2 days are revision).
    # No VTU exam date: a weekly plan, spread over the whole plan.
    if exam_date is None:
        vtu_last_day = plan_days - 1
    else:
        vtu_last_day = (exam_date - today).days - 3

    # --- one group for every VTU subject (so the subjects rotate) ---
    for subject in subjects:
        hours = max(SESSION, subject["credits"] * 0.5)   # credits decide the workload (min 1 hr)
        units = []
        for module in subject["remaining"]:
            units.append({
                "name": subject["name"],
                "unit": "Module " + number_text(module),
                "hours": hours,
            })
        groups.append(new_group("VTU", subject["name"], units, vtu_last_day,
                                subject["credits"], exam_date is not None))

    # --- one group for every additional study ---
    for study in studies:
        hours = hours_for_difficulty(study["difficulty"])
        units = []
        for topic in study["topics"]:
            units.append({"name": study["name"], "unit": topic, "hours": hours})

        if study["date"] is None:
            last_day = vtu_last_day                       # no date: weekly plan, last priority
        else:
            last_day = (study["date"] - today).days - 2   # 1 day before is revision
        groups.append(new_group("ADDITIONAL", study["name"], units, last_day,
                                study["difficulty"], study["date"] is not None))

    # Keep only groups that have work, then sort them by priority.
    active = []
    for group in groups:
        if group["left"] > 0:
            active.append(group)
    active.sort(key=group_order)
    return active


# ============================================================
# 4. THE SCHEDULER
# ============================================================

def take_hours(group, hours, limit, items):
    """Take about `hours` from the group's first units and add them to today's list.
    A module/topic is not cut into pieces smaller than 1 hr (a leftover half hour is
    added to the last piece). Returns the hours really taken (never more than `limit`)."""
    taken = 0.0
    while hours > 0 and len(group["units"]) > 0:
        unit = group["units"][0]

        used = hours
        if unit["hours"] - used < SESSION:
            used = unit["hours"]              # finish the unit, do not leave a tiny piece
        if used > limit - taken:
            used = limit - taken              # today's hours are full
        if used <= 0:
            break

        items.append({
            "category": group["category"],
            "name": unit["name"],
            "unit": unit["unit"],
            "hours": used,
        })

        unit["hours"] = unit["hours"] - used
        group["left"] = group["left"] - used
        taken = taken + used
        hours = hours - used

        if unit["hours"] <= 0:
            group["units"].pop(0)             # this module/topic is finished
    return taken


def todays_order(group):
    """Groups with an exam date first, nearest date first.
    For the same date, the group that is most behind its share goes first."""
    return (not group["dated"], group["last_day"], -group["credit"])


def make_schedule(groups, plan_days, hours_per_day):
    """Returns a list with one entry per day. Each entry is a list of study items."""
    daily_limit = int(hours_per_day / 0.5) * 0.5   # never go above the entered hours
    plan = []

    # Staggered start: the first group can study today, the next one a little later, and so on.
    # This is what makes the subjects take turns instead of all starting on the same day.
    # (The daily rate is added again in the day loop below.)
    for number, group in enumerate(groups):
        share = (len(groups) - number) / len(groups)
        group["credit"] = SESSION * share - group["rate"]

    for day_number in range(plan_days):
        items = []
        free = daily_limit

        # Today's fair share is added to every group's "credit".
        for group in groups:
            if group["left"] > 0 and day_number <= group["last_day"]:
                group["credit"] = group["credit"] + group["rate"]

        for group in sorted(groups, key=todays_order):
            if group["left"] <= 0 or day_number > group["last_day"]:
                continue

            if day_number == group["last_day"]:
                hours = group["left"]                              # last day: finish everything
            else:
                hours = int(group["credit"] / SESSION) * SESSION   # whole 1-hour sessions only

            if hours > group["left"]:
                hours = group["left"]
            if hours > free:
                hours = int(free / SESSION) * SESSION              # the day is nearly full

            if hours > 0:
                taken = take_hours(group, hours, free, items)
                group["credit"] = group["credit"] - taken
                free = free - taken

        # If nothing was planned today but work is left, do not waste the day:
        # study one session of the group that is furthest behind its share.
        if len(items) == 0:
            behind = None
            for group in groups:
                if group["left"] > 0 and day_number <= group["last_day"]:
                    if behind is None or group["credit"] > behind["credit"]:
                        behind = group
            if behind is not None:
                taken = take_hours(behind, SESSION, free, items)
                behind["credit"] = behind["credit"] - taken

        plan.append(items)
    return plan


# ============================================================
# 5. SHOWING THE RESULT
# ============================================================

def show_plan(plan, today, subjects, vtu_revision, extra_revision):
    # Subjects with the same number of modules are revised together.
    revision_rows = []
    counts = []
    for subject in subjects:
        if subject["modules"] not in counts:
            counts.append(subject["modules"])
    for count in counts:
        names = []
        for subject in subjects:
            if subject["modules"] == count:
                names.append(subject["name"])
        revision_rows.append([", ".join(names), "Modules 1 to " + number_text(count)])

    rows = []
    for day_number in range(len(plan)):
        day = today + timedelta(days=day_number)
        day_rows = []
        total = 0.0

        for category in ("VTU", "ADDITIONAL"):
            for item in plan[day_number]:
                if item["category"] == category:
                    day_rows.append([category, item["name"], item["unit"], f"{item['hours']:.1f}"])
                    total = total + item["hours"]

        if day in vtu_revision:
            for names, modules in revision_rows:
                day_rows.append(["VTU REVISION", names, modules, "-"])
        if day in extra_revision:
            for name in extra_revision[day]:
                day_rows.append(["ADDITIONAL REVISION", name, "All topics", "-"])
        if len(day_rows) == 0:
            day_rows.append(["-", "No study sessions", "-", "-"])

        # Put the date and the total in the same table
        first_row = True
        for cells in day_rows:
            if first_row:
                rows.append([day.strftime("%d-%m-%Y")] + cells)
                first_row = False
            else:
                rows.append([""] + cells)
        rows.append(["", "", "TOTAL", "", f"{total:.1f}"])
        rows.append(None)

    rows.pop()   # no separator after the last day
    print_table(["Date", "Type", "Subject / Study", "Module / Topic", "Hours"], rows)


def show_leftovers(groups):
    left = []
    for group in groups:
        if group["left"] > 0:
            left.append(group)
    if len(left) == 0:
        return

    show_title("WARNING: NOT ENOUGH TIME")
    print("These could not fit. Study more hours per day or move the dates:")
    for group in left:
        print(f"  • {group['name']}: {len(group['units'])} item(s), {group['left']:.1f} hr left")


def show_weekly_goals(plan, today, vtu_revision, extra_revision):
    """One block of goals for every week of the plan (7 days each)."""
    show_title("WEEKLY GOALS")

    rows = []
    weeks = (len(plan) + 6) // 7
    for week in range(weeks):
        start = week * 7
        end = min(start + 7, len(plan))
        first_day = today + timedelta(days=start)
        last_day = today + timedelta(days=end - 1)
        dates = first_day.strftime("%d-%m") + " to " + last_day.strftime("%d-%m")

        # what is studied in this week, subject by subject
        names = []
        units_by_name = {}
        for items in plan[start:end]:
            for item in items:
                if item["name"] not in units_by_name:
                    names.append(item["name"])
                    units_by_name[item["name"]] = []
                if item["unit"] not in units_by_name[item["name"]]:
                    units_by_name[item["name"]].append(item["unit"])

        week_rows = []
        for name in names:
            week_rows.append([name, ", ".join(units_by_name[name])])

        # revision days that fall in this week
        vtu_days = []
        for offset in range(start, end):
            day = today + timedelta(days=offset)
            if day in vtu_revision:
                vtu_days.append(day.strftime("%d-%m"))
            if day in extra_revision:
                for name in extra_revision[day]:
                    week_rows.append([name + " (revision)", "All topics on " + day.strftime("%d-%m")])
        if len(vtu_days) > 0:
            week_rows.append(["VTU (revision)", "All modules on " + " and ".join(vtu_days)])

        if len(week_rows) == 0:
            week_rows.append(["-", "Nothing new to study"])

        first_row = True
        for cells in week_rows:
            if first_row:
                rows.append(["Week " + str(week + 1), dates] + cells)
                first_row = False
            else:
                rows.append(["", ""] + cells)
        rows.append(None)

    rows.pop()
    print_table(["Week", "Dates", "Subject / Study", "Goal for the week"], rows)


def show_rules():
    show_title("PRIORITY SYSTEM USED")
    rules = [
        "Groups WITH an exam date come first, nearest exam first. Groups with NO date use the time left.",
        "Each group gets an equal share of time every day until its own date, so study is spread evenly.",
        "Every VTU subject has its own share, so subjects rotate. Hours per module = credits x 0.5 (min 1 hr).",
        "Additional studies: difficulty sets hours per topic (1-2 = 1 hr, 3-4 = 1.5 hr, 5 = 2 hr).",
        "Every session is at least 1 hr. Your daily hours are never exceeded.",
        "VTU study ends 3 days before the exam, then 2 revision days. Each dated additional study gets 1 revision day.",
    ]
    for number, rule in enumerate(rules, start=1):
        print(f"\n{number}. {rule}")


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

def main():
    today = date.today()

    show_title("WELCOME TO STUDY PLANNER AGENT")
    print("\nHi! I'm your Study Planner Agent.")
    print("\nLet's start!")

    show_title("STUDENT INFORMATION")
    name = input("What is your name? ").strip()
    hours_per_day = ask_decimal("How many hours can you study per day? ", 1)
    subject_count = ask_whole_number("How many VTU subjects do you have? ", 0, 20)

    show_title("VTU EXAM / TARGET DATE")
    exam_date = read_date("VTU exam/target date if any (DD-MM-YYYY or none): ", today)

    subjects = read_subjects(subject_count)

    show_title("ADDITIONAL STUDIES")
    studies = read_additional(today)

    show_title("STUDY ANALYSIS")
    for subject in subjects:
        print(subject["name"], "-", len(subject["remaining"]), "modules remaining")

    plan_days = count_plan_days(today, exam_date, studies)
    groups = make_groups(subjects, studies, exam_date, today, plan_days)
    plan = make_schedule(groups, plan_days, hours_per_day)

    # Revision days
    vtu_revision = []
    if exam_date is not None:
        vtu_revision = [exam_date - timedelta(days=2), exam_date - timedelta(days=1)]

    extra_revision = {}
    for study in studies:
        if study["date"] is not None:
            day = study["date"] - timedelta(days=1)
            if day not in extra_revision:
                extra_revision[day] = []
            extra_revision[day].append(study["name"])

    if exam_date is None:
        show_title("DEADLINE-AWARE WEEKLY PLAN")
    else:
        show_title("DEADLINE-AWARE EXAM PLAN")

    show_plan(plan, today, subjects, vtu_revision, extra_revision)
    show_leftovers(groups)
    show_weekly_goals(plan, today, vtu_revision, extra_revision)
    show_rules()

    show_title("PLAN COMPLETE")
    print(f"\nAll the best, {name}! Stay consistent with your study plan.")


if __name__ == "__main__":
    main()