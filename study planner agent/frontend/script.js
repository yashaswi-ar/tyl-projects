let subjectCount = 0;
let additionalCount = 0;


// ============================================================
// ADD VTU SUBJECT
// ============================================================

function addSubject() {

    subjectCount++;

    const container =
        document.getElementById(
            "subjectsContainer"
        );

    const div =
        document.createElement("div");

    div.className = "dynamic-item";

    div.id =
        `subject-${subjectCount}`;

    div.innerHTML = `

        <div class="dynamic-header">

            <h3>
                Subject ${subjectCount}
            </h3>

            <button
                type="button"
                class="remove-button"
                onclick="removeElement('subject-${subjectCount}')">

                Remove

            </button>

        </div>


        <div class="dynamic-grid">

            <div class="form-group">

                <label>
                    Subject Name
                </label>

                <input
                    type="text"
                    class="subject-name"
                    placeholder="Computer Networks"
                >

            </div>


            <div class="form-group">

                <label>
                    Credits
                </label>

                <input
                    type="number"
                    class="subject-credits"
                    min="1"
                    max="10"
                    placeholder="4"
                >

            </div>


            <div class="form-group">

                <label>
                    Number of Modules
                </label>

                <input
                    type="number"
                    class="subject-modules"
                    min="0.5"
                    step="0.5"
                    placeholder="5"
                >

            </div>

        </div>


        <div class="form-group">

            <label>
                Modules Already Studied
            </label>

            <input
                type="text"
                class="subject-studied"
                placeholder="Example: 1,2 or none"
            >

            <small>
                Enter module numbers separated by commas.
            </small>

        </div>

    `;

    container.appendChild(div);
}


// ============================================================
// ADDITIONAL STUDY
// ============================================================

function addAdditionalStudy() {

    additionalCount++;

    const container =
        document.getElementById(
            "additionalContainer"
        );

    const div =
        document.createElement("div");

    div.className = "dynamic-item";

    div.id =
        `additional-${additionalCount}`;

    div.innerHTML = `

        <div class="dynamic-header">

            <h3>
                Additional Study ${additionalCount}
            </h3>

            <button
                type="button"
                class="remove-button"
                onclick="removeElement('additional-${additionalCount}')">

                Remove

            </button>

        </div>


        <div class="additional-grid">

            <div class="form-group">

                <label>
                    Name
                </label>

                <input
                    type="text"
                    class="additional-name"
                    placeholder="Aptitude"
                >

            </div>


            <div class="form-group">

                <label>
                    Topics
                </label>

                <input
                    type="text"
                    class="additional-topics"
                    placeholder="Percentage, Blood Relations"
                >

            </div>


            <div class="form-group">

                <label>
                    Difficulty
                </label>

                <select
                    class="additional-difficulty">

                    <option value="1">
                        1 - Easy
                    </option>

                    <option value="2">
                        2
                    </option>

                    <option value="3">
                        3
                    </option>

                    <option value="4">
                        4
                    </option>

                    <option value="5">
                        5 - Hard
                    </option>

                </select>

            </div>


            <div class="form-group">

                <label>
                    Target / Exam Date
                </label>

                <input
                    type="date"
                    class="additional-date"
                >

            </div>

        </div>

        <small>
            Leave the date empty if there is no fixed deadline.
        </small>

    `;

    container.appendChild(div);
}


// ============================================================
// REMOVE
// ============================================================

function removeElement(id) {

    const element =
        document.getElementById(id);

    if (element) {
        element.remove();
    }
}


// ============================================================
// COLLECT SUBJECTS
// ============================================================

function collectSubjects() {

    const elements =
        document.querySelectorAll(
            "#subjectsContainer .dynamic-item"
        );

    const subjects = [];

    elements.forEach(element => {

        const name =
            element
                .querySelector(".subject-name")
                .value
                .trim();

        const credits =
            element
                .querySelector(".subject-credits")
                .value;

        const modules =
            element
                .querySelector(".subject-modules")
                .value;

        const studied =
            element
                .querySelector(".subject-studied")
                .value
                .trim();


        if (!name) {
            throw new Error(
                "Please enter the subject name."
            );
        }


        if (!credits) {
            throw new Error(
                `Please enter credits for ${name}.`
            );
        }


        if (!modules) {
            throw new Error(
                `Please enter the number of modules for ${name}.`
            );
        }


        subjects.push({

            name: name,

            credits: Number(credits),

            modules: Number(modules),

            studied_modules:
                studied || "none"

        });

    });

    return subjects;
}


