// document.getElementById("invoiceForm").addEventListener("submit", function (event) {
//     event.preventDefault(); // Prevent form from reloading the page

//     let fileInput = document.getElementById("upload-file");
//     let empIdInput = document.getElementById("emp_id");

//     if (fileInput.files.length === 0) {
//         alert("Please select a file to upload.");
//         return;
//     }

//     // if (!empIdInput.value.trim()) {
//     //     alert("Please enter an Employee ID.");
//     //     return;
//     // }

//     let formData = new FormData();
//     formData.append("invoice_doc", fileInput.files[0]);
//     // formData.append("emp_id", empIdInput.value);

//     fetch("/upload_invoice", {
//         method: "POST",
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.message) {
//             alert(data.message);
//             addInvoiceToTable(data.date, data.month, data.year, data.file_path);
//             fileInput.value = ""; // Reset file input
//             // empIdInput.value = ""; // Reset employee ID input
//         } else {
//             alert("Error: " + data.error);
//         }
//     })
//     .catch(error => console.error("Error:", error));
// });

// function addInvoiceToTable(date, month, year, filePath) {
//     let table = document.getElementById("invoiceTable").getElementsByTagName("tbody")[0];
//     let newRow = table.insertRow(0);

//     newRow.innerHTML = `
//         <td>${date}</td>
//         <td>${month}</td>
//         <td>${year}</td>
//         <td><a href="${filePath}" target="_blank">View Document</a></td>
//     `;
// }

// function getMonthName(month) {
//     const monthNames = ["January", "February", "March", "April", "May", "June",
//         "July", "August", "September", "October", "November", "December"
//     ];
//     return monthNames[month - 1]; // Month in database is 1-12
// }

// function downloadSampleInvoice() {
//     const sampleInvoiceURL = "{{ url_for('static', filename='uploads/SAMPLE_INVOICE.docx') }}";
//     const link = document.createElement("a");
//     link.href = sampleInvoiceURL;
//     link.download = "SAMPLE_INVOICE.docx";  // Ensures the file is downloaded instead of opened
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);

//     // window.open(sampleInvoiceURL, '_blank');
// }

// function filterInvoices() {
//     const startDate = document.getElementById('filter-start-date').value;
//     const endDate = document.getElementById('filter-end-date').value;
//     const rows = document.querySelectorAll('#invoiceTable tbody tr');

//     rows.forEach(row => {
//         const dateCell = row.cells[0].textContent; // Get the date from the first column
//         const invoiceDate = new Date(dateCell);
//         let showRow = true;

//         if (startDate && new Date(startDate) > invoiceDate) {
//             showRow = false;
//         }
//         if (endDate && new Date(endDate) < invoiceDate) {
//             showRow = false;
//         }

//         row.style.display = showRow ? '' : 'none';
//     });
// }

// // Fetch invoices on page load
// window.onload = function() {
//     fetch('/get_invoices')
//         .then(response => response.json())
//         .then(invoices => {
//             invoices.forEach(invoice => {
//                 addInvoiceToTable(invoice.date, getMonthName(invoice.month), invoice.year, invoice.file_path);
//             });
//         })
//         .catch(error => console.error('Error fetching invoices:', error));
// };

document.getElementById("invoiceForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent page reload

    let fileInput = document.getElementById("upload-file");

    if (fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }

    let formData = new FormData();
    formData.append("invoice_doc", fileInput.files[0]);

    fetch("/upload_invoice", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            addInvoiceToTable(data.date, data.month, data.year, data.time, data.file_path);
            fileInput.value = ""; // Reset file input
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error("Error:", error));
});

// Function to add invoice to the table
function addInvoiceToTable(date, month, year, time, filePath) {
    let table = document.getElementById("invoiceTable").getElementsByTagName("tbody")[0];
    let newRow = table.insertRow(0);

    newRow.innerHTML = `
        <td>${date}</td>
        <td>${month}</td>
        <td>${year}</td>

        <td><a href="${filePath}" target="_blank">View Document</a></td>
    `;
}

// Fetch invoices on page load
window.onload = function() {
    fetch('/get_invoices')
        .then(response => response.json())
        .then(invoices => {
            let table = document.getElementById("invoiceTable").getElementsByTagName("tbody")[0];
            table.innerHTML = ""; // Clear table before appending new data

            invoices.forEach(invoice => {
                addInvoiceToTable(invoice.date, invoice.month, invoice.year, "N/A", invoice.file_path);
            });
        })
        .catch(error => console.error('Error fetching invoices:', error));
};
function logoutUser() {
    console.log("Logout button clicked!"); // Debugging
    fetch('/logout', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                sessionStorage.clear();
                window.location.href = "/signin"; // Redirect to sign-in page
            } else {
                alert("Logout failed! Try again.");
            }
        })
        .catch(error => {
            console.error("Logout Error:", error);
            alert("Something went wrong. Please try again.");
        });
}

// Ensure button is clickable
document.addEventListener("DOMContentLoaded", function() {
    document.querySelector(".logout-btn").addEventListener("click", logoutUser);
});

 

