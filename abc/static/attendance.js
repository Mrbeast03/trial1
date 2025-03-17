document.addEventListener("DOMContentLoaded", function () {
    fetchAttendanceRecords();
    fetchTodayRecords();

    const mealYesBtn = document.getElementById("meal-yes");
    const mealNoBtn = document.getElementById("meal-no");
    const sendBtn = document.getElementById("send-btn");
    const weeklyReportBtn = document.getElementById("weekly-report-btn");
    const selectedMealSpan = document.getElementById("selected-meal");
    const mealButtons = document.querySelectorAll(".meal-section button");

    let mealChoice = null;
    
    if (mealYesBtn && mealNoBtn) {
        mealYesBtn.addEventListener("click", () => {
            mealChoice = "Yes";
            updateMealSelection("Yes");
        });
        mealNoBtn.addEventListener("click", () => {
            mealChoice = "No";
            updateMealSelection("No");
        });
    }
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMealData);
    }
    function updateMealSelection(choice) {
        mealChoice = choice;
        // selectedMealSpan.innerText = choice; // Update the span text
        updateTableWithMeal(new Date().toISOString().split("T")[0], choice); // Update the table

    }
    mealButtons.forEach(button => {
        button.addEventListener("click", function () {
            // Remove selected class from all meal buttons
            mealButtons.forEach(btn => btn.classList.remove("selected"));
            // Add selected class to clicked button
            this.classList.add("selected");
        });
    });

});

function fetchAttendanceRecords() {
    fetch('/fetch-attendance')
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                console.error("Unexpected data format:", data);
                data = [];
            }

            if (data.length === 0) {
                console.log("No attendance records found.");
            } else {
                localStorage.setItem("attendanceRecords", JSON.stringify(data));
            }
            updateAttendanceTable(data);
        })
        .catch(error => console.error('Error fetching attendance:', error));
}

function updateAttendanceTable(records) {
    let table = document.querySelector(".checkin-section table");
    table.innerHTML = `<tr><th>Date</th><th>Check-in</th><th>Check-out</th><th>Total Hours</th></tr>`;

    if (!Array.isArray(records)) return;

    records.forEach(record => {
        let checkin_time = record?.checkin ?? "Not Checked-in";
        let checkout_time = record?.checkout ?? "Not Checked-out";
        let totalHours = calculateTotalHours(checkin_time, checkout_time);
        // let mealSelection = record?.meal ?? "Not Selected";

        table.innerHTML += `
            <tr>
                <td>${record.date}</td>
                <td>${checkin_time}</td>
                <td>${checkout_time}</td>
                <td>${totalHours}</td>
                
            </tr>
        `;
    });
}

window.onload = function () {
    let savedData = localStorage.getItem("attendanceRecords");
    if (savedData) updateAttendanceTable(JSON.parse(savedData));
};

function calculateTotalHours(loginTime, logoutTime) {
    if (!loginTime || loginTime === "-" || loginTime === "null") return "Not Checked-in";
    if (!logoutTime || logoutTime === "-" || logoutTime === "null") return "Pending";

    let login = new Date(`1970-01-01T${loginTime}`);
    let logout = new Date(`1970-01-01T${logoutTime}`);

    if (isNaN(logout.getTime())) return "Pending";
    if (logout < login) return "Error in data";

    let diffMs = logout - login;
    let diffHrs = Math.floor(diffMs / 3600000);
    let diffMins = Math.floor((diffMs % 3600000) / 60000);

    return `${diffHrs} hrs ${diffMins} mins`;
}

function sendCheckIn() {
    fetch('/store-login-time', { method: 'POST' })
        .then(response => response.json())
        .then(data => data.message && fetchAttendanceRecords())
        .catch(error => console.error('Error:', error));
}

function sendCheckOut() {
    fetch('/store-logout-time', { method: 'POST' })
        .then(response => response.json())
        .then(data => data.message && fetchAttendanceRecords())
        .catch(error => console.error('Error:', error));
}

function sendAttendanceData() {
    const today = new Date().toISOString().split("T")[0];
    let selectedMealElement = document.getElementById("selected-meal");
    let mealChoice = selectedMealElement ? selectedMealElement.innerText : "Not Selected";

    const attendanceData = {
        date: today,
        meal: mealChoice,
        type: "pending",
        status: "pending"
    };

    fetch("/store-attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(attendanceData)
    })
    .then(response => response.json())
    .then(data => {
        alert("Attendance data submitted successfully!");
        fetchAttendanceRecords();
    })
    .catch(error => console.error("Error storing attendance:", error));
}

function updateTableWithMeal(date, mealChoice) {
    let table = document.querySelector(".attendance-section table");
    let existingRow = [...table.rows].find(row => row.cells[0]?.innerText === date);

    if (existingRow) {
        existingRow.cells[4].innerText = mealChoice; // Update meal column
    } else {
        table.innerHTML += `
            <tr>
                <td>${date}</td>
                <td>${mealChoice}</td>

                <td>pending</td>
                <td>pending</td>
                
            </tr>
        `;
    }
}

function convertTo24Hour(time12h) {
    if (!time12h || time12h === "-" || time12h === "null") return "00:00:00";

    let [time, modifier] = time12h.split(" ");
    let [hours, minutes] = time.split(":");

    if (modifier === "PM" && hours !== "12") hours = String(parseInt(hours, 10) + 12);
    else if (modifier === "AM" && hours === "12") hours = "00";

    return `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}:00`;
}

// function sendMealData() {
//     const mealChoice = document.querySelector(".meal-section button.selected");
//     if (!mealChoice) {
//         alert("Please select a meal option before sending.");
//         return;
//     }

//     fetch('/store-meal', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             meal: mealChoice.innerText
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.message) {
//             alert("Meal data stored successfully!");
//             fetchTodayRecords(); // Refresh the table after storing
//         } else {
//             alert("Error: " + data.error);
//         }
//     })
//     .catch(error => console.error('Error:', error));
// }
function sendMealData() {
    const mealChoice = document.querySelector(".meal-section button.selected");

    if (!mealChoice) {
        alert("Please select a meal option before sending.");
        return;
    }

    fetch('/store-meal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            meal: mealChoice.innerText.trim() // Trim spaces to prevent empty values
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Meal data stored successfully!");
            fetchTodayRecords(); // Refresh the table after storing
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}


function fetchTodayRecords() {
    fetch('/fetch-today-records')
    .then(response => response.json())
    .then(data => {
        let table = document.querySelector(".attendance-records table");
        table.innerHTML = `<tr><th>Date</th><th>Meal</th><th>Type</th><th>Status</th></tr>`;

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(record => {
                table.innerHTML += `
                    <tr>
                        <td>${record.date}</td>
                        <td>${record.meal}</td>
                        <td>${record.type}</td>
                        <td>${record.status}</td>
                    </tr>
                `;
            });
        } else {
            table.innerHTML += `<tr><td colspan="4">No records found for today.</td></tr>`;
        }
    })
    .catch(error => console.error('Error fetching today’s records:', error));
}