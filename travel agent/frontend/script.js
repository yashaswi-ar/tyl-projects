const BACKEND_URL = "http://127.0.0.1:5003";

let currentGoal = null;
let currentPlan = null;


async function createPlan() {

    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const days = document.getElementById("days").value;
    const budget = document.getElementById("budget").value;
    const preference = document.getElementById("preference").value;

    const result = document.getElementById("result");

    if (!source || !destination || !days || !budget) {
        result.innerHTML = `
            <div class="error">
                Please fill in all the required fields.
            </div>
        `;
        return;
    }

    result.innerHTML = "<p>Creating your travel plan...</p>";

    currentGoal = {
        source: source,
        destination: destination,
        days: days,
        budget: budget,
        preference: preference
    };

    try {

        const response = await fetch(`${BACKEND_URL}/plan`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(currentGoal)
        });

        const data = await response.json();

        if (!data.success) {

            result.innerHTML = `
                <div class="error">
                    ${data.message}
                </div>
            `;

            return;
        }

        currentPlan = data.plan;

        displayPlan(data.plan);

    } catch (error) {

        result.innerHTML = `
            <div class="error">
                Could not connect to the Travel Agent backend.
                <br><br>
                Make sure the Flask server is running on port 5003.
            </div>
        `;
    }
}


function displayPlan(plan) {

    const result = document.getElementById("result");

    result.innerHTML = `
        <div class="plan-card">

            <h2>Travel Plan</h2>

            <p>
                <strong>Transport:</strong>
                ${plan.transport.type}
            </p>

            <p>
                <strong>Travel Duration:</strong>
                ${plan.transport.duration}
            </p>

            <p>
                <strong>Hotel:</strong>
                ${plan.hotel.name}
            </p>

            <p>
                <strong>Hotel Type:</strong>
                ${plan.hotel.type}
            </p>

            <p>
                <strong>Weather:</strong>
                ${plan.weather}
            </p>

            <p>
                <strong>Transport Cost:</strong>
                ₹${plan.budget.transport}
            </p>

            <p>
                <strong>Hotel Cost:</strong>
                ₹${plan.budget.hotel}
            </p>

            <p>
                <strong>Total Cost:</strong>
                ₹${plan.budget.total}
            </p>

            <button class="approve-btn" onclick="approveBooking()">
                Approve Booking
            </button>

        </div>
    `;
}


async function approveBooking() {

    const result = document.getElementById("result");

    try {

        const response = await fetch(`${BACKEND_URL}/approve`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                goal: currentGoal,
                plan: currentPlan
            })
        });

        const data = await response.json();

        if (data.success) {

            result.innerHTML += `
                <div class="plan-card">
                    <h3>Booking Approved</h3>
                    <p>${data.message}</p>
                </div>
            `;

        } else {

            result.innerHTML += `
                <div class="error">
                    ${data.message}
                </div>
            `;
        }

    } catch (error) {

        result.innerHTML += `
            <div class="error">
                Could not connect to the backend.
            </div>
        `;
    }
}