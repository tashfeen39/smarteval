        document.getElementById('selectQuestions').addEventListener('change', function () {
            var selectQuestionsValue = parseInt(this.value);
            var questionDropdownsDiv = document.getElementById('questionDropdowns');
            questionDropdownsDiv.innerHTML = '';

            for (var i = 1; i <= selectQuestionsValue; i++) {
                var questionDiv = document.createElement('div');
                questionDiv.classList.add('question-container');

                var heading = document.createElement('h3');
                heading.textContent = `Question ${i}`;
                questionDiv.appendChild(heading);

                var topicInput = document.createElement('input');
                topicInput.type = 'text';
                topicInput.name = `question_${i}_topic`;
                topicInput.placeholder = 'Enter question topic';
                questionDiv.appendChild(topicInput);

                var keywordsTextarea = document.createElement('textarea');
                keywordsTextarea.name = `question_${i}_keywords`;
                keywordsTextarea.placeholder = 'Enter keywords separated by commas';
                questionDiv.appendChild(keywordsTextarea);

                var complexitySelect = document.createElement('select');
                complexitySelect.name = `question_${i}_complexity`;
                complexitySelect.classList.add('question-complexity');

                var easyOption = document.createElement('option');
                easyOption.value = 'easy';
                easyOption.textContent = 'Easy';
                complexitySelect.appendChild(easyOption);

                var moderateOption = document.createElement('option');
                moderateOption.value = 'moderate';
                moderateOption.textContent = 'Moderate';
                complexitySelect.appendChild(moderateOption);

                var complexOption = document.createElement('option');
                complexOption.value = 'complex';
                complexOption.textContent = 'Complex';
                complexitySelect.appendChild(complexOption);

                questionDiv.appendChild(complexitySelect);

                var select = document.createElement('select');
                select.name = `question_${i}_parts`;
                select.classList.add('question-parts');
                for (var j = 1; j <= 4; j++) {
                    var option = document.createElement('option');
                    option.value = j;
                    option.textContent = j;
                    select.appendChild(option);
                }
                questionDiv.appendChild(select);

                var regenerateButton = document.createElement('button');
                regenerateButton.textContent = 'Regenerate';
                regenerateButton.classList.add('regenerate-button');
                regenerateButton.addEventListener('click', (function (index) {
                    return function (event) {
                        regenerateQuestion(event, index);
                    };
                })(i));
                questionDiv.appendChild(regenerateButton);

                questionDropdownsDiv.appendChild(questionDiv);
            }
        });



        const controller = new AbortController();

        // After the user clicks the "Generate Paper" button
        document.getElementById('paperForm').addEventListener('submit', function (event) {
            event.preventDefault();

            var subjectId = document.getElementById('subject').value;
            var subjectName = document.getElementById('subject').options[document.getElementById('subject').selectedIndex].text;
            var selectQuestions = document.getElementById('selectQuestions').value;
            var data = {
                subject_id: subjectId,
                subject_name: subjectName,
                selectQuestions: selectQuestions
            };

            var questionParts = [];
            var questionTopics = [];
            var questionComplexities = [];
            var questionKeywords = [];
            var questionSelects = document.querySelectorAll('.question-container');

            if (questionSelects.length !== parseInt(selectQuestions)) {
                console.error('Inconsistent number of question containers');
                return;
            }

            questionSelects.forEach(function (questionContainer) {
                var topicInput = questionContainer.querySelector('input[type="text"]');
                var keywordsTextarea = questionContainer.querySelector('textarea');
                var complexitySelect = questionContainer.querySelector('.question-complexity');
                var partsSelect = questionContainer.querySelector('.question-parts');

                if (!topicInput.value || !keywordsTextarea.value || !complexitySelect.value || !partsSelect.value) {
                    console.error('Missing data for one or more questions');
                    return;
                }

                questionTopics.push(topicInput.value);
                questionKeywords.push(keywordsTextarea.value.split(',').map(keyword => keyword.trim()));
                questionComplexities.push(complexitySelect.value);
                questionParts.push(parseInt(partsSelect.value));
            });

            data['questionParts'] = questionParts;
            data['questionTopics'] = questionTopics;
            data['questionComplexities'] = questionComplexities;
            data['questionKeywords'] = questionKeywords;

            fetch('{% url "portals:generate_paper" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data),
                signal: controller.signal
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Response Data:', data);

                    if (data.success) {
                        var paperPromptsDiv = document.getElementById('paperPrompts');
                        paperPromptsDiv.innerHTML = '';

                        var paperContent = `<h2>Subject Name: ${data.subject_name}</h2>`;

                        data.paper_prompts.forEach((prompt, index) => {
                            paperContent += `<div class="question-prompt-container">`;
                            paperContent += `<h3><b>Question ${index + 1}:</b></h3>`;
                            paperContent += `<p>${prompt.replace(/\n/g, '<br>')}</p>`;
                            paperContent += `</div>`;
                        });

                        paperPromptsDiv.innerHTML = paperContent;
                    } else {
                        console.error('Error:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        window.addEventListener('unload', () => {
            controller.abort();
        });

        // Add this event listener to the subject dropdown
        document.getElementById('subject').addEventListener('change', function () {
            var selectedSubject = this.value;
            // Update the prompt based on the selected subject
            if (selectedSubject === 'operating_system') {
                // Update the prompt for the "Operating System" subject
                updatePrompt("The question paper is on the topic of Operating System.");
            } else {
                // Reset the prompt or handle other subjects as needed
                updatePrompt("");
            }
        });

        function updatePrompt(promptText) {
            var messageDiv = document.getElementById('message');
            messageDiv.textContent = promptText;
        }

        function regenerateQuestion(event, questionIndex) {
            event.preventDefault();
            // Get the question data for the given index
            var questionContainer = document.querySelectorAll('.question-container')[questionIndex - 1];
            var questionPromptContainer = document.querySelectorAll('.question-prompt-container')[questionIndex - 1];
            console.log('Supposed question container:', questionContainer)
            console.log('Supposed question Prompt Container:', questionPromptContainer)
            var topicInput = questionContainer.querySelector('input[type="text"]');
            var keywordsTextarea = questionContainer.querySelector('textarea');
            var complexitySelect = questionContainer.querySelector('.question-complexity');
            var partsSelect = questionContainer.querySelector('.question-parts');

            var questionData = {
                topic: topicInput.value,
                keywords: keywordsTextarea.value.split(',').map(keyword => keyword.trim()),
                complexity: complexitySelect.value,
                parts: parseInt(partsSelect.value),
                questionIndex: questionIndex
            };

            // Make an AJAX call to the backend with the updated question data and question index
            fetch('{% url "portals:regenerate_question" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(questionData),
                signal: controller.signal
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(questionData => {
                    console.log('Response Question Data:', questionData);
                    if (questionData.success) {
                        // Update the corresponding question prompt in the frontend
                        var questionPromptElement = questionPromptContainer.querySelector('p');
                        console.log('To be changed question:', questionPromptElement)
                        questionPromptElement.innerHTML = questionData.question_prompt.replace(/\n/g, '<br>');

                    } else {
                        console.error('Error:', questionData.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }