let paperContent = "";
document
  .getElementById("selectQuestions")
  .addEventListener("change", function () {
    var selectQuestionsValue = parseInt(this.value);
    var questionDropdownsDiv = document.getElementById("questionDropdowns");
    questionDropdownsDiv.innerHTML = "";

    for (var i = 1; i <= selectQuestionsValue; i++) {
      var questionDiv = document.createElement("div");
      questionDiv.classList.add("question-div");

      var heading = document.createElement("h3");
      heading.textContent = `Question ${i}`;
      questionDiv.appendChild(heading);

      var topicInput = document.createElement("input");
      topicInput.type = "text";
      topicInput.name = `question_${i}_topic`;
      topicInput.placeholder = "Enter question topic";
      topicInput.classList.add("form-control", "mb-3"); // Add Bootstrap classes
      topicInput.style.borderRadius = "5px"; // Add custom styles
      topicInput.style.padding = "10px";
      topicInput.style.fontSize = "16px";
      questionDiv.appendChild(topicInput);

      var keywordsTextarea = document.createElement("textarea");
      keywordsTextarea.name = `question_${i}_keywords`;
      keywordsTextarea.placeholder = "Enter instructions";
      keywordsTextarea.classList.add("form-control", "mb-3", "custom-textarea"); // Add custom class
      keywordsTextarea.style.borderRadius = "5px"; // Add custom styles
      keywordsTextarea.style.padding = "10px";
      keywordsTextarea.style.fontSize = "16px";
      keywordsTextarea.style.resize = "vertical"; // Allow vertical resizing
      questionDiv.appendChild(keywordsTextarea);

      // -------------------- BT LEVEL -------------------

      // BT Level Heading
      var btHeading = document.createElement("h5");
      btHeading.textContent = "BT Level";
      questionDiv.appendChild(btHeading);

      // Create a new select element for BT levels
      var btSelect = document.createElement("select");
      btSelect.name = `question_${i}_bt_level`;
      btSelect.classList.add("form-select", "mb-3", "question-bt-level");

      // Add an option for "N/A"
      var notApplicable = document.createElement("option");
      notApplicable.value = "n/a";
      notApplicable.textContent = "N/A";
      btSelect.appendChild(notApplicable);

      // Add options for Bloom's Taxonomy levels
      var levels = [
        "Remember",
        "Understand",
        "Apply",
        "Analyze",
        "Evaluate",
        "Create",
      ];
      levels.forEach(function (level) {
        var option = document.createElement("option");
        option.value = level.toLowerCase();
        option.textContent = level;
        btSelect.appendChild(option);
      });

      // Append the BT level select to the question div
      questionDiv.appendChild(btSelect);

      // ---------------- BT LEVEL END -------------------

      // Complexity Level Heading
      var heading = document.createElement("h5");
      heading.textContent = `Complexity Level`;
      questionDiv.appendChild(heading);

      var complexitySelect = document.createElement("select");
      complexitySelect.name = `question_${i}_complexity`;
      complexitySelect.classList.add(
        "form-select",
        "mb-3",
        "question-complexity"
      );

      var notApplicable = document.createElement("option");
      notApplicable.value = "n/a";
      notApplicable.textContent = "N/A";
      complexitySelect.appendChild(notApplicable);

      var easyOption = document.createElement("option");
      easyOption.value = "easy";
      easyOption.textContent = "Easy";
      complexitySelect.appendChild(easyOption);

      var moderateOption = document.createElement("option");
      moderateOption.value = "moderate";
      moderateOption.textContent = "Moderate";
      complexitySelect.appendChild(moderateOption);

      var complexOption = document.createElement("option");
      complexOption.value = "complex";
      complexOption.textContent = "Complex";
      complexitySelect.appendChild(complexOption);

      questionDiv.appendChild(complexitySelect);

      // Number of Parts Heading
      var heading = document.createElement("h5");
      heading.textContent = `Number of Parts`;
      questionDiv.appendChild(heading);

      var select = document.createElement("select");
      select.name = `question_${i}_parts`;
      select.classList.add("form-select", "mb-3", "question-parts");

      var notApplicable = document.createElement("option");
      notApplicable.value = "n/a";
      notApplicable.textContent = "N/A";
      select.appendChild(notApplicable);

      for (var j = 1; j <= 4; j++) {
        var option = document.createElement("option");
        option.value = j;
        option.textContent = j;
        select.appendChild(option);
      }
      questionDiv.appendChild(select);

      var regenerateButton = document.createElement("button");
      regenerateButton.textContent = "Regenerate";
      regenerateButton.classList.add(
        "btn",
        "btn-primary",
        "mb-3",
        "regenerate-button"
      );
      regenerateButton.addEventListener(
        "click",
        (function (index) {
          return function (event) {
            regenerateQuestion(event, index, data);
          };
        })(i)
      );
      questionDiv.appendChild(regenerateButton);

      questionDropdownsDiv.appendChild(questionDiv);
    }
    // Disable all regenerate buttons initially
    var regenerateButtons = document.querySelectorAll(".regenerate-button");
    regenerateButtons.forEach(function (button) {
      button.disabled = true;
    });
  });

// Function to enable regenerate buttons after paper generation
function enableRegenerateButtons() {
  var regenerateButtons = document.querySelectorAll(".regenerate-button");
  regenerateButtons.forEach(function (button) {
    button.disabled = false;
  });
}

const controller = new AbortController();

