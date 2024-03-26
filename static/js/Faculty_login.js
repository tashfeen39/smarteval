document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form.needs-validation");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const usernameFeedback = document.querySelector(
    "#username + .invalid-feedback"
  );
  const passwordFeedback = document.querySelector(
    "#password + .invalid-feedback"
  );

  form.addEventListener("submit", function (event) {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }

    form.classList.add("was-validated");

    if (usernameInput.value.trim() === "") {
      event.preventDefault();
      usernameInput.classList.add("is-invalid");
      usernameFeedback.textContent = "Please enter your Username.";
      usernameFeedback.style.display = "block"; // Show error message
    } else {
      usernameInput.classList.remove("is-invalid");
      usernameFeedback.textContent = "";
      usernameFeedback.style.display = "none"; // Hide error message
    }

    if (passwordInput.value.trim() === "") {
      event.preventDefault();
      passwordInput.classList.add("is-invalid");
      passwordFeedback.textContent = "Please enter a password.";
      passwordFeedback.style.display = "block"; // Show error message
    } else {
      passwordInput.classList.remove("is-invalid");
      passwordFeedback.textContent = "";
      passwordFeedback.style.display = "none"; // Hide error message
    }
  });

  // Reset validation state on input
  usernameInput.addEventListener("input", function () {
    usernameInput.classList.remove("is-invalid");
    usernameFeedback.textContent = "";
    usernameFeedback.style.display = "none"; // Hide error message
  });

  passwordInput.addEventListener("input", function () {
    passwordInput.classList.remove("is-invalid");
    passwordFeedback.textContent = "";
    passwordFeedback.style.display = "none"; // Hide error message
  });
});