// ============================================================
// COLLECT ADDITIONAL STUDIES
// ============================================================

function collectAdditionalStudies() {

    const elements =
        document.querySelectorAll(
            "#additionalContainer .dynamic-item"
        );

    const studies = [];

    elements.forEach(element => {

        const name =
            element
                .querySelector(".additional-name")
                .value
                .trim();


        const topicText =
            element
                .querySelector(".additional-topics")
                .value
                .trim();


        const difficulty =
            element
                .querySelector(".additional-difficulty")
                .value;


        const targetDate =
            element
                .querySelector(".additional-date")
                .value;


        if (!name) {
            throw new Error(
                "Please enter the additional study name."
            );
        }


        const topics =
            topicText
                .split(",")
                .map(topic => topic.trim())
                .filter(topic => topic);


        studies.push({

            name: name,

            topics: topics.length
                ? topics
                : ["General preparation"],

            difficulty:
                Number(difficulty),

            target_date:
                targetDate || null

        });

    });

    return studies;
}


// ============================================================
// GENERATE PLAN
// ============================================================

async function generatePlan() {

    const errorBox =
        document.getElementById(
            "errorMessage"
        );

    errorBox.classList.remove("show");

    errorBox.textContent = "";


    try {

        const name =
            document
                .getElementById("name")
                .value
                .trim();


        const hours =
            document
                .getElementById("hoursPerDay")
                .value;


        const examDate =
            document
                .getElementById("examDate")
                .value;


        if (!name) {

            throw new Error(
                "Please enter your name."
            );

        }


        if (!hours || Number(hours) < 1) {

            throw new Error(
                "Study time must be at least 1 hour."
            );

        }


        const subjects =
            collectSubjects();


        if (subjects.length === 0) {

            throw new Error(
                "Please add at least one VTU subject."
            );

        }


        const additionalStudies =
            collectAdditionalStudies();


        const requestData = {

            name: name,

            hours_per_day:
                Number(hours),

            exam_date:
                examDate || null,

            subjects:
                subjects,

            additional_studies:
                additionalStudies

        };


        // Show loading
        const button =
            document.querySelector(
                ".generate-button"
            );

        button.disabled = true;

        button.innerHTML =
            "Generating Plan...";


        const response =
            await fetch(
                "/api/generate-plan",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            requestData
                        )
                }
            );


        const result =
            await response.json();


        if (!response.ok ||
            !result.success) {

            throw new Error(
                result.message ||
                "Unable to generate plan."
            );

        }


        displayResult(result);


    } catch (error) {

        errorBox.textContent =
            error.message;

        errorBox.classList.add(
            "show"
        );

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    } finally {

        const button =
            document.querySelector(
                ".generate-button"
            );

        button.disabled = false;

        button.innerHTML =
            'Generate Study Plan <span>→</span>';

    }
}


// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(result) {

    const resultSection =
        document.getElementById(
            "result"
        );

    resultSection.classList.remove(
        "hidden"
    );


    document.getElementById(
        "resultTitle"
    ).textContent =
        `${result.student.name}'s Study Plan`;


    let subtitle =
        `Starting ${result.plan_info.start_date}`;


    if (result.plan_info.exam_date) {

        subtitle +=
            ` • Target: ${result.plan_info.exam_date}`;

    }


    document.getElementById(
        "resultSubtitle"
    ).textContent =
        subtitle;


    displaySummary(result);

    displayDailyPlan(
        result.daily_plan
    );

    displayWeeklyGoals(
        result.weekly_goals
    );

    displayWarnings(
        result.leftovers
    );

    displayRules(
        result.rules
    );


    resultSection.scrollIntoView({
        behavior: "smooth"
    });
}


// ============================================================
// SUMMARY
// ============================================================

function displaySummary(result) {

    const container =
        document.getElementById(
            "summaryCards"
        );


    const totalDays =
        result.plan_info.days;


    let totalStudyHours = 0;


    result.daily_plan.forEach(day => {

        totalStudyHours +=
            day.total_hours;

    });


    container.innerHTML = `

        <div class="summary-card">

            <div class="value">
                ${totalDays}
            </div>

            <div class="label">
                Plan Days
            </div>

        </div>


        <div class="summary-card">

            <div class="value">
                ${result.student.hours_per_day}
            </div>

            <div class="label">
                Hours / Day
            </div>

        </div>


        <div class="summary-card">

            <div class="value">
                ${totalStudyHours.toFixed(1)}
            </div>

            <div class="label">
                Planned Study Hours
            </div>

        </div>

    `;
}


