// // $(document).ready(function() {
// //     // List of Admin and Super Admin names
// //     const people = [
// //       "Admin", "Super Admin", "HR Manager", "Team Lead",
// //       "Bhushan Datey", "Supervisor", "CEO", "CTO"
// //     ];

// //     // Initialize Select2 with dynamic search
// //     $("#notify-to").select2({
// //       placeholder: "Type a name...",
// //       minimumInputLength: 1,
// //       allowClear: true,
// //       data: people.map(name => ({ id: name, text: name }))
// //     });

// //     // Handle selecting users to add as tags (like email recipients)
// //     $("#notify-to").on('select2:select', function(e) {
// //       const selectedName = e.params.data.text;
// //       addTag(selectedName);
// //     });

// //     // Add tag to the container
// //     function addTag(name) {
// //       const tag = $('<div class="tag"></div>')
// //         .text(name)
// //         .append('<button class="remove-btn">x</button>')
// //         .on('click', '.remove-btn', function() {
// //           $(this).parent().remove(); // Remove tag
// //         });
// //       $('#tags-container').append(tag);
// //       $("#notify-to").val(null).trigger('change'); // Reset select field
// //     }
// //   });

// // document.getElementById("leaveForm").addEventListener("submit", function(event) {
// //     event.preventDefault(); // Prevent the default form submission

// //     const formData = new FormData(this);

// //     const fromDate = document.getElementById("from-date").value;
// //     const toDate = document.getElementById("to-date").value;

// //     // Check if dates are present (client-side validation)
// //     if (!fromDate || !toDate) {
// //         alert("Start and end dates are required.");
// //         return; // Stop submission
// //     }

// //     // Append the dates to the FormData
// //     formData.append("from_date", fromDate);
// //     formData.append("to_date", toDate);

// //     fetch("/apply_leave", {
// //         method: "POST",
// //         body: formData
// //     })
// //     .then(response => response.json())
// //     .then(data => {
// //         if (data.message) {
// //             console.log("Success:", data.message);
// //             alert("Applied for leave successfully!"); // Show success message
// //         } else {
// //             console.error("Error Response:", data.error);
// //             alert(data.error); // Show error message
// //         }
// //     })
// //     .catch(error => {
// //       console.error("Fetch Error:", error);
// //         alert("An error occurred. Please try again later.");
// //     });
// // });

 
// $(document).ready(function() {
//     const people = [
//         "Admin", "Super Admin", "HR Manager", "Team Lead",
//         "Bhushan Datey", "Supervisor", "CEO", "CTO"
//     ];

//     $("#notify-to").select2({
//         placeholder: "Type a name...",
//         minimumInputLength: 1,
//         allowClear: true,
//         data: people.map(name => ({ id: name, text: name }))
//     });

//     // The tag handling is now ONLY for visual representation
//     $("#notify-to").on('select2:select', function(e) {
//         const selectedName = e.params.data.text;
//         addTag(selectedName);
//     });

//     function addTag(name) {
//         const tag = $('<div class="tag"></div>')
//             .text(name)
//             .append('<button class="remove-btn">x</button>')
//             .on('click', '.remove-btn', function() {
//                 $(this).parent().remove();
//                 // Important: Trigger change on Select2 to update its internal value
//                 $("#notify-to").trigger('change'); 
//             });
//         $('#tags-container').append(tag);
//         $("#notify-to").val(null).trigger('change'); // Clear Select2 input
//     }
// });

// document.getElementById("leaveForm").addEventListener("submit", function(event) {
//     event.preventDefault();

//     const formData = new FormData(this);

//     const fromDate = document.getElementById("from-date").value;
//     const toDate = document.getElementById("to-date").value;
//     const slot = document.getElementById("slot").value;
//     const reason = document.getElementById("reason").value;

//     if (!fromDate || !toDate || !slot || !reason) {
//         alert("All fields are required: Start Date, End Date, Slot, and Reason.");
//         return;
//     }

//     formData.append("from_date", fromDate);
//     formData.append("to_date", toDate);
//     formData.append("slot", slot);
//     formData.append("reason", reason);


//     const selectedNames = $("#notify-to").val(); // Get selected names from Select2
//     if (selectedNames) {
//         selectedNames.forEach(name => {
//             formData.append('notify_to', name);
//         });
//     }

//     const fileInput = document.getElementById('documents');
//     if (fileInput && fileInput.files && fileInput.files.length > 0) {
//         formData.append('document', fileInput.files[0]);
//     }

