function submitFeedback() {
  var name = document.getElementById("name").value;
  var feedbackSubject = document.getElementById("feedbackSubject").value;
  var message = document.getElementById("message").value;

  // You can add code here to send the feedback data to a server for processing
  // For this example, we'll just display the feedback in an alert
  var feedback =
    "Name: " +
    name +
    "\nFeedback Subject: " +
    feedbackSubject +
    "\nMessage:\n" +
    message;
  alert("Feedback Submitted:\n" + feedback);

  // Clear the form fields after submission
  document.getElementById("feedbackForm").reset();
}