// ============================================================
// DAILY PLAN
// ============================================================

function displayDailyPlan(days) {

    const container =
        document.getElementById(
            "dailyPlan"
        );


    container.innerHTML = "";


    days.forEach(day => {

        const card =
            document.createElement(
                "div"
            );

        card.className =
            "day-card";


        let rows = "";


        if (day.items.length === 0) {

            rows = `
                <div class="study-row">

                    <div class="category">
                        -
                    </div>

                    <div class="study-name">
                        No study sessions
                    </div>

                    <div class="study-unit">
                        -
                    </div>

                    <div class="study-hours">
                        -
                    </div>

                </div>
            `;

        } else {

            day.items.forEach(item => {

                let categoryClass =
                    "category";


                if (
                    item.category === "VTU"
                ) {

                    categoryClass +=
                        " vtu";

                } else if (
                    item.category === "ADDITIONAL"
                ) {

                    categoryClass +=
                        " additional";

                } else {

                    categoryClass +=
                        " revision";

                }


                const hoursText =
                    item.hours > 0
                        ? `${item.hours.toFixed(1)} hr`
                        : "Revision";


                rows += `

                    <div class="study-row">

                        <div class="${categoryClass}">
                            ${escapeHtml(item.category)}
                        </div>

                        <div class="study-name">
                            ${escapeHtml(item.name)}
                        </div>

                        <div class="study-unit">
                            ${escapeHtml(item.unit)}
                        </div>

                        <div class="study-hours">
                            ${hoursText}
                        </div>

                    </div>

                `;

            });

        }


        card.innerHTML = `

            <div class="day-header">

                <h4>
                    ${day.date}
                </h4>

                <div class="day-total">
                    ${day.total_hours.toFixed(1)} hr
                </div>

            </div>

            ${rows}

        `;


        container.appendChild(card);

    });
}


// ============================================================
// WEEKLY GOALS
// ============================================================

function displayWeeklyGoals(weeks) {

    const container =
        document.getElementById(
            "weeklyGoals"
        );


    container.innerHTML = "";


    weeks.forEach(week => {

        const card =
            document.createElement(
                "div"
            );

        card.className =
            "week-card";


        let goals = "";


        week.goals.forEach(goal => {

            goals += `

                <div class="goal">

                    <div class="goal-name">
                        ${escapeHtml(
                            goal.name
                        )}
                    </div>

                    <div class="goal-text">
                        ${escapeHtml(
                            goal.goal
                        )}
                    </div>

                </div>

            `;

        });


        card.innerHTML = `

            <h4>
                Week ${week.week}
            </h4>

            <div class="week-dates">
                ${week.start} → ${week.end}
            </div>

            ${goals}

        `;


        container.appendChild(card);

    });
}


// ============================================================
// WARNINGS
// ============================================================

function displayWarnings(leftovers) {

    const block =
        document.getElementById(
            "warningBlock"
        );


    const container =
        document.getElementById(
            "warnings"
        );


    container.innerHTML = "";


    if (
        !leftovers ||
        leftovers.length === 0
    ) {

        block.classList.add(
            "hidden"
        );

        return;

    }


    block.classList.remove(
        "hidden"
    );


    leftovers.forEach(item => {

        const div =
            document.createElement(
                "div"
            );

        div.className =
            "warning-item";


        div.textContent =
            `${item.name}: ${item.items_left} item(s), ${item.hours_left} hr left`;


        container.appendChild(div);

    });
}


// ============================================================
// RULES
// ============================================================

function displayRules(rules) {

    const container =
        document.getElementById(
            "rules"
        );


    container.innerHTML = "";


    rules.forEach((rule, index) => {

        const div =
            document.createElement(
                "div"
            );

        div.className =
            "rule";


        div.textContent =
            `${index + 1}. ${rule}`;


        container.appendChild(div);

    });
}


// ============================================================
// HTML SAFETY
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text;

    return div.innerHTML;
}


// ============================================================
// START WITH ONE SUBJECT
// ============================================================

addSubject();