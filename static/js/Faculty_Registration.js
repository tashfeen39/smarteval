document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form.needs-validation");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirm_password");
  const errorElement = document.getElementById("password-error");
  const profilePictureInput = document.getElementById("profile_picture");
  const profilePicturePreview = document.getElementById(
    "profile_picture_preview"
  );

  form.addEventListener("submit", function (event) {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    } else {
      // Clear the custom validity on successful submission
      confirmPasswordInput.setCustomValidity("");
    }

    form.classList.add("was-validated");
  });

  function validatePassword() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (password === confirmPassword) {
      errorElement.textContent = "";
      confirmPasswordInput.setCustomValidity("");
    } else {
      errorElement.textContent = "Passwords do not match";
      confirmPasswordInput.setCustomValidity("Passwords do not match");
    }
  }

  confirmPasswordInput.addEventListener("focus", function () {
    confirmPasswordInput.addEventListener("input", validatePassword);
    passwordInput.addEventListener("input", validatePassword);
  });

  profilePictureInput.addEventListener("change", function () {
    const file = profilePictureInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        profilePicturePreview.setAttribute("src", e.target.result);
      };
      reader.readAsDataURL(file);
    } else {
      profilePicturePreview.removeAttribute("src");
    }
  });
  // Display error message for username, email, and phone number fields
  // const errorMessageElements = document.querySelectorAll(".error-message");
  // errorMessageElements.forEach(function (element) {
  //   element.classList.add("invalid-feedback");
  // });
});