//     fetch("/apply_leave", {
//         method: "POST",
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.message) {
//             console.log("Success:", data.message);
//             alert("Leave application submitted successfully!");
//             this.reset(); // Reset the form
//             $("#notify-to").val(null).trigger('change'); // Clear Select2 selection
//             $('#tags-container').empty(); // Clear the displayed tags
//         } else {
//             console.error("Error Response:", data.error);
//             alert(data.error);
//         }
//     })
//     .catch(error => {
//         console.error("Fetch Error:", error);
//         if (error.message) {
//             alert("An error occurred: " + error.message);
//         } else {
//             alert("An error occurred. Please try again later.");
//         }
//     });
// }); 





// $(document).ready(function() {
//   $("#notify-to").select2({
//       placeholder: "Select Person",
//       allowClear: true
//   });

//   document.getElementById("leaveForm").addEventListener("submit", function(event) {
//     event.preventDefault();
//     const formData = new FormData(this);
//     console.log("FormData before sending:", [...formData.entries()]);
    
//     const slot = document.getElementById("slot").value;
//     console.log("Selected Slot:", slot);  // Debugging: Check sent value
    
//     const reason = document.getElementById("reason").value;
//     console.log("Reason entered:", reason);
//     // Proceed with form submission
// });


//   $("#leaveForm").on("submit", function(event) {
//       event.preventDefault();

//       let formData = new FormData(this);

//       fetch("/apply_leave", {
//           method: "POST",
//           body: formData
//       })
//       .then(response => response.json())
//       .then(data => {
//           if (data.message) {
//               console.log("Success:", data.message);
//               alert("Leave application submitted successfully!");
//               this.reset();
//               $("#notify-to").val(null).trigger('change');
//               showPopup(data.message);
//           } else {
//               console.error("Error:", data.error);
//               alert(data.error);
//           }
//       })
//       .catch(error => {
//           console.error("Fetch Error:", error);
//           alert("An error occurred. Please try again.");
//       });
//   });
// });
// loadLeaveApplications();
// function showPopup(message) {
//     $("#popup").text(message).fadeIn();
//     setTimeout(function() {
//         $("#popup").fadeOut();
//     }, 3000);
// }

// $("#leave-form").on("submit", function(event) {
//     event.preventDefault();
   
//     const slot = $("#slot").val();
//     const fromDate = $("#from-date").val();
//     const toDate = $("#to-date").val();
//     const reason = $("#reason").val();
//     const attachment = $("#documents").val() ? "Yes" : "No";
//     // const notifiedTo = $("#tags-container .tag").map(function() {
//     //     return $(this).text().replace("x", "").trim();
//     // }).get().join(", ");

//     const selectedNotifiedTo = $("#notify-to").val();
//     const notifiedTo = (selectedNotifiedTo && selectedNotifiedTo.length) 
//                           ? selectedNotifiedTo.join(", ") 
//                           : "None";
   
//     if (!slot || !fromDate || !toDate || !reason) {
//         alert("Please fill all required fields.");
//         return;
//     }
   
//     const newRow = `<tr>
//         <td>${slot}</td>
//         <td>${fromDate}</td>
//         <td>${toDate}</td>
//         <td>${notifiedTo}</td>
//         <td>${reason}</td>
//         <td>${attachment}</td>
//         <td class="status">false</td>
//         <!-- <td>
//             <button class="approve-btn">Approve</button>
//             <button class="reject-btn">Reject</button>
//         </td> -->
//     </tr>`;
   
//     $("#leave-table-body").append(newRow);
//     $("#leave-form")[0].reset();
//     $("#tags-container").empty();
// });

// function loadLeaveApplications() {
//     fetch("/get_leave_applications")
//     .then(response => response.json())
//     .then(data => {
//         if (data.leave_applications) {
//             $("#leave-table-body").empty(); // Clear current table data

//             data.leave_applications.forEach(app => {
//                 let row = `<tr>
//                     <td>${app.slot}</td>
//                     <td>${app.start_date}</td>
//                     <td>${app.end_date}</td>
//                     <td>${app.apply_to}</td>
//                     <td>${app.reason}</td>
//                     <td>${app.document_path ? "Yes" : "No"}</td>
//                     <td>${app.status}</td>
//                 </tr>`;
//                 $("#leave-table-body").append(row);
//             });
//         }
//     })
//     .catch(error => {
//         console.error("Error fetching leave applications:", error);
//     });
// }


$(document).ready(function() {
    // Initialize Select2 on the multi-select field
    $("#notify-to").select2({
        placeholder: "Select Person",
        allowClear: true
    });
    loadLeaveApplications();
    // Handle leave application form submission
    $("#leave-form").on("submit", function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        
        fetch("/apply_leave", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                // Append the new leave application to the table
                var app = data.leave_application;
                var newRow = `<tr>
                    <td>${app.slot}</td>
                    <td>${app.start_date}</td>
                    <td>${app.end_date}</td>
                    <td>${app.apply_to}</td>
                    <td>${app.reason}</td>
                    <td>${app.document_path ? "Yes" : "No"}</td>
                    <td>${app.status}</td>
                </tr>`;
                loadLeaveApplications();
                $("#leave-table-body").prepend(newRow);
                $("#leave-form")[0].reset();
                $("#notify-to").val(null).trigger('change');
                showPopup(data.message);
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error("Fetch Error:", error);
            alert("An error occurred. Please try again.");
        });
    });
    
    // Load existing leave applications on page load
    // loadLeaveApplications();
});

function showPopup(message) {
    $("#popup").text(message).fadeIn();
    setTimeout(function() {
        $("#popup").fadeOut();
    }, 3000);
}

function loadLeaveApplications() {
    fetch("/get_leave_applications")
    .then(response => response.json())
    .then(data => {
        if (data.leave_applications) {
            $("#leave-table-body").empty();
            data.leave_applications.forEach(app => {
                var row = `<tr>
                    <td>${app.slot}</td>
                    <td>${app.start_date}</td>
                    <td>${app.end_date}</td>
                    <td>${app.apply_to}</td>
                    <td>${app.reason}</td>
                    <td>${app.document_path ? "Yes" : "No"}</td>
                    <td>${app.status}</td>
                </tr>`;
                $("#leave-table-body").append(row);
            });
        }
    })
    .catch(error => {
        console.error("Error fetching leave applications:", error);
    });
}
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