// After the user clicks the "Generate Paper" button
document
  .getElementById("paperForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    var subjectId = document.getElementById("subject").value;
    var subjectName =
      document.getElementById("subject").options[
        document.getElementById("subject").selectedIndex
      ].text;
    var selectQuestions = document.getElementById("selectQuestions").value;

    // Prepare data to send to the backend
    var data = {
      subject_id: subjectId,
      selectQuestions: selectQuestions,
      questionParts: Array.from(
        document.querySelectorAll(".question-parts")
      ).map((el) => el.value),
      questionTopics: Array.from(
        document.querySelectorAll('input[name*="question_"]')
      ).map((el) => el.value),
      questionBTLevels: Array.from(
        document.querySelectorAll(".question-bt-level")
      ).map((el) => el.value),
      questionComplexities: Array.from(
        document.querySelectorAll(".question-complexity")
      ).map((el) => el.value),
      questionKeywords: Array.from(
        document.querySelectorAll('textarea[name*="question_"]')
      ).map((el) => el.value.split(",").map((kw) => kw.trim())),
    };

    fetch(generatePaperUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        var paperPromptsDiv = document.getElementById("paperPrompts");
        paperPromptsDiv.innerHTML = `<h2>Subject Name: ${data.subject_name}</h2>`;

        data.paper_prompts.forEach((prompt, index) => {
          paperPromptsDiv.innerHTML += `<div class="question-prompt-container">
                <h3><b>Question ${index + 1}:</b></h3>
                <p>${prompt.replace(/\n/g, "<br>")}</p>
            </div>`;
        });

        enableRegenerateButtons();
        createDownloadButton(paperPromptsDiv.innerHTML);
      })
      .catch((error) => console.error("Error:", error));
  });


window.addEventListener("unload", () => {
  controller.abort();
});

document.getElementById("subject").addEventListener("change", function () {
  var selectedSubject = this.value;
  // Update the prompt based on the selected subject
  if (selectedSubject === "operating_system") {
    // Update the prompt for the "Operating System" subject
    updatePrompt("The question paper is on the topic of Operating System.");
  } else if (selectedSubject === "data_structures") {
    // Update the prompt for the "Data Structures" subject
    updatePrompt("The question paper is on the topic of Data Structures.");
  } else if (selectedSubject === "algorithms") {
    // Update the prompt for the "Algorithms" subject
    updatePrompt("The question paper is on the topic of Algorithms.");
  } else {
    // Reset the prompt or handle other subjects as needed
    updatePrompt("");
  }
});

function updatePrompt(promptText) {
  var messageDiv = document.getElementById("message");
  messageDiv.textContent = promptText;
}

function regenerateQuestion(event, questionIndex) {
  event.preventDefault();

  // Find the specific question div by the provided index
  var questionContainer =
    document.querySelectorAll(".question-div")[questionIndex - 1];
  var topicInput = questionContainer.querySelector('input[type="text"]');
  var keywordsTextarea = questionContainer.querySelector("textarea");
  var complexitySelect = questionContainer.querySelector(
    ".question-complexity"
  );
  var partsSelect = questionContainer.querySelector(".question-parts");
  var btSelect = questionContainer.querySelector(".question-bt-level");

  // Gather the data for the selected question
  var questionData = {
    topic: topicInput.value,
    keywords: keywordsTextarea.value
      .split(",")
      .map((keyword) => keyword.trim()),
    complexity: complexitySelect.value,
    parts: parseInt(partsSelect.value),
    questionIndex: questionIndex,
    bt_level: btSelect.value, // Include the selected BT level
  };

  fetch(regenerateQuestionUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
    body: JSON.stringify(questionData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.json();
    })
    .then((questionData) => {
      if (questionData.success) {
        // Update the specific question prompt with the new generated prompt
        var questionPromptContainer = document.querySelectorAll(
          ".question-prompt-container"
        )[questionIndex - 1];
        var questionPromptElement = questionPromptContainer.querySelector("p");

        if (questionPromptElement) {
          questionPromptElement.innerHTML =
            questionData.question_prompt.replace(/\n/g, "<br>");
        } else {
          var newPromptElement = document.createElement("p");
          newPromptElement.innerHTML = questionData.question_prompt.replace(
            /\n/g,
            "<br>"
          );
          questionPromptContainer.appendChild(newPromptElement);
        }

        console.log(
          `Updated Question ${questionIndex}:`,
          questionData.question_prompt
        );
      } else {
        console.error("Error:", questionData.error);
      }
    })
    .catch((error) => console.error("Error:", error));
}

// Example of attaching the regenerate function to the regenerate button
document.querySelectorAll(".regenerate-button").forEach((button, index) => {
  button.addEventListener("click", function (event) {
    regenerateQuestion(event, index + 1);
  });
});


$(function () {
  // Initialize Select2 for the subject dropdown
  $("#subject").select2({
    theme: "bootstrap-5",
    width: $(this).data("width")
      ? $(this).data("width")
      : $(this).hasClass("w-100")
      ? "100%"
      : "style",
    placeholder: $(this).data("placeholder"),
  });
});

// Download Button
function createDownloadButton(paperContent) {
  const downloadContainer = document.getElementById("downloadContainer");

  // Remove any existing download button
  const existingButton = downloadContainer.querySelector("button");
  if (existingButton) {
    existingButton.remove();
  }

  const downloadButton = document.createElement("button");
  downloadButton.textContent = "Download Paper";
  downloadButton.classList.add("btn", "btn-primary");
  downloadButton.addEventListener("click", () => {
    const cleanedContent = paperContent.replace(/<\/?[^>]+(>|$)/g, ""); // Remove HTML tags
    const formattedContent = cleanedContent.replace(/\n/g, "\r\n"); // Replace line breaks with Windows-style line breaks

    const blob = new Blob([formattedContent], { type: "application/msword" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "generated_paper.doc";
    a.click();
    window.URL.revokeObjectURL(url);
  });

  downloadContainer.appendChild(downloadButton);
}
