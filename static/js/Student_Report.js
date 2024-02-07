// JavaScript function to handle the selection change
function handleNextView(selectElement) {
  var selectedOption = selectElement.value;

  // Hide all content sections
  var contentSections = document.getElementsByClassName("content-section");
  for (var i = 0; i < contentSections.length; i++) {
    contentSections[i].style.display = "none";
  }

  // Show the selected content section
  var selectedContent = document.getElementById(selectedOption + "Content");
  if (selectedContent) {
    selectedContent.style.display = "block";
  }
}

// Attach the onchange event to the select element
document.getElementById("classSelect").addEventListener("change", function () {
  handleNextView(this);
});
