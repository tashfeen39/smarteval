// admin_degree_form.js
console.log("JavaScript file loaded successfully.");

document.addEventListener("DOMContentLoaded", function () {
  const departmentSelect = document.getElementById("id_department");
  const programSelect = document.getElementById("id_program");

  departmentSelect.addEventListener("change", function () {
    const departmentId = departmentSelect.value;

    // Make an AJAX request to fetch programs for the selected department
    fetch(`/get_programs/?department_id=${departmentId}`)
      .then((response) => response.json())
      .then((data) => {
        // Clear existing options
        programSelect.innerHTML = "";

        // Add new options based on the response
        data.forEach((program) => {
          const option = document.createElement("option");
          option.value = program.id;
          option.text = program.name;
          programSelect.appendChild(option);
        });
      })
      .catch((error) => {
        console.error("Error fetching programs:", error);
      });
  });
});
